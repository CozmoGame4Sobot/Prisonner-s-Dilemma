import asyncio
import copy
import cozmo
import time
from cozmo.util import degrees, distance_mm
import threading

from constants import (
                        START_CUBE,
                        TAP_CUBE,
                        COOP_CUBE,
                        DEFECT_CUBE,
                        RED_LIGHT,
                        GREEN_LIGHT,
                        SEA_LIGHT,
                        YELLOW_LIGHT,
                        BLUE_LIGHT,
                        
                        #Score conditions
                        P_R,
                        P_O,
                        O_R,
                        O_O,
                        X_X,
                        
                        
                        COZMO_DEFECT,
                        COZMO_COOP,
                        PLAYER_DEFECT,
                        PLAYER_COOP)

from random import randint

thread_lock = threading.Condition()

class SpeedTapEngine:
    
    
    
    MAX_INDEX = 5
                               
    def __init__(self, game_robot):
        self.robot = game_robot
        self.robot_cube = None
        self.player_coop_cube = None
        self.player_defect_cube = None
        self.deal_hand_no = 0
        self.tap_registry = []
        self.result_track = []
        self.robot_score = 0
        self.player_score = 0
        self.score_plan = None
        
    
        
    def reset_deals(self):
        
        self.deal_hand_no = 0
        self.tap_registry = []
        self.result_track = []
        self.robot_score = 0
        self.player_score = 0
        
        
        
    def cozmo_setup_game(self, score_plan):
        light_cube_list = [cozmo.objects.LightCube1Id, cozmo.objects.LightCube2Id ,cozmo.objects.LightCube3Id ]
        self.score_plan = score_plan
        
        try:
            self.robot.set_head_angle(degrees(0)).wait_for_completed()
            self.robot.move_lift(-3)
            cube = self.robot.world.wait_for_observed_light_cube(timeout=60)
        except asyncio.TimeoutError:
            print("Didn't find a cube :-(")
            return
        # cozmo taps to select cube
        try:
            cube.start_light_chaser(START_CUBE)
            self.robot.move_lift(3)
            self.robot.go_to_object(cube, distance_mm(35.0)).wait_for_completed()
            ############################
            #needs refining
            self.robot.move_lift(-2)
            time.sleep(.20)
            self.robot.move_lift(2)
            time.sleep(.20)
            tapped_event = self.robot.world.wait_for(cozmo.objects.EvtObjectTapped,timeout=0.1)
            ##############################
        except asyncio.TimeoutError:
            pass
        finally:
            cube.stop_light_chaser()
            cube.set_lights_off()
            cube.set_lights(cozmo.lights.green_light)
        
        self.robot_cube = cube
        
        # Now player has to select their cube
        other_cube_list = []
        other_idx = 0
        for lightcube_id in light_cube_list:
            other_cube = self.robot.world.light_cubes.get(lightcube_id)
            if other_cube.object_id == self.robot_cube.object_id:
                # the robot's cube should not be lit
                continue
            if other_idx == 0:
                other_cube.start_light_chaser(COOP_CUBE)
                self.player_coop_cube = other_cube
                other_idx += 1
            else:
                other_cube.start_light_chaser(DEFECT_CUBE)
                self.player_defect_cube = other_cube
            other_cube_list.append(other_cube)
        
        try:
            while len(other_cube_list) > 0:
                tapped_event = self.robot.world.wait_for(cozmo.objects.EvtObjectTapped,timeout=120)
                if tapped_event:
                    player_cube = tapped_event.obj
                    if player_cube.object_id == self.robot_cube.object_id:
                        print("Cannot take Cozmo's cube!!!")
                    elif player_cube not in other_cube_list:
                        continue
                    else:
                        player_cube.stop_light_chaser()
                        player_cube.set_lights_off()
                        other_cube_list.remove(player_cube)
                #print("Player selected Cube: %d" % self.player_cube.object_id)
        except asyncio.TimeoutError:
            print("No-one tapped our cube :-(")
        finally:
            self.robot_cube.set_lights_off()
            for other_cube in other_cube_list:
                other_cube.stop_light_chaser()
                other_cube.set_lights_off()
        
        
        return self.robot_cube, self.player_coop_cube, self.player_defect_cube
    
    def deal_hand(self):
        
        for i in range(0,3):
            self.player_coop_cube.start_hand(GREEN_LIGHT)
            self.player_defect_cube.start_hand(GREEN_LIGHT)
            self.robot_cube.start_hand(GREEN_LIGHT)
            time.sleep(0.5)
            self.player_coop_cube.set_lights_off()
            self.player_defect_cube.set_lights_off()
            self.robot_cube.set_lights_off()
            time.sleep(0.5)
        self.player_coop_cube.start_hand(YELLOW_LIGHT)
        self.player_defect_cube.start_hand(BLUE_LIGHT)
        self.robot_cube.start_hand(RED_LIGHT)
        self.tap_registry.append([])
        

    
    def register_tap(self, tap_type):
        tap_registered = False
        register_for = None          
        
        # lock tap_registry to prevent overwriting
        try:
            thread_lock.acquire()
            self.tap_registry[self.deal_hand_no].append(tap_type) 
            tap_registered = True    
        except IndexError:
            # Tap registered outside active life
            pass
        finally:
            thread_lock.notify_all()
            thread_lock.release()
        if tap_registered:
            if tap_type == PLAYER_DEFECT:
                # Once player tap is registered both player cubes blink
                # Out of action
                cozmo.logger.info("PD : Player tap registered grab")
                self.player_coop_cube.start_light_chaser(DEFECT_CUBE)
                self.player_defect_cube.start_light_chaser(DEFECT_CUBE)
                #self.player_coop_cube.start_light_chaser(TAP_CUBE)
                #self.player_defect_cube.start_light_chaser(TAP_CUBE)
            elif tap_type == PLAYER_COOP:
                # Once player tap is registered both player cubes blink
                # Out of action
                cozmo.logger.info("PD : Player tap registered share")
                self.player_coop_cube.start_light_chaser(COOP_CUBE)
                self.player_defect_cube.start_light_chaser(COOP_CUBE)
                #self.player_coop_cube.start_light_chaser(TAP_CUBE)
                #self.player_defect_cube.start_light_chaser(TAP_CUBE)
            elif tap_type == COZMO_DEFECT:
                # Cozmo cube out of action
                cozmo.logger.info("PD : Cozmo tap registered grab")
                self.robot_cube.start_light_chaser(TAP_CUBE)
            elif tap_type == COZMO_COOP:
                # Cozmo cube out of action
                cozmo.logger.info("PD : Cozmo tap registered share")
                self.robot_cube.start_light_chaser(TAP_CUBE)
        return tap_registered
    
    
    def deactivate_current_deal(self):
        try:
            self.player_coop_cube.stop_light_chaser()
            self.player_defect_cube.stop_light_chaser()
            self.robot_cube.stop_light_chaser()
            self.player_coop_cube.set_lights_off()
            self.player_defect_cube.set_lights_off()
            self.robot_cube.set_lights_off()
            
            deal_no = self.deal_hand_no
            self.deal_hand_no += 1
            
            # Only tapped cubes will show red light chase
            # for 2 seconds
            if PLAYER_COOP in self.tap_registry[deal_no]:
                self.player_coop_cube.start_light_chaser(COOP_CUBE)
                self.player_defect_cube.start_light_chaser(COOP_CUBE)
            elif PLAYER_DEFECT in self.tap_registry[deal_no]:
                self.player_coop_cube.start_light_chaser(DEFECT_CUBE)
                self.player_defect_cube.start_light_chaser(DEFECT_CUBE)
                
            
            if COZMO_COOP in self.tap_registry[deal_no]:
                self.robot_cube.start_light_chaser(COOP_CUBE)
            else:
                self.robot_cube.start_light_chaser(DEFECT_CUBE)                
            time.sleep(2)
            # Switch to blue score light
            #self.player_cube.start_hand(SEA_LIGHT)
            #self.robot_cube.start_hand(SEA_LIGHT)
        except IndexError:
            # current deal is already inactive
            pass
 
        
    def score_last_deal(self):
        deal_no = self.deal_hand_no - 1
        if PLAYER_DEFECT in self.tap_registry[deal_no]:
            if COZMO_DEFECT in self.tap_registry[deal_no]:
                self.result_track.append(P_R)
                self.robot_score += self.score_plan[P_R][1]
                self.player_score += self.score_plan[P_R][0]
            else:
                self.result_track.append(P_O)
                self.robot_score += self.score_plan[P_O][1]
                self.player_score += self.score_plan[P_O][0]
        elif PLAYER_COOP in self.tap_registry[deal_no]:
            if COZMO_DEFECT in self.tap_registry[deal_no]:
                self.result_track.append(O_R)
                self.robot_score += self.score_plan[O_R][1]
                self.player_score += self.score_plan[O_R][0]
            else:
                self.result_track.append(O_O)
                self.robot_score += self.score_plan[O_O][1]
                self.player_score += self.score_plan[O_O][0]
        else:
            self.result_track.append(X_X)
            cozmo.logger.info("PD : Missing data at deal %d" % self.deal_hand_no)
            
        
        # Update screen on score
        
                


# A thread-safe implementation of Singleton pattern
# To be used as mixin or base class
class GoalStatements(object):
    
    # use special name mangling for private class-level lock
    # we don't want a global lock for all the classes that use Singleton
    # each class should have its own lock to reduce locking contention
    __lock = threading.Lock()
    
    # private class instance may not necessarily need name-mangling
    __instance = None
    
    
    @classmethod
    def instance(cls, *args):
        if not cls.__instance:
            with cls.__lock:
                if not cls.__instance:
                    cls.__instance = cls(*args)
                    
        return cls.__instance
    
    def __init__(self, score_plan):
        self.statements = ["Goal : Try to get %s points in this game" % score_plan[0][0],
                            "Goal : Try to get %s points in this game" % score_plan[1][0],
                            "Goal : Try to get %s points in this game" % score_plan[2][0],
                            "Goal : Try to get %s points in this game" % score_plan[3][0],
                            "Ready for next one? Remember to tap on time!"]  
