from psychopy.visual import TextStim
from psychopy import visual, data, event, core, gui, sound
from numpy.random import binomial
import numpy as np
import pandas as pd
import serial
import cedrus_util
from PIL import Image
import pygame
import os

def trialvalues():
    blocks = 1
    trials = 84
    numCorr = 74
    return trials,blocks,numCorr

def xstart(button):
    # x = (np.ceil(len(button)/2) * 100) - 100
    x = (np.ceil(len(button)/2) * 200) - 200
    return -x

def deterMove(key,posi,options):
    #print(options)
    orig = posi
    if len(options) == 0:
        return 0
    #determine how key moves depending on index
    if key == [6]: #move left
        posi = posi-1
    elif key == [-1]: #move right
        posi = posi + 1
    elif key == [4] or key ==[5]: #move up
        if posi >= int(len(options)/2):
            posi = posi - int(len(options)/2)
        else:
            posi = posi + int(len(options)/2)
    #elif key == [5]: #move down
    #    posi = posi + int(len(options)/2)
    if 0 <= posi < len(options): #check it is a possible move
        return posi
    #else:
    #    return orig
    if posi < 0:
        return len(options)-1
    if posi > len(options)-1:
        return 0
    #return original position if not possible

    
def optiongenerate(win, ser, keymap, block, trial, frameRate, timer, totalStimuliDisplay, feat_lst, attributes,all_feats=None, type = 'opt', ans = None, test = False, ml_res = None,options = None,posi=None,key = None, data=None):
    if type == 'opt' or type == 'select':
        
        startTime = timer.getTime()
        
        stim = [] 
        all_feats = {}
        pcell=[]
        y = 240 #100
        ### display known features
        for feat in feat_lst:
        ## display the information (feat: attributes[feat].values[0])##
            line = feat+': ' + str(attributes[feat].values[0])
            all_feats[feat] = attributes[feat].values[0]
            # stimit = TextStim(win, text = line, color = 'white', pos = (0,y),font='freesans')
            stimit = TextStim(win, text = line, color = 'white', pos = (0,y),font='freesans',height = 42,wrapWidth = 950)
            stim.append(stimit)
            # y -= 60
            y -= 100
        # stim.append(TextStim(win, text = '<$50,000\t\t\t>$50,000',color = 'white', pos = (0,-400))) #answer line
        stim.append(TextStim(win, text = '<$50,000\t\t\t>$50,000',color = 'white', pos = (0,-400),height = 42,wrapWidth = 950)) #answer line
        pcell.append(visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(930,-230))) # photostim bottom analog right
        pcell.append(visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(930,-110))) # photostim top digital right
        pcell1 = visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(930,-230)) # photostim bottom analog right
        pcell2 = visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(930,-110)) # photostim top digital right
        #screenshot = visual.BufferImageStim(win, stim=stim)
        #screenshot.setAutoDraw(True)
        
        all_opt = []
        if type == 'select':
            ## show option line
            x = xstart(options)
            y = -200
            
            for ind,item in enumerate(options):
                ### start fresh line if halfway through
                #print(ind,item)
                if ind == int(len(options)/2):
                    x = xstart(options)
                    # y = -250
                    y = -300
                ## choose highlight based on position
                if ind == posi:
                    # disp = TextStim(win, text = item, color = 'white', pos = (x,y),font = 'freesans')
                    disp = TextStim(win, text = item, color = 'white', pos = (x,y),font = 'freesans',height = 42,wrapWidth = 950)
                else:
                    # disp = TextStim(win, text = item, color = 'black', pos = (x,y),font = 'freesans')
                    disp = TextStim(win, text = item, color = 'black', pos = (x,y),font = 'freesans',height = 42,wrapWidth = 950)
                #stim.append(disp)
                all_opt.append(disp)
                # x += 200
                x += 400
        full = stim+all_opt
        screenshot = visual.BufferImageStim(win, stim= full)
        light = visual.BufferImageStim(win, stim= full + pcell)
        #light.setAutoDraw(True)
        #screenshot.setAutoDraw(True)
        bufferDuration = timer.getTime() - startTime
        totalFrames = round(bufferDuration  * frameRate)
        print(bufferDuration)
        
        ### display options for other features using textstim
    
        keep_going = True
        
        cedrus_util.reset_timer(ser)    # reset responsebox timer
        #totalFrames = 0
        keylist = []
        key = [0]
        first = True
        cedrus_util.clear_buffer(ser)
        #core.checkPygletDuringWait = False
        while keep_going: # 0(n)
            totalFrames += 1
            screenshot.draw()
            pcell1.draw()
            pcell2.draw()
            #light.draw()
            win.flip()
            #light.setAutoDraw(False)
            screenshot.setAutoDraw(True)
            
            receiveBuffer = ser.in_waiting
            ###add movement here?
            if receiveBuffer >= 6:
                if first:
                    reactionTimer = timer.getTime()
                    print(reactionTimer)
                    first = False
                #core.wait(0.25)
                keylist.append(ser.read(ser.in_waiting))
                key, press, time = cedrus_util.readoutput([keylist[-1]], keymap)
                
                #screenshot.setAutoDraw(False)
                if type == 'select':
                    while press == [1] and key not in [[1],[2],[3]] and len(options)>0:
                        screenshot.setAutoDraw(False)
                        posi = deterMove(key,posi,options)
                        all_opt[posi].color = 'white'
                        for i,item in enumerate(all_opt):
                            if  i != posi:
                                all_opt[i].color = 'black'
                        #print(posi,i)
                        screenshot = visual.BufferImageStim(win, stim=stim+all_opt)
                        screenshot.setAutoDraw(True)
                        win.flip()
                        keylist.append(ser.read(ser.in_waiting))
                        try:
                            key, press, time = cedrus_util.readoutput([keylist[-1]], keymap)
                        except IndexError:
                            print('Button held')
                            press=[0]
                        print(key,press)
                    if press == [1] and key == [1] and len(options)>0:
                        posi = options[posi]
                        keep_going = False
                        #response to other keypress
                if type == 'opt':
                    if press == [1] and (key == [2] or key == [3]):
                        keep_going = False
            cedrus_util.clear_buffer(ser)    
        

        reactionTime = reactionTimer- startTime
        rtFrames = round(reactionTime * frameRate)
        print(reactionTime,rtFrames)
        # convert the time of correct button push
        try:
            reactionTimeCedrus = cedrus_util.HexToRt(cedrus_util.BytesListToHexList(time))
        except IndexError:
            print('Index Error Instance Caught')
            reactionTimeCedrus = 999
            
        #rtFrames = totalFrames
    

        #data = None
        #correct = None
        screenshot.setAutoDraw(False)
        
        
        
        if key == [1]:
            #penaltyFrameTime = int(0.5 * frameRate)
            #for frame in range(penaltyFrameTime): # waits 0.5 seconds before next sample
            #win.flip()        
            
            endTime = timer.getTime() - startTime # end time is full time because reaction time does not capture navigation of screen
            totalFrames = round((timer.getTime() - startTime) * frameRate)
            #totalFrames += penaltyFrameTime # adding the penalty in frames.
        else:
            endTime = reactionTime
            totalFrames = round((reactionTimer-startTime)*frameRate)
        print(totalFrames)
        
        data = {'Block': block, 'Trial': trial, 'Stim Type': type, 'Feats Used': totalStimuliDisplay, 'All Features': all_feats, 'Response': key, 'Start Time (ms)': startTime * 1000, 'Reaction Time (ms)':  reactionTime * 1000, 'CEDRUS Reaction Time (ms)': reactionTime, 'Reaction Time (frames)': rtFrames, 'Total Time (ms)': endTime * 1000, 'Total Frames': totalFrames}
        return (key,data,posi,all_feats)
    
    
    elif type == 'response':
        # photocell1.setAutoDraw(False)
        #photocell2.setAutoDraw(False)
        fixation = TextStim(win, text = '+', pos = (0,0))
        # fixation.height = 50
        fixation.height = 85
        photocell1 = visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(-930, -230))
        photocell1.setAutoDraw(True)
        
        keep_going = True
        startTime = timer.getTime()
        cedrus_util.reset_timer(ser)    # reset responsebox timer
        totalFrames = 0
        
        if (key == [2] and ans == 0) or (key == [3] and ans == 1):
            correct = True
            correctFrameTime = int(0.5 * frameRate)
            if test: #supresss feedback
                fixation.color = 'blue'
            else:
                fixation.color = 'green'
            #fixation.color = 'green'
            fixation.setAutoDraw(True)
            for frame in range(correctFrameTime): # waits 0.5 seconds before next sample
                win.flip()
            totalFrames += correctFrameTime
        else:
            correct = False
            #incorrect.play()
            incorrectFrameTime = int(0.5 * frameRate)
            if test: #supresss feedback
                # no feedback if performing > specified accuracy after minimum amt of trials
                fixation.color = 'blue'
            else:
                fixation.color = 'red'
            #fixation.color = 'red' 
            fixation.setAutoDraw(True)
            for frame in range(incorrectFrameTime): # waits 0.5 seconds before next sample
                win.flip()
            totalFrames += incorrectFrameTime
        fixation.setAutoDraw(False)
        photocell1.setAutoDraw(False)
        for frame in range(int(0.5*frameRate)): # waits .5 second before next trial. The ISI
            win.flip()
        endTime = timer.getTime() - startTime # end time of this fixation presentation.
        totalFrames += frameRate # adding the ISI frames.
        if key == [2]:
            subres = 0
        elif key == [3]:
            subres = 1
        else:
            subres = -1
        data = data.copy()
        data['Correct'] = correct
        data['Model Response'] = ml_res
        data['Human to ML Response'] = subres == ml_res
        data['Stim Type'] = type
        #data = {'Block': block, 'Trial': trial, 'Stim Type': type, 'Response': key, 'Correct': correct, 'Model Response': ml_res,'Human to ML Response': correct == ml_res,'Features Presented': all_feats, 'Test Period': test, 'Start Time (ms)': startTime * 1000, 'Total Time (ms)': endTime * 1000, 'Total Frames': totalFrames}

        
        return data




