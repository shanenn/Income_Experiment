#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 17/08/2023 15:05:55

@author: shanenn
"""
from psychopy import visual, core, logging
import featDisp10 as disp10
import featpick1 as pick1
from itertools import combinations, permutations
from instructAndSave import instructions, blockInstructions, informationInputGUI1, saveExperimentData
import pandas as pd
import numpy as np
import serial
import cedrus_util
import os


# this version of the experiment has the train session separate from the test session
def experiment (participantInfo, dataPath):
    
    
    numTrials, blocks, numCorrectToEnd = disp10.trialvalues(participantInfo['Session'])
    trainTrials,trainblocks = disp10.trainvalues()#numTrials*blocks - 195 ###195 is number of real trials = 1
    numTrials2, blocks2, numCorrectToEnd2 = pick1.trialvalues()

    if blocks * numTrials < numCorrectToEnd:
        print('Number Correct to end too large')
        core.quit()

    try:
        np.random.seed(int(participantInfo['Participant ID']))
    except ValueError:
        print('\''+participantInfo['Participant ID']+'\'', 'is an invalid value. Defaulting to id value: 0')
        participantInfo['Participant ID'] = '0'
        np.random.seed(int(participantInfo['Participant ID']))
        # np.random.seed(0)
        
        
    try:
        for fn in ['trial_435_7030.csv','train_100_7030.csv','select_168_7030.csv']:
            fn = os.path.join(os.getcwd(), '../data/' + 'Subject' + participantInfo['Participant ID']+ '/' +'subject'+participantInfo['Participant ID']+'_'+fn)
            pd.read_csv(fn)
    except FileNotFoundError:
        from modelpredictcsv import subject_csv_read
        print('Shuffling csvs')
        subject_csv_read(int(participantInfo['Participant ID']))
        # full_model_csv_read(int(participantInfo['Participant ID']),df_split)
    

    perm = list(permutations(['Workclass','Highest Degree','Marital Status','Race','Gender','Native Country','Occupation','Hours per Week','Age'],9))
    np.random.shuffle(perm)
    percent = [0,0]

    
    # get portname -- paste Jennys Code.
    portname, keymap = cedrus_util.getname()
    ser = serial.Serial(portname, 115200) 


    win = visual.Window(size=(1920, 1080), units='pix', fullscr = True, color = (-1,-1,-1))
    logging.console.setLevel(logging.WARNING)  #this will print if there is a delay
    win.recordFrameIntervals = True    
    win.refreshThreshold = 1/60 + 0.004
    frameRate = round(win.getActualFrameRate())
    
    cedrus_util.reset_timer(ser)    # reset responsebox timer
    timer = core.Clock()
    experimentStartTime = timer.getTime() * 1000
    experimentData = []

    if participantInfo['Session'] == '2': #start likely new set of practice trials
        factor1 = int(disp10.trialvalues('1')[0]*disp10.trialvalues('1')[1]) # use num of trials from session 1 because it differs from session 2
        factor2 = numTrials2 * blocks2 # number trials from feature select
    else: ###this will activate if session == 1
        factor1 = 0
        factor2 = 0

    df = pd.read_csv(os.path.join(os.getcwd(), '../data/' + 'Subject' + participantInfo['Participant ID'] + '/' +'subject'+ participantInfo['Participant ID'] +'_trial_435_7030.csv'))
    if participantInfo['Session'] == 'Training': ###give shorter block of practice trials
        numTrials = trainTrials
        blocks = trainblocks
        df = pd.read_csv(os.path.join(os.getcwd(), '../data/' + 'Subject' + participantInfo['Participant ID'] + '/' +'subject'+ participantInfo['Participant ID'] +'_train_100_7030.csv'))


    #### start real experiment
    experimentData.append(instructions(win, timer, ser, keymap, 0))
    experimentData.append(instructions(win, timer, ser, keymap, 1))
    experimentData.append(instructions(win, timer, ser, keymap, 2))
    experimentData.append(instructions(win, timer, ser, keymap, 3))

    
    if participantInfo['Section'] == 'Guess Only':
        experimentData.append(instructions(win, timer, ser, keymap, 4))
        experimentData.append(instructions(win, timer, ser, keymap, 5))
        for blk in range(blocks): ##Guess each block
            if blk < int(participantInfo['Block'])-1:
                continue
            print(blk)
            for i in range(numTrials):
                # ensures continuation through pd
                tNum = i
                i += numTrials*blk + factor1
                print('Current index:',i)
                print('block:', blk + 1, ' trial:', tNum + 1, ' index:', i, ':')

                correct, data = disp10.trial(win, ser, keymap, block = blk, trial = i, frameRate = frameRate, timer = timer, perm = perm, df1 = df)
                print('Participant correct:',correct)
                experimentData += data
                #print(data['Response'])
                if data[-1]['Response'] == -1:
                    pass
                elif numCorrectToEnd != None and correct:
                    numCorrectToEnd -= 1
                    percent[0] += 1
                    percent[1] += 1
                else:
                    percent[1] += 1
                if percent[1] > 0:
                    print('Correct needed:',numCorrectToEnd)
                    print('Current percent:',percent[0]/percent[1])

                
                if numCorrectToEnd != None and numCorrectToEnd == 0:
                    break

            experimentEndTime = timer.getTime() * 1000
            saveExperimentData(participantInfo, experimentStartTime, experimentEndTime, experimentData, blk, dataPath)
            if numCorrectToEnd != None and numCorrectToEnd == 0:
                experimentData.append(instructions(win, timer, ser, keymap, -1))
                break
            else:
                experimentData.append(blockInstructions(win, timer, ser, keymap, blk + 1, blocks + blocks2))
        if percent[1] > 0:
            print('Percent Correct:',percent[0]/percent[1])
        print(percent)
    if participantInfo['Session'] == 'Training': ###only activate when running training
        experimentData.append(instructions(win, timer, ser, keymap, -3))
    
    mlFeed = False
    if (blocks2 != 0 or participantInfo['Section'] == 'Select Feature') and participantInfo['Session'] != 'Training':
        win.color = (0,0,0)
        win.flip()
        df = pd.read_csv(os.path.join(os.getcwd(), '../data/' + 'Subject' + participantInfo['Participant ID'] + '/' +'subject'+ participantInfo['Participant ID'] +'_select_168_7030.csv'))
            
        #### use this block to make each possible beginning permutation
        start = list(combinations(['Workclass','Highest Degree','Marital Status','Race','Gender','Native Country','Occupation','Hours per Week','Age'],3))#,'Years of Education'],3)) 
        np.random.shuffle(start)
        if len(start) < len(df):
            start = start * int(np.ceil((len(df)/len(start))))

        experimentData.append(instructions(win, timer, ser, keymap, 6))
        if mlFeed:
            experimentData.append(instructions(win, timer, ser, keymap, -2))
        experimentData.append(instructions(win, timer, ser, keymap, 7))
        
        percent = [0,0] #refresh accuracy
        for blk in range(blocks2): ##Guess each block
            ## Will attempt to skip block if necessary only should skip if starting fromm 'select feature'
            if blk < int(participantInfo['Block'])-1 and participantInfo['Section'] == 'Select Feature':
                continue
            for i in range(numTrials2):
                # ensures continuation through pd
                tNum = i
                i += numTrials2*blk + factor2
                print('block:', blk + blocks + 1, ' trial:', tNum + 1, ' current index:', i, ':')

                correct, data = pick1.trial(win, ser, keymap, block = blk+blocks, trial = i, frameRate = frameRate, timer = timer, perm = perm, df1 = df,start = start)
                print('Participant correct:',correct)
                experimentData += data
                if numCorrectToEnd2 != None and correct:
                    numCorrectToEnd2 -= 1
                    percent[0] += 1
                percent[1] += 1
                print('Current percent:',percent[0]/percent[1])
                
                if numCorrectToEnd2 != None and numCorrectToEnd2 == 0:
                    break

            experimentEndTime = timer.getTime() * 1000
            saveExperimentData(participantInfo, experimentStartTime, experimentEndTime, experimentData, blk+blocks, dataPath)

            if numCorrectToEnd2 != None and numCorrectToEnd2 == 0:
                experimentData.append(instructions(win, timer, ser, keymap, -1))
                break
            else:
                experimentData.append(blockInstructions(win, timer, ser, keymap, blk + blocks + 1, blocks + blocks2))

        print('Percent Correct:',percent[0]/percent[1])
        print(percent)

    win.close()
    
    print('Overall, %i frames were dropped.' % win.nDroppedFrames)
    core.quit()
    return

if __name__ == '__main__':
    participantInfo = informationInputGUI1()
    currentPath = os.getcwd()
    dirpath = os.path.join(currentPath, '../data/Subject' +participantInfo['Participant ID'])
    path = os.path.join(currentPath, '../data/Subject' +participantInfo['Participant ID']+ '/' + participantInfo['Participant ID'] + 'Session' + participantInfo['Session'])

    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)
        
    if not os.path.isdir(path):
        os.mkdir(path)    

    experiment(participantInfo = participantInfo, dataPath = path)


    


