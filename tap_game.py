import argparse
import asyncio
import copy
import cozmo
from datetime import datetime
import getopt
import logging
import os
import sys 
import time
from cozmo_player import CozmoPlayerActions, cozmo_tap_game
from constants import SCORE_SETS


def add_file_logger(log_path, cozmo_action, practice):
    ''' setup file logger'''
    if practice:
        filename="Pract_%s.log" % datetime.now().strftime("%H%M%S_%d%m%Y")
    else:
        filename="Exp_%s.log" % datetime.now().strftime("%H%M%S_%d%m%Y")
    filePath = os.path.join(log_path, filename)
    
    # create error file handler and set level to info
    handler = logging.FileHandler(os.path.join(log_path, filename),"w", encoding=None, delay="true")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
    handler.setFormatter(formatter)
    
    # add file handler to cozmo
    cozmo.logger.addHandler(handler)
    
def handle_selection(cozmo_action):    
    log_path = None
    configParam = {"practice" : False,
                   "participantID":None,
                   "score_plan": None}
    log_path = None
    parser = argparse.ArgumentParser()
    parser.add_argument("--participantID", type=int, required=True,
                         help="Participant ID is required to record logs correctly")
    parser.add_argument("--ignoreLog", type=bool, nargs='?', const=True, default=False,
                        help="Provide this argument to indicate logs are to be ignores")
    parser.add_argument("--practice", type=bool, nargs='?', const=True, default=False,    
                        help="Activate practice round without robot.")
    parser.add_argument("--singleScreen", type=bool, nargs='?', const=True, default=False,    
                        help="For checking game on single screen")
    parser.add_argument('--scoreSet', type=int, choices=[1, 2], required=True,
                         help="Which score set will the game use?")
    parser.add_argument("--log", type=str, default="./logs", 
                        help="Entire log directory path. The filename is defined by the code")
    args = parser.parse_args()
    
    # Check log option entered and directory
    if not args.ignoreLog:
        if args.log=="./logs":
            log_path = args.log
        else:
            log_path = args.log
        
        if not log_path  or not os.path.isdir(log_path):
            print("ERROR!!! Please create the log directory '%s' on your system." % log_path)
            print("If you want to log at an alternative location use --log=<log_path> to enter it")
            exit(0)
        else:
            if args.participantID:
                log_path = os.path.join(log_path, 'P%s' % args.participantID)
                if not os.path.isdir(log_path):
                    os.mkdir(log_path)
            configParam["logPath"] = log_path
           
    cozmo_action.setup_ScorePlan(SCORE_SETS["score_set%s" % (args.scoreSet)])
        
    configParam["participantID"] = args.participantID
    
    if args.participantID <= 0:
        print("ERROR! Cannot proceed without participant ID.") 
        exit(0)
    
    
    if args.practice:
        configParam["practice"] = True
        cozmo_action.set_practice(True)
        
    else: 
        configParam["practice"] = False
        
    if args.singleScreen:
        cozmo_action.set_singleScreen()
       
        
    if configParam and log_path:
        add_file_logger(log_path, cozmo_action, args.practice) 
    return configParam       
    
         
if __name__ == "__main__":
  
   cozmo_action = CozmoPlayerActions()
   if handle_selection(cozmo_action):
       cozmo.run_program(cozmo_tap_game)
   del cozmo_action
   exit(0)
    
   
    
