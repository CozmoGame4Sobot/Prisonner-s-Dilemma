import asyncio
import cozmo
import time
import threading

from constants import ( PLAYER_COOP,
                        PLAYER_DEFECT)

class Human_Listener(threading.Thread):
#class Human_Listener():
    def __init__(self,
                 game_robot,
                 human_cube_1,
                 human_cube_2,
                 tap_game):
        threading.Thread.__init__(self)
        self.player_coop_cube  = human_cube_1
        self.player_defect_cube = human_cube_2
        self.robot = game_robot
        self.game = tap_game
        self.game_on = False
        self.listen = False

    def run(self):
        player_cubes = [self.player_coop_cube.object_id, 
                        self.player_defect_cube.object_id ]
        while self.game_on:
            try:
                if self.listen:
                    tapped_event = self.robot.world.wait_for(cozmo.objects.EvtObjectTapped,timeout=3)
                    if tapped_event and tapped_event.obj.object_id in player_cubes:
                        self.listen = False
                        if tapped_event.obj.object_id == self.player_coop_cube.object_id: 
                            cozmo.logger.info("PD : Player tapped to share")
                            self.game.register_tap(tap_type=PLAYER_COOP)
                        else:
                            cozmo.logger.info("PD : Player tapped to grab")
                            self.game.register_tap(tap_type=PLAYER_DEFECT)
                        
                else:
                    time.sleep(0.5)
            except asyncio.TimeoutError:
                pass