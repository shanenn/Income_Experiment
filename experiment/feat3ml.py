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



def trialvalues():
    blocks = 4
    trials = 75
    numCorr = 200
    return trials,blocks,numCorr

def trainvalues():
    blocks = 2
    trials = 60
    return trials,blocks

    
def optiongenerate(win, ser, keymap, block, trial, frameRate, timer, feat_lst, attributes,all_feats=None, type = 'opt', ans = None, test = False, ml_res = None,options = None, data=None,trialind = None, ml_prob = None, train = False,screens = None):
    

    resp=screens['resp'] # screen with response fixation
    # mask=screens['mask'] # screen to cover words
    screenshot=screens['screenshot'] # screen used for features, ml response, and wait screen
    kp_prompt=screens['kp_prompt'] # screen with pass or keep prompt
    fixation = screens['fixation'] # fixation for start and feedback
    cameraCell = screens['cameraCell']
    anaLeft = screens['anaLeft']
    anaRight = screens['anaRight']

               
    responsewindow = 1 # second to respond in test
    pkwindow = 1.5 # second to respond pk
    penaltywindow = 5.5
    if train:
        penaltywindow = .5

    if type == 'opt':
        # firstlight = visual.BufferImageStim(win, stim=pcell[:2])

    
        stim = [] 
        all_feats = {}
        totalFrames = 0
        first = True
        
        ## loop to display each feature
        startTime = timer.getTime()
        for featind,feat in enumerate(feat_lst):
        ## display the information (feat: attributes[feat].values[0])##
            #start = timer.getTime()
            line = feat+': ' + str(attributes[feat].values[0])
            all_feats[feat] = attributes[feat].values[0]


            screenshot.text = line

            screenshot.setAutoDraw(True)
            if first: ### first feat has different pcell from rest
                anaRight.setAutoDraw(True)
                first = False
            anaLeft.setAutoDraw(True)

            for frame in range(int(0.5*frameRate)): # waits 0.5 seconds before next sample
                win.flip()
            screenshot.setAutoDraw(False)
            anaLeft.setAutoDraw(False)
            anaRight.setAutoDraw(False)
            # mask.setAutoDraw(True)
            for frame in range(int(0.3*frameRate)): # waits 0.5 seconds before next sample
                win.flip()
            # mask.setAutoDraw(False)

        resp.setAutoDraw(True)
        anaRight.setAutoDraw(True)
        stimDuration = timer.getTime() - startTime
        cedrus_util.reset_timer(ser)    # reset responsebox timer
        keylist = []
        cedrus_util.clear_buffer(ser)
        reactionTime = False
        rtFrames = int(responsewindow*frameRate)


        for i in range(int(responsewindow*frameRate)): # 2 sec response window?

            win.flip()
            receiveBuffer = ser.in_waiting

            if receiveBuffer >= 6:

                keylist.append(ser.read(ser.in_waiting))
                key, press, time = cedrus_util.readoutput([keylist[-1]], keymap)
                if press == [1] and (key == [2] or key == [3]):
                    reactionTimer = timer.getTime()
                    reactionTime = reactionTimer - stimDuration - startTime
                    rtFrames = round(reactionTime * frameRate)

                    respkey = key

                    break

            cedrus_util.clear_buffer(ser)
        resp.setAutoDraw(False)
        anaRight.setAutoDraw(False)
        remainingFrames = int(responsewindow*frameRate - rtFrames) # - i
        print(remainingFrames/frameRate)
        if train:
            remainingFrames = 0
        for i in range(int(remainingFrames + 0.3*frameRate)):
            win.flip()
        if not reactionTime:
            reactionTime = -.999
            rtFrames = round(reactionTime * frameRate)
            reactionTimer = timer.getTime()
            respkey = -1
        print(respkey)
        # convert the time of correct button push
        try:
            reactionTimeCedrus = cedrus_util.HexToRt(cedrus_util.BytesListToHexList(time))
        except IndexError:
            print('Index Error Instance Caught')
            reactionTimeCedrus = -999
        except UnboundLocalError:
            print('No Response')
            reactionTimeCedrus = -999


        if (respkey == [2] and ans == 0) or (respkey == [3] and ans == 1):
            correct = True
        else:
            correct = False
        print(correct)   
        if respkey == -1:
            mlFeed= False
        elif not train:
        ### confidence check
        ### change to ml pick
            keep_going = True
            cedrus_util.reset_timer(ser)    # reset responsebox timer
            keylist = []
            cedrus_util.clear_buffer(ser)

            conftime = False
            confstart = timer.getTime()

            pkrtFrames = int(pkwindow*frameRate)
            kp_prompt.setAutoDraw(True)
            anaRight.setAutoDraw(True)
            for i in range(int(pkwindow*frameRate)):
                totalFrames += 1
                win.flip()
                receiveBuffer = ser.in_waiting
                if receiveBuffer >= 6:
                    keylist.append(ser.read(ser.in_waiting))
                    key, press, time = cedrus_util.readoutput([keylist[-1]], keymap)

                    if press == [1] and key in [[2],[3]]:
                        choice = key
                        conftime = timer.getTime() - confstart ## time to response
                        pkrtFrames = round(conftime * frameRate)
                        win.flip()

                        break
                cedrus_util.clear_buffer(ser)
                
            kp_prompt.setAutoDraw(False)
            anaRight.setAutoDraw(False)
            remainingFrames = int(pkwindow*frameRate - pkrtFrames) # - i
            print(remainingFrames/frameRate)
            for i in range(int(remainingFrames + 0.3*frameRate)):
                win.flip()
            
            
            if not conftime:
                respkey = -1
                choice = -1
            if choice == [2]:
                mlFeed = True
            else:
                mlFeed = False

        else:
            mlFeed = True
        if respkey == [2]:
            respkey = 0
        if respkey == [3]:
            respkey = 1
        totalTime = timer.getTime()-startTime
        totalFrames = round(totalTime*frameRate)        
        data = {'Block': block, 'Trial': trial, 'Stim Type': type, 'Reference Index': trialind, 'Features': all_feats, 'Correct Answer' : ans, 'Response': respkey, 'Correct': correct, 'Model Response': ml_res, 'Model Correct': ml_res == ans, 'Model Confidence': ml_prob, 'Human to ML Response': resp==ml_res, 'Ask ML': mlFeed,'Start Time (ms)': startTime * 1000,'Stim Dur': stimDuration * 1000, 'Reaction Time (ms)':  reactionTime * 1000, 'CEDRUS Reaction Time (ms)': reactionTime, 'Reaction Time (frames)': rtFrames,'Total Time (ms)': totalTime * 1000, 'Total Frames': totalFrames}
        return data, all_feats
    
    

    if type == 'select':
        # show option line

        totalFrames = 0
        startTime = timer.getTime()
        keep_going = True
        cedrus_util.reset_timer(ser)    # reset responsebox timer
        keylist = []
        cedrus_util.clear_buffer(ser)
        
        if not train: ## punish timer for participants if chosen
            screenshot.text = '...'
            screenshot.setAutoDraw(True)
            waitFrameTime = 2.5
            for frame in range(int(waitFrameTime*frameRate)):

                win.flip()
            screenshot.setAutoDraw(False)
        
        line = f'{ml_prob*100:.0f}%'
        if ml_res:
            screenshot.color = 'royalblue'

        else:
            screenshot.color = 'red'

        screenshot.text = line

        screenshot.setAutoDraw(True)
        anaRight.setAutoDraw(True)

        for frame in range(int(.5*frameRate)): # waits 0.5 seconds before next sample
            win.flip()
        screenshot.setAutoDraw(False)
        anaRight.setAutoDraw(False)
        screenshot.color='white'
        for frame in range(int(.3*frameRate)): # waits 0.5 seconds before next sample

            win.flip()
        totalTime = timer.getTime()-startTime
        totalFrames = round(totalTime*frameRate)   

        if ml_res == ans:# or (key == [3] and ans == 1):
            correct = True
        else:
            correct = False
        if train:
            cameraCell.setAutoDraw(False)
            for _ in range(int(0.5*frameRate)):
                win.flip()
    
    
    elif type == 'response':
        if not train and data['Ask ML']: ### if it is not a training session and subject asked for ml to take the question
            print('Picked Model')
            key = data['Model Response']
        else:
            key = data['Response']
        anaLeft.setAutoDraw(True)
        
        # keep_going = True
        startTime = timer.getTime()
        cedrus_util.reset_timer(ser)    # reset responsebox timer
        totalFrames = 0
        
        if (key == 0 and ans == 0) or (key == 1 and ans == 1):
            correct = True
            correctFrameTime = int(0.5 * frameRate)
            if test: #supresss feedback
                fixation.color = 'blue'
            else:
                fixation.color = 'green'

            fixation.setAutoDraw(True)
            anaRight.setAutoDraw(True)
            for frame in range(correctFrameTime): # waits 0.5 seconds before next sample
                win.flip()
            
        elif key == -1:
            if data['Reaction Time (ms)'] > 0:
                penaltywindow -= (pkwindow+.3)
            #print(penaltywindow)
            correct = False
            fixation.color = 'grey'
            incorrectFrameTime = int(penaltywindow * frameRate) - 200 ## using 180 frames to switch pc on and off
            fixation.setAutoDraw(True)
            for _ in range(4): # number of flashes
                anaRight.setAutoDraw(True)
                for _ in range(25):
                    win.flip()
                    anaRight.setAutoDraw(False)
                for _ in range(25):
                    win.flip()
            # print(incorrectFrameTime)
            for frame in range(incorrectFrameTime): # waits 0.5 seconds before next sample
                win.flip()
            # totalFrames += incorrectFrameTime
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
            anaRight.setAutoDraw(True)
            for frame in range(incorrectFrameTime): # waits 0.5 seconds before next sample
                win.flip()
            # totalFrames += incorrectFrameTime
        fixation.setAutoDraw(False)
        anaLeft.setAutoDraw(False)
        anaRight.setAutoDraw(False)
        if not train:
            cameraCell.setAutoDraw(False)
        ## blank screen after trial
        for frame in range(int(.5*frameRate)): # waits .5 second before next trial. The ISI
            win.flip()
        # totalTime = timer.getTime()-startTime
        totalTime = timer.getTime()- data['Start Time (ms)']/1000
        totalFrames = round(totalTime*frameRate) 
        data = data.copy()
        data['Final Correct'] = correct
        data['Final Response'] = key
        # data['Model Response'] = ml_res
        # data['Stim Type'] = type
        # data['Start Time (ms)'] =  startTime * 1000
        data['Total Time (ms)']= totalTime * 1000 
        data['Total Frames']= totalFrames
        print('Total Time of trial:',totalTime,totalFrames)
        return data



