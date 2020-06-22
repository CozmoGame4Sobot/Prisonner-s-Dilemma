import asyncio
import copy
import cozmo
import time
from cozmo.util import degrees, distance_mm, Pose
from datetime import datetime

from asyncio.locks import Lock
from constants import ( PLAYER_ID,
                        COZMO_ID,
                        
                        P_R,
                        P_O,
                        O_R,
                        O_O,
                        X_X,
                        
                        COZMO_DEFECT,
                        COZMO_COOP,
                        COZMO_CHOICE,
                        
                        RESULT_STATEMENT)

from game_engine import SpeedTapEngine, GoalStatements
from human_player import Human_Listener
from game_cubes import BlinkyCube
from random import randint, shuffle
from screen import Screen
from idlelib.PyShell import fix_x11_paste
from turtledemo import planet_and_moon

cozmo.world.World.light_cube_factory = BlinkyCube

class CozmoPlayerActions(object):
    """
    A singleton class defining how cozmo will act
    """
    
    __instance = None
    
    def __new__(cls):
      if not CozmoPlayerActions.__instance:
          CozmoPlayerActions.__instance = object.__new__(cls)
          #CozmoPlayerActions.__instance.sad_not_angry = True
          #CozmoPlayerActions.__instance.reaction_time = 1
          CozmoPlayerActions.__instance.rounds_to_play = 20
          CozmoPlayerActions.__instance.practice = False
          CozmoPlayerActions.__instance.singleScreen = False
      return  CozmoPlayerActions.__instance
    
        
    def set_practice(self, practice):
        self.practice = practice
        if practice:
            self.rounds_to_play = 16
    
    def set_singleScreen(self):
        self.singleScreen = True
    
    def setup_ScorePlan(self, score_plan):
        self.score_plan = score_plan
        self.goals_statment_list = GoalStatements(score_plan).statements
        
    def set_game_lose_reaction(self, is_sad):
        self.sad_not_angry = is_sad
                
    
    def cozmo_tap_decision(self, game_robot, speed_tap_game, goal=None):
        """
        This module decides whether cozmo should tap or not
        @param game_robot: The cozmo robot handle
        @param speed_tap_game: The game engine that needs to register the tap
        @param goal: If this is a practice round then cozmo taps if the goal requires it to tap 
        """
        if not self.practice:
            tap_decision = goal in [P_R, O_R ]#randint(0, 10) in [0, 4, 8, 5, 10]
            
        else:
            tap_decision = goal in [P_R, O_R]
        time.sleep(1.5)
        game_robot.move_lift(-3)
        time.sleep(.1)
        game_robot.move_lift(4)
        time.sleep(.1)
        game_robot.play_anim('anim_speedtap_tap_02')#.wait_for_completed()
        if tap_decision:
            cozmo.logger.info("PD : Cozmo tapped grab")
            cozmo_tapped = speed_tap_game.register_tap(tap_type=COZMO_DEFECT)
        else:
            cozmo.logger.info("PD : Cozmo tapped share")
            cozmo_tapped = speed_tap_game.register_tap(tap_type=COZMO_COOP)
        time.sleep(0.5)
        return True
    
    def select_wait(self):
        wait_anims = ['anim_speedtap_wait_short',
          'anim_speedtap_wait_medium',
          'anim_speedtap_wait_medium_02',
          'anim_speedtap_wait_medium_03',
          'anim_speedtap_wait_long'
          ]
        selected = randint(0,4)
        return wait_anims[selected]
    
    def act_out(self, game_robot, act_type):
        selected_anim = None
        if act_type == "stand_back":
            game_robot.drive_wheels(-100, -100, duration=1.5)
            time.sleep(1.5)
            game_robot.move_lift(-3)
            time.sleep(0.2)
        elif act_type == "check_score":
            game_robot.drive_wheels(100, -100, duration=1)
            game_robot.set_head_angle(degrees(10)).wait_for_completed()
            if self.practice:
                time.sleep(2)
            else:
                time.sleep(0.5)
            game_robot.drive_wheels(-100, 100, duration=1)
            game_robot.set_head_angle(degrees(0)).wait_for_completed()
            time.sleep(0.5)
        
        else:
            selected_anim = self.select_wait()
           
        
        if selected_anim:
            game_robot.play_anim(selected_anim).wait_for_completed()
            
            
            
