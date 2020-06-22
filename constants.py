import cozmo
START_CUBE = 0
TAP_CUBE = 1
COOP_CUBE = 2
DEFECT_CUBE = 3

COZMO_CHOICE = [[1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                [1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0],
                [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1]]


PLAYER_ID = 1
COZMO_ID = 2

PLAYER_COOP = 1
PLAYER_DEFECT = 2
COZMO_COOP = 3
COZMO_DEFECT = 4

#Score conditions
P_R = 0   # player and cozmo grab
P_O = 1   # player grab cozmo share
O_R = 2   # player share cozmo grab
O_O = 3   # player and cozmo share
X_X = 4   # undefined if player does not tap

RESULT_STATEMENT = ["Player-Grabbed Cozmo-Grabbed",
                    "Player-Grabbed Cozmo-Shared",
                    "Cozmo-Grabbed Player-Shared",
                    "Player-Shared Cozmo-Shared",
                    "Missing Data"]
RED_LIGHT = cozmo.lights.red_light
BLUE_LIGHT = cozmo.lights.blue_light
GREEN_LIGHT = cozmo.lights.green_light
YELLOW_LIGHT = cozmo.lights.Light(cozmo.lights.Color(rgb=(255, 255, 0)),
                                                        cozmo.lights.off)
PINK_LIGHT = cozmo.lights.Light(cozmo.lights.Color(rgb=(255, 0, 255)),
                                                        cozmo.lights.off)
SEA_LIGHT = cozmo.lights.Light(cozmo.lights.Color(rgb=(0, 255, 255)),
                                                        cozmo.lights.off)
WHITE_LIGHT = cozmo.lights.Light(cozmo.lights.Color(rgb=(255, 255, 255)),
                                                        cozmo.lights.off)
PURPLE_LIGHT = cozmo.lights.Light(cozmo.lights.Color(rgb=(65,0,130)),
                                                        cozmo.lights.off)


SCORE_SETS = {
              "score_set1" : [(1, 1), (10, 0), (0, 10), (7, 7)],
              "score_set2" : [(4, 4), (10, 0), (0, 10), (6,6)]
              }

                          