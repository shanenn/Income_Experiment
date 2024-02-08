#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 17/08/2023 15:05:55

@author: shanenn
"""
from psychopy.visual import TextStim, GratingStim
from psychopy import visual, core, logging
import feat3ml as feat3
from itertools import combinations, permutations
from instructAndSave import instructions, blockInstructions, informationInputGUI2, saveExperimentData
import pandas as pd
import numpy as np
import serial
import cedrus_util
import os






# this version of the experiment has the train session separate from the test session
def experiment (participantInfo, dataPath):
    
    full = False ### true: use fullmodel.py false: use individual models
    df_split = '7525'
    thermcamera = True
    if participantInfo['Section'] == 'Three Feature Training':
        thermcamera = False
    numTrials3, blocks3, numCorrectToEnd3 = feat3.trialvalues()
    trainTrials2, trainblocks2 = feat3.trainvalues()
 
    if blocks3 * numTrials3 < numCorrectToEnd3:
        print('Number Correct to end too large')
        core.quit()


    try:
        np.random.seed(int(participantInfo['Participant ID']))
    except ValueError:
        print('\''+participantInfo['Participant ID']+'\'', 'is an invalid value. Defaulting to id value: 0')
        participantInfo['Participant ID'] = '0'
        np.random.seed(int(participantInfo['Participant ID']))
        # np.random.seed(0)  
        
    start = list(combinations(['Workclass','Highest Degree','Marital Status','Race','Gender','Occupation','Hours per Week','Age'],3))#,'Years of Education'],3)) 
    np.random.shuffle(start)    
    fn_list = [f'{i}{df_split}.csv' for i in ['Train_','Prac1_','Prac2_']]
    try:
        for fn in fn_list:
            path = os.path.join(os.getcwd(), '../data/' + 'Subject' + participantInfo['Participant ID']+ '/' +'subject'+participantInfo['Participant ID']+'_'+fn)
            pd.read_csv(path)
            path = os.path.join(os.getcwd(), '../data/' + 'Subject' + participantInfo['Participant ID']+ '/' +'subject'+participantInfo['Participant ID']+'_fullmodel_'+fn)
            pd.read_csv(path)
    except FileNotFoundError:
        from modelpredictcsv import sub_model_csv_read,full_model_csv_read
        print('Shuffling csvs')
        sub_model_csv_read(int(participantInfo['Participant ID']),df_split)
        full_model_csv_read(int(participantInfo['Participant ID']),df_split)

    perm = list(permutations(['Workclass','Highest Degree','Marital Status','Race','Gender','Native Country','Occupation','Hours per Week','Age'],9))
    np.random.shuffle(perm)
    percent = [0,0]

    # # Socket settings.
    # HOST = '127.0.0.1'
    # PORT = 1033
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # # messages to send to thermal camera.
    # msgCollect = 'Collect'
    # msgEndTrial = bytes('Stop', 'utf-8')
    # msgEndExp = bytes('End', 'utf-8')

    try:
        # s.bind((HOST, PORT))
        # s.listen(1) # only one connection
        # print(f"Listening on {HOST}:{PORT}...")

    
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
            factor3 = numTrials3 * blocks3
        else: ###this will activate if session == 1
            factor3 = 0

        pcell = []
        pcell.append(visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(930,-230))) # photostim bottom analog right
        pcell.append(visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(930,-110))) # photostim top digital right
        pcell.append(visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(-930, -230))) # photostim bottom analog left
        # pcell.append(visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(-930,-110))) # photostim top digital left

        # featlight = visual.BufferImageStim(win, stim=pcell[1:]) #1

        # resp = visual.TextStim(win, text = '+',color = 'yellow',pos = (0,0), height = 50) #answer line
        resp = visual.TextStim(win, text = '+',color = 'yellow',pos = (0,0), height = 85) #answer line
        resp = visual.BufferImageStim(win, stim=[resp]+[pcell[1]]) #+[pcell[0]]2


        # mask = GratingStim(win, tex=np.full((256,256),-1), mask=None, size=(550,50)) #3
        # screenshot = visual.TextStim(win,text = '',color='white',font='FreeSans',height = 28,wrapWidth = 550,contrast = 2,pos = (0,0)) # 4

        # keep_txt = visual.TextStim(win,text = "Pass",color='red',font='FreeSans',height = 75,wrapWidth = 550,contrast = 2,pos = (-150,0))
        # pass_txt = visual.TextStim(win,text = "Keep",color='royalblue',font='FreeSans',height = 75,wrapWidth = 550,contrast = 2,pos = (150,0))
        screenshot = visual.TextStim(win,text = '',color='white',font='FreeSans',height = 42,wrapWidth = 950,contrast = 2,pos = (0,0)) # 4

        keep_txt = visual.TextStim(win,text = "Pass",color='red',font='FreeSans',height = 100,wrapWidth = 950,contrast = 2,pos = (-150,0))
        pass_txt = visual.TextStim(win,text = "Keep",color='royalblue',font='FreeSans',height = 100,wrapWidth = 950,contrast = 2,pos = (150,0))
        kp_prompt = visual.BufferImageStim(win, stim = [keep_txt]+[pass_txt]+[pcell[1]]) #+[pcell[0]]5

        # firstlight = visual.BufferImageStim(win, stim=pcell) #7
        # fixation = TextStim(win, text = '+', pos = (0,0),height = 50)
        fixation = TextStim(win, text = '+', pos = (0,0),height = 85)

        screens = {'resp':resp, 'screenshot':screenshot,'kp_prompt':kp_prompt,'fixation': fixation,
                   'anaRight':pcell[0],'cameraCell':pcell[1],'anaLeft':pcell[2]}
                
        # if thermcamera:
        #     # wait for connection
        #     subprocess.Popen(['python', 'clientexperiment.py', dataPath])        
        #     conn, addr = s.accept()
        #### start experiment
        experimentData.append(instructions(win, timer, ser, keymap, 0))
        experimentData.append(instructions(win, timer, ser, keymap, 1))
        experimentData.append(instructions(win, timer, ser, keymap, 2))
        experimentData.append(instructions(win, timer, ser, keymap, 3))




        if participantInfo['Section'] == 'Three Feature Training':
            ses = str(int(participantInfo['Session']) - 2)
            path = 'Prac'+ses+'_'+df_split+'.csv'
            df = pd.read_csv(os.path.join(os.getcwd(), '../data/' + 'Subject' + participantInfo['Participant ID']+ '/' +'subject'+participantInfo['Participant ID']+'_'+path))
            if full:
                df = pd.read_csv(os.path.join(os.getcwd(), '../data/' + 'Subject' + participantInfo['Participant ID']+ '/' +'subject'+participantInfo['Participant ID']+'_fullmodel_'+path))
            train = True

            if len(start) < len(df):
                start = start * int(np.ceil((len(df)/len(start))))


            experimentData.append(instructions(win, timer, ser, keymap, 8))
            experimentData.append(instructions(win, timer, ser, keymap, 9))

            for blk in range(trainblocks2): ##Guess each block
                ##Skip to next block(s) if necessary
                if blk < int(participantInfo['Block'])-1:
                    continue
                for i in range(trainTrials2):
                    # ensures continuation through pd
                    tNum = i
                    i += trainTrials2*blk
                    combo = start[i]
                    print(combo)
                    print('block:', blk + 1, ' trial:', tNum + 1, ' current index:', i, ':')
                    correct, data = feat3.trial(win, ser, keymap, block = blk, trial = i, frameRate = frameRate, timer = timer, perm = perm, df1 = df,start = combo,mlFeed = train, screens=screens)
                    print('Participant correct:',correct)
                    experimentData += data
                    print('Data:',data)
                    if data[0]['Response'] != -1:
                        if correct:
                            percent[0] += 1
                        percent[1] += 1
                        print('Current percent:',percent[0]/percent[1])
                    # 

                experimentEndTime = timer.getTime() * 1000
                saveExperimentData(participantInfo, experimentStartTime, experimentEndTime, experimentData, blk, dataPath)

                if numCorrectToEnd3 != None and numCorrectToEnd3 == 0:
                    experimentData.append(instructions(win, timer, ser, keymap, -1))
                    break
                else:
                    experimentData.append(blockInstructions(win, timer, ser, keymap, blk + 1, trainblocks2,percent=percent))

            # print('Percent Correct:',percent[0]/percent[1])
            print(percent)        



        if participantInfo['Section'] == 'Three Feature':


            train = False
            df = pd.read_csv(os.path.join(os.getcwd(), '../data/' + 'Subject' + participantInfo['Participant ID']+ '/' +'subject'+participantInfo['Participant ID']+'_Train_'+df_split+'.csv'))
            if full:
                df = pd.read_csv(os.path.join(os.getcwd(), '../data/' + 'Subject' + participantInfo['Participant ID']+ '/' +'subject'+participantInfo['Participant ID']+'_fullmodel_Train_'+df_split+'.csv'))

            if len(start) < len(df):
                start = start * int(np.ceil((len(df)/len(start))))
            experimentData.append(instructions(win, timer, ser, keymap, 10))
            experimentData.append(instructions(win, timer, ser, keymap, 11))




            for blk in range(blocks3): ##Guess each block
                ##Skip to next block(s) if necessary
                if blk < int(participantInfo['Block'])-1:
                    continue
                for i in range(numTrials3):
                    # ensures continuation through pd
                    tNum = i
                    i += numTrials3*blk + factor3
                    combo = start[i]
                    print(combo)
                    print('block:', blk + 1, ' trial:', tNum + 1, ' current index:', i, ':')
                    correct, data = feat3.trial(win, ser, keymap, block = blk, trial = i, frameRate = frameRate, timer = timer, perm = perm, df1 = df,start = combo,mlFeed = train, thermcamera = thermcamera, screens=screens)
                    print('Participant correct:',correct)
                    experimentData += data
                    print('='*20)
                    print('Data:',data)
                    if data[0]['Response'] != -1:
                        if numCorrectToEnd3 != None and correct:
                            numCorrectToEnd3 -= 1
                            percent[0] += 1
                        percent[1] += 1
                        print('Correct needed:',numCorrectToEnd3)
                        print('Current percent:',percent[0]/percent[1])

                    if numCorrectToEnd3 != None and numCorrectToEnd3 == 0:
                        break

                experimentEndTime = timer.getTime() * 1000
                saveExperimentData(participantInfo, experimentStartTime, experimentEndTime, experimentData, blk, dataPath)

                if numCorrectToEnd3 != None and numCorrectToEnd3 == 0:
                    experimentData.append(instructions(win, timer, ser, keymap, -1))
                    break
                else:
                    experimentData.append(blockInstructions(win, timer, ser, keymap, blk + 1, blocks3,percent=percent))

            # print('Percent Correct:',percent[0]/percent[1])   
    
    except OSError as e:
        print(f"Error: {e}")
        
    #finally:
        # if thermcamera:
        #     conn.sendall(msgEndExp)
        #     s.close()
        win.close()
        core.quit()
        
    
        print('Overall, %i frames were dropped.' % win.nDroppedFrames)
    # core.quit()
        return

if __name__ == '__main__':
    participantInfo = informationInputGUI2()
    currentPath = os.getcwd()
    dirpath = os.path.join(currentPath, '../data/Subject' +participantInfo['Participant ID'])
    path = os.path.join(currentPath, '../data/Subject' +participantInfo['Participant ID']+ '/' + participantInfo['Participant ID'] + 'Session' + participantInfo['Session'])

    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)
        
    if not os.path.isdir(path):
        os.mkdir(path)
        
    if not os.path.isdir(path + '/images'):
        os.mkdir(path + '/images')
        os.mkdir(path + '/timeStamp')
        

    experiment(participantInfo = participantInfo, dataPath = path)



    

