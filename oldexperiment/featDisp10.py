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

def trialvalues(ses = '1'):
    if ses == '2':
        blocks = 3
        trials = 80
        numCorr = 220
    else:
        blocks = 3
        trials = 65
        numCorr = 175
    return trials,blocks,numCorr

def trainvalues():
    blocks = 1
    trials = 65
    return trials,blocks


def generatePage(win, ser, keymap, block, trial, frameRate, timer, feat_lst, attributes, type = 'opt', ans = None, test = False, ml_res = None, all_feats = None,key = None,data = None,trialind = None): 

    if type == 'opt':
        
        
        
        stim = [] 
        all_feats = {}
        pcell = []
        totalFrames = 0
        first = True
        pcell.append(visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(930,-230))) # photostim bottom analog right
        pcell.append(visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(930,-110))) # photostim top digital right
        #featpcell = pcell.copy()
        featpcell = pcell[0]#visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(-930,-230)) # photostim bottom analog left
        digleft = visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(-930,-110)) # photostim top digital left ?
        firstlight = visual.BufferImageStim(win, stim=pcell)
        #featlight = visual.BufferImageStim(win, stim=featpcell)
        featlight = visual.BufferImageStim(win, stim=[featpcell])
        options = visual.TextStim(win, text = '+',color = 'yellow',pos = (0,0), height = 50) #answer line
        #print(options.font)
        options = visual.BufferImageStim(win, stim=[options]+[pcell[0],digleft])
        #y = 240 #225
        y = 0
        screenshot = visual.TextStim(win,text = '',color='white',font='FreeSans',height = 28,wrapWidth = 550,contrast = 2)
        myTex = np.full((256,256),-1)
        mask = GratingStim(win, tex=myTex, mask=None, size=(550,50))
        #myStim = 
#myStim.draw()
#win.flip()
        ## loop to display each feature
        startTime = timer.getTime()
        for feat in feat_lst:
        ## display the information (feat: attributes[feat].values[0])##
            #start = timer.getTime()
            line = feat+': ' + str(attributes[feat].values[0])
            all_feats[feat] = attributes[feat].values[0]
            #stim.append(line)
            #screenshot.text = '\n\n\n'.join(stim)
            screenshot.text = line
            screenshot.pos = (0,y)
            screenshot.setAutoDraw(True)
            if first: ### first feat has different pcell from rest
                firstlight.draw()
                first = False
            else:
                featlight.draw()
            #print(timer.getTime())############
            for frame in range(int(0.5*frameRate)): # waits 0.5 seconds before next sample
                #print(screenshot.color)
                win.flip()
            screenshot.setAutoDraw(False)
            mask.setAutoDraw(True)
            for frame in range(int(0.3*frameRate)): # waits 0.5 seconds before next sample
                win.flip()
            mask.setAutoDraw(False)
            #mask.tex = np.random.random((256,256))
        options.setAutoDraw(True)
        stimDuration = timer.getTime() - startTime
        cedrus_util.reset_timer(ser)    # reset responsebox timer
        keylist = []
    
        cedrus_util.clear_buffer(ser)
        reactionTime = False
       # while keep_going: # 0(n)
        for i in range(int(1*frameRate)): ### 1 sec of response time
            #rtFrames += 1
        
            win.flip()
            receiveBuffer = ser.in_waiting
        
            if receiveBuffer >= 6:
                keylist.append(ser.read(ser.in_waiting))
                key, press, time = cedrus_util.readoutput([keylist[-1]], keymap)
                if press == [1] and (key == [2] or key == [3]):
                    #keep_going = False
                    reactionTimer = timer.getTime()
                    reactionTime = reactionTimer - stimDuration - startTime
                    rtFrames = round(reactionTime * frameRate)
                    break
            cedrus_util.clear_buffer(ser)
        if not reactionTime:
            reactionTime = -.999
            rtFrames = round(reactionTime * frameRate)
            reactionTimer = timer.getTime()
            key = [-1]
        print(key)
        # convert the time of correct button push
        try:
            reactionTimeCedrus = cedrus_util.HexToRt(cedrus_util.BytesListToHexList(time))
        except IndexError:
            print('Index Error Instance Caught')
            reactionTimeCedrus = -999
        except UnboundLocalError:
            print('No Response')
            reactionTimeCedrus = -999

        #rtFrames = totalFrames
        totalTime = reactionTimer-startTime
        totalFrames = round(totalTime*frameRate)
        

        options.setAutoDraw(False)
        firstlight.setAutoDraw(False)
        screenshot.setAutoDraw(False)
        #endTime = reactionTime
        if (key == [2] and ans == 0) or (key == [3] and ans == 1):
            correct = True
        else:
            correct = False
        print(correct)
        if key == [2]:
            subres = 0
        elif key == [3]:
            subres = 1
        else:
            subres = -1
        data = {'Block': block, 'Trial': trial, 'Stim Type': type, 'Correct': correct,'Reference Index': trialind, 'Correct Answer' : ans, 'All Features': all_feats, 'Response': subres, 'Start Time (ms)': startTime * 1000,'Stim Dur': stimDuration * 1000, 'Reaction Time (ms)':  reactionTime * 1000, 'CEDRUS Reaction Time (ms)': reactionTime, 'Reaction Time (frames)': rtFrames, 'Total Time (ms)': totalTime * 1000, 'Total Frames': totalFrames}
        
    elif type == 'response':
        # photocell1.setAutoDraw(False)
        #photocell2.setAutoDraw(False)
        fixation = TextStim(win, text = '+', pos = (0,0))
        fixation.height = 50
        photocell1 = visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(-930, -230))
        photocell1.setAutoDraw(True) 
        if (key == [2] and ans == 0) or (key == [3] and ans == 1):
            correct = True
            #correctFrameTime = int(0.5 * frameRate)
            if test:
                fixation.color = 'blue'
            else:
                fixation.color = 'green'
            #fixation.color = 'green'
            fixation.setAutoDraw(True)
            for frame in range(int(0.5*frameRate)): # 0.5 seconds of feedback before next trial
                win.flip()
            #totalFrames += correctFrameTime
        else:
            correct = False
            #incorrect.play()
            #incorrectFrameTime = int(0.5 * frameRate)
            if key == [-1]:
                fixation.color = 'gray'
            elif test:
                # no feedback if performing > specified accuracy after minimum amt of trials
                fixation.color = 'blue'
            else:
                fixation.color = 'red'
            fixation.setAutoDraw(True)
            #print(waitFrameTime)
            for frame in range(int(0.5*frameRate)): # 0.5 seconds of feedback before next trial
                win.flip()
            #totalFrames += incorrectFrameTime
        fixation.setAutoDraw(False)
        photocell1.setAutoDraw(False)
        waitFrameTime = int(np.random.uniform(30,60))
        for frame in range(waitFrameTime): # waits 1 second before next trial. The ISI
            win.flip()
        #endTime = timer.getTime() - startTime # end time of this fixation presentation.
        #totalFrames += frameRate # adding the ISI frames.
        data = data.copy()
        data['Stim Type'] = type
        data['Model Response'] = ml_res
        data['Human to ML Response'] = data['Response'] == ml_res
        data['All Features'] = data['All Features']
        

        
    return key, data, all_feats