def log_deal_plan(plan):
    cozmo.logger.info("PD : %s" % list(map(lambda x: 'Share' if x==1 else 'Grab' if x==0 else 'Missing', plan)))

def cozmo_tap_game(robot: cozmo.robot.Robot):
    
    # Initialize all the game engines screens and listners
    speed_tap_game = SpeedTapEngine(robot)
    robot_game_action = CozmoPlayerActions()
    display_screen = Screen()
    display_screen.setup(robot_game_action.score_plan,
                         singleScreen=robot_game_action.singleScreen)
    game_screen = display_screen.gameScreen
    #display_screen.start()
    display_screen.root.mainloop(1)
    game_screen.show_play_screen(0, 0)
    
    time.sleep(0.25)        # sleep to give the cozmo cube to stop flashing
    robot_cube, player_coop_cube, player_defect_cube = speed_tap_game.cozmo_setup_game(robot_game_action.score_plan)
    
    if robot_cube in [player_coop_cube, player_defect_cube]:
        print("Participant cannot play on the same cube as cozmo")
        game_screen.master.destroy() 
        exit(0)
    monitor_player_tap = Human_Listener(robot, player_coop_cube, player_defect_cube, speed_tap_game)
    
    # initialise variables
    
    
    correctChoice = -1                  # Correct choice is for practice round
    track_correct_practice = 0
    game_complete = False
    winner = 0
    score_to = 5 
    pass_criteria = 8                   # Only applies for practice rounds
    
    goal_statement = ""
    preset_goals = [P_R,
                    P_O,
                    O_R,
                    O_O]    
    cozmo_fixture =  COZMO_CHOICE[randint(0, 2)]
    # Now all decided so lets suffle it up
    shuffle(cozmo_fixture)
    
    monitor_player_tap.game_on = True
    monitor_player_tap.start()
    deal_count = 1
    
    if robot_game_action.practice:
        cozmo.logger.info("PD : Playing practice round")
    else:
        cozmo.logger.info("PD : Playing experiment round")
        cozmo.logger.info("PD : Cozmo initial plan fixture")
        log_deal_plan(cozmo_fixture)
        
    cozmo.logger.info("PD : Score set: %s" % robot_game_action.score_plan)
        
    try:
        while deal_count <= robot_game_action.rounds_to_play :
            #print("%s" % cozmo_fixture)
            cozmo.logger.info("PD : Deal started")
            if robot_game_action.practice:
                if track_correct_practice%4 == 0:
                    shuffle(preset_goals)
                    #cozmo.logger.info("PD : Preset Goals :%s" % preset_goals)
                correctChoice = preset_goals[(track_correct_practice-1)%4]
                cozmo.logger.info("PD : Practice Goal : %s" % robot_game_action.goals_statment_list[correctChoice])
            goal_statement = robot_game_action.goals_statment_list[correctChoice]
            
            
            
            game_screen.show_play_screen(speed_tap_game.player_score,
                                         speed_tap_game.robot_score)
            game_screen.show_goal_statement(goal_statement)
            
            # Cozmo get in ready position
            robot_game_action.act_out(robot, "wait")
            
           
            # Deal the hand
            speed_tap_game.deal_hand()
            cozmo.logger.info("PD : Hand delt : %s" % deal_count)
            #print("Pre: %s" % datetime.now())
            monitor_player_tap.listen = True
            if robot_game_action.practice:
                cozmo_goal = correctChoice
            else:
                cozmo_goal = cozmo_fixture[deal_count - 1]
            # Get Cozmo to decide whether it is going to tap
            tapped = robot_game_action.cozmo_tap_decision(robot,
                                                          speed_tap_game,
                                                          cozmo_goal)
            
            
            
            # If player has tapped it would be registered by now      
            monitor_player_tap.listen = False
            speed_tap_game.deactivate_current_deal() 
            cozmo.logger.info("PD : Hand deactivated : %s" % deal_count)
            speed_tap_game.score_last_deal()   
            result = speed_tap_game.result_track[-1]
            cozmo.logger.info("PD : Result : %s" % RESULT_STATEMENT[result])
            game_screen.show_play_screen(speed_tap_game.player_score,
                                         speed_tap_game.robot_score)
            cozmo.logger.info("PD : After hand %s player score : %s" % (deal_count, speed_tap_game.player_score))
            cozmo.logger.info("PD : After hand %s cozmo score  : %s" % (deal_count, speed_tap_game.robot_score))
            game_screen.show_selection(result, correctChoice) 
            if robot_game_action.practice:
                game_screen.show_goal_statement(goal_statement)
            else:
                game_screen.show_goal_statement("")
             
            if robot_game_action.practice:
                # We need to track practice round so that
                # we know the player has correctly understood the game
                if result==correctChoice:
                    track_correct_practice += 1
                    cozmo.logger.info("PD : CORRECT for %s times" % track_correct_practice)
                    
                    
                else:
                    cozmo.logger.info("PD : INCORRECT choice. Chances left: %s " % (robot_game_action.rounds_to_play - deal_count -1))
                    
                    # One wrong implies all wrong
                    track_correct_practice = 0
                    
                
                # We are not tracking scores across games for 
                # practice so reset deal                
                speed_tap_game.reset_deals()
                                  
                     
            deal_count += 1                
            
            #time.sleep(2)
            # Cozmo check out score
            robot_game_action.act_out(robot, "stand_back")
            robot_game_action.act_out(robot, "check_score")
            
            robot_cube.stop_light_chaser()
            player_coop_cube.stop_light_chaser()
            player_defect_cube.stop_light_chaser()
            robot_cube.set_lights_off()
            player_coop_cube.set_lights_off()
            player_defect_cube.set_lights_off()
            
            if robot_game_action.practice and track_correct_practice >= pass_criteria:
                cozmo.logger.info("PD : Practice Passed") 
                print("PRACTICE PASSED")
                break
            elif not robot_game_action.practice and result == X_X :
                if robot_game_action.rounds_to_play >= 35:
                    cozmo.logger.info("PD : Over 15 rounds of missing data. We will stop.")
                    break;
                else:
                    cozmo.logger.info("PD : Rounds incremented to compensate for missing data")
                    robot_game_action.rounds_to_play += 1
                    # We missed a even paced tap/no tap decision by cozmo so append it 
                    # at the end to maintain balance
                    cozmo_fixture.append(cozmo_goal)
                    cozmo_fixture[deal_count - 2] = -1 
                    cozmo.logger.info("PD : Updated cozmo plan")
                    log_deal_plan(cozmo_fixture)
                
            if deal_count <= robot_game_action.rounds_to_play:
                robot.move_lift(3)
                if robot_game_action.practice or deal_count%5 == 0:
                    #robot.drive_wheels(-50, -50, duration=0.5)
                    robot.go_to_object(robot_cube, distance_mm(35.0)).wait_for_completed()
                else:
                    robot.drive_wheels(100, 100, duration=1.5)
                    time.sleep(1.5)
                    
                
                cozmo.logger.info("PD : Ready for next deal")            
            
            
            
        # clear up games to show result    
        robot_cube.stop_light_chaser()
        player_coop_cube.stop_light_chaser()
        player_defect_cube.stop_light_chaser()
        robot_cube.set_lights_off()
        player_coop_cube.set_lights_off()
        player_defect_cube.set_lights_off()
        cozmo.logger.info("PD : Done playing")   
        robot_game_action.act_out(robot, "stand_back")
       
        time.sleep(2)
        
        robot.go_to_object(robot_cube, distance_mm(60.0)).wait_for_completed()
        
        #display_screen.root.mainloop()
        
        if robot_game_action.practice and deal_count >= robot_game_action.rounds_to_play:
            cozmo.logger.info("PD : Practice Failed") 
            print("PRACTICE FAILED")
        
    finally:
         monitor_player_tap.game_on = False
         robot_cube.stop_light_chaser()
         player_coop_cube.stop_light_chaser()
         player_defect_cube.stop_light_chaser()
         robot_cube.set_lights_off()
         player_coop_cube.set_lights_off()
         player_defect_cube.set_lights_off()
         monitor_player_tap.join()
         
         del speed_tap_game
         del player_coop_cube
         del player_defect_cube
         del robot_cube

    
    game_screen.master.destroy() 
         
