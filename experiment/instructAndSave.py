'''This file contains all instructions, save functions, participant information collection'''
from psychopy.visual import TextStim, GratingStim
from psychopy import visual, data, event, core, gui, sound
from numpy.random import binomial
import numpy as np
import pandas as pd
import serial
import cedrus_util
from PIL import Image
import pygame
import os



def instructions(win, timer, ser, keymap, part):
    
    ## General Instruction
    if part == 0:
        instructions = GratingStim(win, tex=None, mask=None, size=(550,50))
        

    if part == 1:
        instructions = TextStim(win, text = 'Your task will be to determine whether an individual makes MORE than $50,000 ' +
                                            'or LESS than $50,000 based on a set of features presented on the screen.\n\n' +
                                            'To continue, press any button.', pos = (0,0))
    elif part == 2:
        instructions = TextStim(win, text = 'If you feel the individual makes less than $50,000/year press the RED button. ' +
                                            'If you feel the individual makes more than $50,000/year press the BLUE button. ' +
                                            'A red fixation will display as feedback for incorrect responses, whereas a green ' +
                                            'fixation will display as feedback for correct responses.\n\n' +
                                            'To continue, press any button.', pos=(0, 0))
    elif part == 3:
        instructions = TextStim(win, text = 'There is a reward for getting trials correct. In all sections of the experiment ' +
                                            'performing well and getting enough correct answers will end the section early. ' +
                                            'Full payment will still be provided for completing the experiment early.\n\n' +
                                            'To begin the section, press any button.', pos=(0, 0))
    ## Instruction for full feature task
    elif part == 4:
        instructions = TextStim(win, text = 'In this section you will be given 9 features before being asked to make a prediction. ' +
                                            'Each feaure will be presented briefly with the category followed by the category\'s value. ' +
                                            'After seeing all features a yellow fixation will appear indicating that it is time to respond.' +
                                            'The time to respond is limited and predictions should be made quickly.\n\n' +
                                            'To continue, press any button.', pos=(0, 0))
    elif part == 5:
        instructions = TextStim(win, text = 'It is recommended NOT to try to memorize all the information. Instead, update your prediction ' +
                                            'as each feature is presented. By doing this your final prediction will be ready when the yellow ' +
                                            'fixation appears and you do not have to worry about missing the response window.\n\n'  +
                                            'The section will begin after this screen.\n' + 
                                            'To begin press any button.', pos=(0, 0))
    
    ## Instruction for feature select task
    elif part == 6:
        instructions = TextStim(win, text = 'In this section be performing the same task with less information. At the beginning ' +
                                            'of the trial you will receive THREE features. You will be asked to choose ONE ' +
                                            'feature from the options presented on the bottom of the screen. Navigate the option ' +
                                            'menu using the small WHITE buttons  on the sides of the control pad and choose your ' +
                                            'option by pressing the right large WHITE button near the center of the control pad.\n\n' +
                                            'To continue, press any button.', pos=(0, 0))
    elif part == 7:
        instructions = TextStim(win, text = 'The features you are given in the beginning will not always be the same. Please choose ' +
                                            'the new feature wisely based on what you already see to maximize important information.\n\n' +
                                            'The section will begin after this screen.\n ' + 
                                            'To begin press any button.', pos=(0, 0))
        
    ## Instruction for three feature only task (training)
    elif part == 8:
        instructions = TextStim(win, text = 'In this section you will be given a set of THREE features. After the features are presented ' +
                                            'you will be asked to make a prediction. After a prediction you will see the prediction from ' +
                                            'a machine learning model. A confidence level (as a percentage) will appear. The text will ' +
                                            'appear in RED to indicate less than $50,000 and BLUE to indicate more than $50,000.\n\n' +
                                            'To continue, press any button.', pos=(0, 0))
    elif part == 9:
        instructions = TextStim(win, text = 'Following the response of the model the correct answer will be presented. In place of a feedback ' +
                                            'fixation, the answer will be presented, colored depending on whether YOU were correct (green) or incorrect (red).\n\n' +
                                            'The section will begin after this screen.\n ' + 
                                            'To begin press any button.', pos=(0, 0))
    ## Instruction for three feature only task
    elif part == 10:
        instructions = TextStim(win, text = 'In this section you will be given a set of THREE features. After the features are presented ' +
                                            'you will be asked to make a prediction. After a prediction you may opt to PASS the question ' +
                                            'to a machine learning model or KEEP your response. This will be done by presssing the RED button ' +
                                            '(Pass) or the BLUE button (KEEP). If chosen, the model\'s response will appear as a percentage. ' + 
                                            'The text will appear in RED to indicate less than $50,000 and BLUE to indicate more than $50,000.\n\n ' +
                                            'To continue, press any button.', pos=(0, 0))
    elif part == 11:
        instructions = TextStim(win, text = 'If the question is passed to the model, the model\'s prediction will be used as the final answer. ' +
                                            'If the question is kept, your response will be used as the final answer. The color of the feedback ' +
                                            'as well as a point towards early termination of the experiment will be determined by the final answer.\n\n' +
                                            'The section will begin after this screen.\n ' + 
                                            'To begin press any button.', pos=(0, 0))
    ## If subject finishes early                            
    elif part == -1:
        instructions = TextStim(win, text = 'You correctly identified a substantial amount of trials to end this section ' +
                                            'early. This section is now complete. Please wait for experimenter to indicate when to continue.\n\n ' +
                                            'To continue, press any button.', pos=(0, 0))
    ## If subject is recieving ML response
    elif part == -2:
        instructions = TextStim(win, text = 'After a prediction you will see the prediction from a machine learning model. A confidence level (as a percentage) ' +
                                            'will appear. The text will appear in RED to indicate less than $50,000 and BLUE to indicate more than $50,000.\n\n ' +
                                            'To continue, press any button.', pos=(0, 0))
        
    ## If training is over
    elif part == -3:
        instructions = TextStim(win, text = 'The training session is now over. \n\n' +
                                            'To continue, press any button.', pos=(0, 0))
    



    instructions.setAutoDraw(True)
    keep_going = True
    totalFrames = 0
    startTime = timer.getTime()
    cedrus_util.reset_timer(ser)    # reset responsebox timer
    keylist = []
    while keep_going:
        totalFrames += 1
        win.flip()
        receiveBuffer = ser.in_waiting
        
        if receiveBuffer != 0:
            endTimer = timer.getTime()
            keylist.append(ser.read(ser.in_waiting))
            key, press, time = cedrus_util.readoutput([keylist[-1]], keymap)
            if key and press == [1]:
                break
    
    endTime = endTimer - startTime
    # convert the time of correct button push

    try:
    	endTimeCedrus = cedrus_util.HexToRt(cedrus_util.BytesListToHexList(time))
    except IndexError:
    	print('Index Error Instance Caught')
    	endTimeCedrus = 999
    
    instructions.setAutoDraw(False)
            
    return {'Stim Type': 'Instructions', 'Start Time (ms)': startTime * 1000,
            'Total Time (ms)': endTime * 1000, 'CEDRUS Total Time (ms)': endTimeCedrus, 'Total Frames': totalFrames}