def trial(win, ser, keymap, block, trial, frameRate, timer, perm, df1, test=False, mlFeed=False):
    storeData = []
    feat_lst = []

    #print(df1.iloc[[trial]])
    
    ## White fixation for 750 ms
    fixation = TextStim(win, text = '+', pos = (0,0))
    fixation.height = 50
    fixation.color = 'white'

    waitFrameTime = np.random.uniform(.5,1)
    #print(waitFrameTime)
    #waitFrameTime = int(0.5 * frameRate)
    fixation.setAutoDraw(True)
    #print('Start',timer.getTime())
    for frame in range(int(waitFrameTime*frameRate)): # waits .75 seconds before next trial
        win.flip()
    fixation.setAutoDraw(False)
    
    #print("Is this what you need?",list(perm[trial]))
    for ind,step in enumerate(perm[trial]): #call permutation of particular index
        inc = df1.iloc[[trial]]['Income'].values[0]
        #print(inc)
        feat_lst.append(step)
        attr = df1.iloc[[trial]]
        trialind = df1.iloc[[trial]]['index'].values[0]
        ## pull and store models answer from same feature set
        ml_res = df1.iloc[[trial]]['ML Pred'].values[0]
        #there is not opt period. partic will see features and respond for each step.
        #if ind == len(perm[trial])-1: #use to choose how many starting features before starting
    print(inc)
    response, data, all_feats = generatePage(win, ser, keymap, block = block, trial = trial, frameRate = frameRate, timer = timer, type = 'opt', feat_lst = feat_lst, attributes = attr, ans = inc, test = test, ml_res = ml_res,trialind=trialind)
    
    
    #storeData.append(data)
    # if mlFeed:
    #     response,mldata = feedbackPage(win, ser, keymap, block, trial, frameRate, timer, df1=df1, test=test,old = response)
    #     storeData.append(mldata)
    #     print('Answer',inc,', Response',response)
    
    response, data, _ = generatePage(win, ser, keymap, block = block, trial = trial, frameRate = frameRate, timer = timer, type = 'response', feat_lst = feat_lst, attributes = attr, ans = inc, test = test, ml_res = ml_res, key = response, all_feats = all_feats,data = data)

    storeData.append(data)
    return data['Correct'], storeData