def trial(win, ser, keymap, block, trial, frameRate, timer, perm, df1, test=False, start=None,mlFeed =False):
    storeData = []
    repeatedStimuli = True
    totalStimuliDisplay = 0
    feat_lst = []
    options = list(perm[trial])
    posi = 1#int((len(options)-1)/4)

    suppress = 2 #how many features to start - 1
    ## White fixation for 750 ms
    fixation = TextStim(win, text = '+', pos = (0,0))
    # fixation.height = 50
    fixation.height = 85
    fixation.color = 'white'
    waitFrameTime = int(0.5 * frameRate)
    fixation.setAutoDraw(True)
    for frame in range(waitFrameTime): # waits 0.5 seconds before next trial
        win.flip()
    fixation.setAutoDraw(False)
    
    
    if start != None:
        end = set(perm[trial])-set(start[trial]) ##split feature list by pulling three features to show from combination list (start)
        perm[trial] = list(start[trial])+list(end) ## reorganizes perm[trial] places first three from combination in beginning
    
    for ind,step in enumerate(perm[trial]): #call permutation of particular index
        inc = df1.iloc[[trial]]['Income'].values[0]
        print(inc)
        #if type(posi) == str:
        #    feat_lst.append(posi)
        #    posi = int((len(options)-1)/4)
        #else:
        feat_lst.append(step)
        attr = df1.iloc[[trial]]
        [options.remove(x) for x in feat_lst if x in options]
        #print(feat_lst)
        #print(options)
        
        totalStimuliDisplay += 1
        ## pull and store models answer from same feature set
        ml_res = df1.iloc[[trial]]['ML Pred'].values[0]
            ###select option stage
        if ind >= suppress:
            optOrSkip, data, posi, all_feats = optiongenerate(win, ser, keymap, block = block, trial = trial, frameRate = frameRate, timer = timer, type = 'select', totalStimuliDisplay = totalStimuliDisplay, feat_lst = feat_lst, attributes = attr, ans = inc, test = test, ml_res = ml_res,options = options, posi = posi)

            feat_lst.append(posi)              
            storeData.append(data)
            
            optOrSkip, data, posi, all_feats = optiongenerate(win, ser, keymap, block = block, trial = trial, frameRate = frameRate, timer = timer, type = 'opt', totalStimuliDisplay = totalStimuliDisplay, feat_lst = feat_lst, attributes = attr, ans = inc, test = test, ml_res = ml_res,options = options, posi = posi)
            
            
            #storeData.append(data)
        
            ## if participant answers or reaches end of feature set
            #if optOrSkip in [[2],[3]]:
            # if mlFeed:
            #     optOrSkip,data = feedbackPage(win, ser, keymap, block, trial, frameRate, timer, df1=df1, test=test,old = optOrSkip)
            #     storeData.append(data)
                
            
            
            data = optiongenerate(win, ser, keymap, block = block, trial = trial, frameRate = frameRate, timer = timer, type = 'response', totalStimuliDisplay = totalStimuliDisplay, feat_lst = feat_lst, attributes = attr, ans = inc, test = test, ml_res = ml_res,options = options, posi = posi,key = optOrSkip,all_feats = all_feats,data = data)
            repeatedStimuli = False
            storeData.append(data)
            #print('Test trial successful')
            #print('ML correct:',ml_res)
            
            
            

            return data['Correct'], storeData
         
        
        
    



