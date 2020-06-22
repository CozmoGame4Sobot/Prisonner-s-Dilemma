# A game of Prisonner's Dilemma with Cozmo robot
The prisonner's dilemma is a classic decision analysis game in which two partners can either play cooperatively or competitively. If one of them compete while the other one cooperates then the competitive partner gets the maximum benefit while the cooperative partner gets the maximum punishment. If they both cooperate then they get a share of the benefit but less than the previous condition. If they both compete they both get a reduced punishment. 
In our game the participants plays a multi-round game of Prisonner’s Dilemma againt Cozmo(robot). For each round they get some game-coins which are shown on the screen. A running tab is kept of how much coins each player has scored. 
Cozmo’s hands are played according to two preset sets, so that it plays an equal number of cooperation and competitive decision.  The set to be played can be chosen by the experimentor at command line. The game can also be played in the practice mode to get the participant used to the scoring. In the practice mode the participants have to score the target score in each of 10 consecutive game

## Requirements. 
Cozmo (robot)
Cozmo app 1.5

We used Python version 3.5.3 with the following packages 

numpy==1.16.4

Pillow==6.1.0

cozmoclad==1.5.0

cozmo==0.14.0


The cozmo sdk(s) are a match for version Cozmo app version 1.5 . They need to be installed in order provided so that a newer version of the packages don't get pulled in.

To setup your device and computer to run custom python code, see instruction from Anki here: http://cozmosdk.anki.com/docs/initial.html

Note: To use later versions of the Cozmo app you might need to revisit the animations that have been updated. 

## To run the game from commandline

usage: tap_game.py [-h] --participantID PARTICIPANTID
                   [--ignoreLog [IGNORELOG]] 
                   [--practice [PRACTICE]]
                   [--singleScreen [SINGLESCREEN]] 
                   --scoreSet {1,2}
                   [--log LOG]


--participantID : ID of participant used for logging. Participant ID is always needed.
--singleScreen : If there is a secon
dary screen, the program expects it to be on the right where it will try to show the game score board. If you have one screen specify this argument
--log: To define the logPath somewhere other than the default location of ./logs
--ignoreLog: If logging is not required.
--scoreSet: Which set Cozmo will play
--practice: Whether the current game is in practice mode

### example
This is how the call looks from command line

python tap_game.py --participantID=4  --scoreSet=1 --practice 

python tap_game.py --participantID=4  --scoreSet=1
