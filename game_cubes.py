import asyncio
import cozmo

from constants import (
                        START_CUBE,
                        TAP_CUBE,
                        COOP_CUBE,
                        DEFECT_CUBE,
                        #DEAL_DONE_CUBE,
                        RED_LIGHT,
                        GREEN_LIGHT,
                        YELLOW_LIGHT,
                        SEA_LIGHT,
                        BLUE_LIGHT,
                        WHITE_LIGHT
                    )

class BlinkyCube(cozmo.objects.LightCube):
    '''Subclass LightCube and add a light-chaser effect.'''
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._chaser = None
        

    def start_light_chaser(self, status):
        '''Cycles the lights around the cube with 1 corner lit up green,
        changing to the next corner every 0.1 seconds.
        '''
        
        chase_light = cozmo.lights.off_light
        if status == START_CUBE:
            chase_light = GREEN_LIGHT
        elif status == TAP_CUBE:
            chase_light = WHITE_LIGHT
        elif status == COOP_CUBE:
            chase_light = YELLOW_LIGHT
        elif status == DEFECT_CUBE:
            chase_light = BLUE_LIGHT
        #elif status == DEAL_DONE_CUBE:
        #    chase_light = SEA_LIGHT
        
        if not self._chaser:           
            async def _chaser(status):            
                while True:
                    for i in range(4):
                        cols = [cozmo.lights.off_light] * 4
                        cols[i] = chase_light
                        self.set_light_corners(*cols)
                        await asyncio.sleep(0.1, loop=self._loop)
            self._chaser = asyncio.ensure_future(_chaser(chase_light), loop=self._loop)

    def stop_light_chaser(self):
        if self._chaser:
            self._chaser.cancel()
            self._chaser = None
            
    def start_hand(self, colour1, colour2=None):
        if colour2:
            cols = [colour1, colour2, colour1, colour2]
        else:
            cols = [colour1] * 4
        #print("%s" % cols)
        self.set_light_corners(*cols)
        
   
    
    
        