def trial(win, ser, keymap, block, trial, frameRate, timer, perm, df1, test=False, start=None,mlFeed =False, thermcamera = False, conn = None, msgCollect = None, msgEndTrial = None,screens=None):
    storeData = []
    repeatedStimuli = True
    feat_lst = []
    options = list(perm[trial])
    suppress = 2 #how many features to start - 1
    ## White fixation for 750 ms
    fixation = screens['fixation']#TextStim(win, text = '+', pos = (0,0))
    # fixation.height = 50
    fixation.height = 85
    fixation.color = 'white'
    waitFrameTime = np.random.uniform(0,.5)

    fixation.setAutoDraw(True)

    inc = df1.iloc[[trial]]['Income'].values[0]

    attr = df1.iloc[[trial]][list(start)]

    trialind = df1.iloc[[trial]]['index'].values[0]
    ml_res = df1.iloc[[trial]]['ML Pred'].values[0]
    ml_prob = df1.iloc[[trial]]['ML Conf'].values[0]


    ## Trial starts
    for frame in range(int(waitFrameTime*frameRate)): # waits ~.25 seconds before turning on camera
        win.flip()
    ## Camera recording start
    screens['cameraCell'].setAutoDraw(True)
    for frame in range(int(1*frameRate)): # waits 1 seconds with camera on
        win.flip()
    fixation.setAutoDraw(False)
        

    ### display first n feats with response window
    data, all_feats = optiongenerate(win, ser, keymap, block = block, trial = trial, frameRate = frameRate, timer = timer, type = 'opt', feat_lst = start, attributes = attr, ans = inc, test = test, ml_res = ml_res,ml_prob = ml_prob, trialind = trialind,train = mlFeed,screens=screens)

    #### pick next feat and response
    if data['Ask ML'] and not mlFeed:
        optiongenerate(win, ser, keymap, block = block, trial = trial, frameRate = frameRate, timer = timer, type = 'select', feat_lst = feat_lst, attributes = attr, ans = inc, test = test, ml_res = ml_res,options = options,all_feats = all_feats,trialind = trialind, ml_prob = ml_prob, data=data, train = mlFeed,screens=screens)

    ### feedback
    data = optiongenerate(win, ser, keymap, block = block, trial = trial, frameRate = frameRate, timer = timer, type = 'response', feat_lst = feat_lst, attributes = attr, ans = inc, test = test, ml_res = ml_res,options = options,all_feats = all_feats,data = data, train = mlFeed,screens=screens)
    repeatedStimuli = False
    storeData.append(data)


    # if thermcamera:
        ## end data collection for trial
        ## set upper right (digital) pc autodraw False
        # screens['cameraCell'].setAutoDraw(False)
        # conn.sendall(msgEndTrial)
        
        # # check that the data has been saved.
        # camdata = conn.recv(1024).decode()
        # while camdata != 'Saved':
        #     camdata = conn.recv(1024).decode()
        # print('Saved')

            
    if mlFeed:
        optiongenerate(win, ser, keymap, block = block, trial = trial, frameRate = frameRate, timer = timer, type = 'select', feat_lst = feat_lst, attributes = attr, ans = inc, test = test, ml_res = ml_res,options = options,all_feats = all_feats,trialind = trialind, ml_prob = ml_prob, data=data, train = mlFeed,screens=screens)
    ## return model correctness if not training and asking ML
    if not mlFeed and data['Ask ML']:
        return data['Model Correct'], storeData

    
    
    return data['Correct'], storeData