def blockInstructions(win, timer, ser, keymap, block, blocks, percent = None):#, test):
    if percent != None:
        instructions = TextStim(win, text = 'Block ' + str(block) + '/' + str(blocks) + ' is now finished. Please wait for the moderator ' +
                                        'to give further instructions.\nYour current score is: ' + str(percent[0]) + '\nWhen prompted, press any button to continue.'
                                         , pos = (0,0))
    else:
        instructions = TextStim(win, text = 'Block ' + str(block) + '/' + str(blocks) + ' is now finished. Please wait for the moderator ' +
                                        'to give further instructions. When prompted, press any button to continue.'
                                         , pos = (0,0))

    
    instructions.setAutoDraw(True)
    keep_going = True
    totalFrames = 0
    startTime = timer.getTime()
    cedrus_util.reset_timer(ser)    # reset responsebox timer
    keylist = []
    while keep_going:
        totalFrames += 1
        win.flip()
        receiveBuffer = ser.in_waiting
        
        if receiveBuffer != 0:
            endTimer = timer.getTime()
            keylist.append(ser.read(ser.in_waiting))
            key, press, time = cedrus_util.readoutput([keylist[-1]], keymap)
            if key and press == [1]:
                break
    
    endTime = endTimer - startTime
    # convert the time of correct button push
    
    
    try:
    	endTimeCedrus = cedrus_util.HexToRt(cedrus_util.BytesListToHexList(time))
    except IndexError:
    	print('Index Error Instance Caught')
    	endTimeCedrus = 999
    
    instructions.setAutoDraw(False)
            
    return {'Stim Type': 'Block Instructions', 'Start Time (ms)': startTime * 1000,
            'Total Time (ms)': endTime * 1000, 'CEDRUS Total Time (ms)': endTimeCedrus, 'Total Frames': totalFrames}

def informationInputGUI1():
    exp_name = 'Income Prediction Task'
    exp_info = {'Participant ID': '',
                'Age': '',
    		    'Session': ('Training', '1', '2'),
               'Section': ('Guess Only','Select Feature'),
               'Block': (1,2,3)}

    dlg = gui.DlgFromDict(dictionary = exp_info, title = exp_name,sortKeys = False)
    exp_info['date'] = data.getDateStr()
    exp_info['exp name'] = exp_name
    
    if dlg.OK == False:
        core.quit() # ends process.
    return exp_info

def informationInputGUI2():
    exp_name = 'Income Prediction Task'
    exp_info = {'Participant ID': '',
                'Age': '',
    		    'Session': ('3', '4'),
               'Section': ('Three Feature Training','Three Feature'),
               'Block': (1,2,3,4)}

    dlg = gui.DlgFromDict(dictionary = exp_info, title = exp_name,sortKeys = False)
    exp_info['date'] = data.getDateStr()
    exp_info['exp name'] = exp_name
    
    if dlg.OK == False:
        core.quit() # ends process.
    return exp_info

def saveExperimentData(participantInfo, experimentStartTime, experimentEndTime, experimentData, block, dataPath):
    participantInfo['Experiment Start Time'] = experimentStartTime
    participantInfo['Experiment End Time'] = experimentEndTime
    participantInfo['Experiment Data'] = experimentData
    df = pd.DataFrame.from_dict(participantInfo)
    abbr = ''.join([s[0] for s in participantInfo['Section'].split()])
    csvFileName = participantInfo['Participant ID'] + '_' + participantInfo['date'] + '_block' + str(block) + '_ses' + str(participantInfo['Session']) + '_sec' + abbr + '.csv'
    df.to_csv(os.path.join(dataPath, csvFileName))
    return
