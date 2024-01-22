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
# import pickle
# from sklearn.model_selection import cross_val_predict
# from sklearn.model_selection import RepeatedStratifiedKFold


def trialvalues():
    blocks = 4
    trials = 75
    numCorr = 200
    return trials,blocks,numCorr

def trainvalues():
    blocks = 2
    trials = 60
    return trials,blocks


def optionchoose(key,options,featind):
    print(featind)
    if key in [[4],[6]]:
        featind -= 1
    elif key in [[5],[-1]]:
        featind += 1
    else:
        print('error')
        return featind
    if featind == len(options):
        return 0
    if featind < 0:
        return len(options)-1
    return featind
    
def optiongenerate(win, ser, keymap, block, trial, frameRate, timer, feat_lst, attributes,all_feats=None, type = 'opt', ans = None, test = False, ml_res = None,options = None, data=None,trialind = None, ml_prob = None, train = False,screens = None):
    
    # screens = {'featlight':
    featlight= screens['featlight']
    resp=screens['resp']
    mask=screens['mask']
    screenshot=screens['screenshot']
    kp_prompt=screens['kp_prompt']
    firstlight=screens['firstlight']
    pcell2=screens['pcell2']
    fixation = screens['fixation']

    responsewindow = 1 # second to respond in test
    pkwindow = 2.5 # second to respond pk
    penaltywindow = 6.6

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
            #stim.append(line)
            #screenshot.text = '\n\n\n'.join(stim)
            screenshot.text = line
            # screenshot.pos = (0,0)
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
        resp.setAutoDraw(True)
        stimDuration = timer.getTime() - startTime
        cedrus_util.reset_timer(ser)    # reset responsebox timer
        keylist = []
        cedrus_util.clear_buffer(ser)
        reactionTime = False
        rtFrames = int(responsewindow*frameRate)
        # keep_going = True
        # while keep_going: # 0(n)
        for i in range(int(responsewindow*frameRate)): # 2 sec response window?
        #rtFrames += 1
            win.flip()
            receiveBuffer = ser.in_waiting
            # print(receiveBuffer)
            if receiveBuffer >= 6:
                # print(receiveBuffer)
                keylist.append(ser.read(ser.in_waiting))
                key, press, time = cedrus_util.readoutput([keylist[-1]], keymap)
                if press == [1] and (key == [2] or key == [3]):
                    #keep_going = False
                    reactionTimer = timer.getTime()
                    reactionTime = reactionTimer - stimDuration - startTime
                    rtFrames = round(reactionTime * frameRate)
                    # cedrus_util.clear_buffer(ser)
                    # break
                    respkey = key
                    break
                    # firstlight.setAutoDraw(False)
                    

                    # keep_going = False
            cedrus_util.clear_buffer(ser)
        resp.setAutoDraw(False)
        screenshot.setAutoDraw(False)
        remainingFrames = int(responsewindow*frameRate - rtFrames)
        print(remainingFrames/frameRate)
        if train:
            remainingFrames = 0
        for i in range(int(remainingFrames + 0.3*frameRate)):
            win.flip()
        if int(remainingFrames + 0.3*frameRate) != 78:
            print('Calculated time',int(remainingFrames + 0.3*frameRate + rtFrames))
        # for i in range(int()):
        #     win.flip()
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

            
        #endTime = reactionTime
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
            print('start loop')
            # confind = 4 ## mid point?
            # confarray = np.arange(10) + 1
            # screenshot.text = str("Pass")
            # screenshot.height = 75
            # screenshot.pos = (-150,0)
            # screenshot.color = 'red'
            # screenshot2.text = str("Keep")
            # screenshot2.height = 75
            # screenshot2.pos = (150,0)
            # screenshot2.color = 'royalblue'
            conftime = False
            confstart = timer.getTime()
            # while keep_going:
            pkrtFrames = int(pkwindow*frameRate)
            for i in range(int(pkwindow*frameRate)):
                totalFrames += 1
                win.flip()
                # screenshot.setAutoDraw(True)
                # screenshot2.setAutoDraw(True)
                kp_prompt.setAutoDraw(True)
                # keylist.append(ser.read(ser.in_waiting))
                receiveBuffer = ser.in_waiting
                if receiveBuffer >= 6:
                    keylist.append(ser.read(ser.in_waiting))
                    key, press, time = cedrus_util.readoutput([keylist[-1]], keymap)

                    if press == [1] and key in [[2],[3]]:
                        # screenshot.setAutoDraw(False)
                        # screenshot2.setAutoDraw(False)
                        choice = key
                        conftime = timer.getTime() - confstart ## time to response
                        pkrtFrames = round(conftime * frameRate)
                        win.flip()
                        # feat = options[featind]
                        # print(attributes)
                        # keep_going = False
                        break
                cedrus_util.clear_buffer(ser)
                
            kp_prompt.setAutoDraw(False)
            remainingFrames = int(pkwindow*frameRate - pkrtFrames)
            print(remainingFrames/frameRate)
            for i in range(int(remainingFrames + 0.3*frameRate)):
                win.flip()
            if int(remainingFrames + 0.3*frameRate) != 168:
                print('Calculated time',int(remainingFrames + 0.3*frameRate + pkrtFrames))
            
            
            if not conftime:
                # reactionTime = -.999
                # rtFrames = round(reactionTime * frameRate)
                # reactionTimer = timer.getTime()
                # penaltywindow -= 1.2
                respkey = -1
                choice = -1
            # print(respkey)


            if choice == [2]:
                mlFeed = True
            
            else:# if choice == [3]:
                mlFeed = False
                # for i in range(int(0.3*frameRate)):
                #     win.flip()
        else:
            mlFeed = True
        if respkey == [2]:
            respkey = 0
        if respkey == [3]:
            respkey = 1
            #rtFrames = totalFrames
        totalTime = timer.getTime()-startTime
        totalFrames = round(totalTime*frameRate)        
        data = {'Block': block, 'Trial': trial, 'Stim Type': type, 'Reference Index': trialind, 'Features': all_feats, 'Correct Answer' : ans, 'Response': respkey, 'Correct': correct, 'Model Response': ml_res, 'Model Correct': ml_res == ans, 'Model Confidence': ml_prob, 'Human to ML Response': resp==ml_res, 'Ask ML': mlFeed,'Start Time (ms)': startTime * 1000,'Stim Dur': stimDuration * 1000, 'Reaction Time (ms)':  reactionTime * 1000, 'CEDRUS Reaction Time (ms)': reactionTime, 'Reaction Time (frames)': rtFrames,'Total Time (ms)': totalTime * 1000, 'Total Frames': totalFrames}
        return data, all_feats
    
    

    if type == 'select':
        # show option line

        totalFrames = 0
        startTime = timer.getTime()
        # featind = 0

        # pcell[0].draw()
        # pcell[1].draw()
        keep_going = True
        cedrus_util.reset_timer(ser)    # reset responsebox timer
        keylist = []
        cedrus_util.clear_buffer(ser)
        
        if not train: ## punish timer for participants if chosen
            screenshot.text = '...'
            screenshot.setAutoDraw(True)
            # waitFrameTime = np.random.uniform(2,3)
            waitFrameTime = 2.5
            for frame in range(int(waitFrameTime*frameRate)):
                # screenshot.draw()
                win.flip()
            screenshot.setAutoDraw(False)
        
        # mlresp = pred
        # mlconf = prob
        
        line = f'{ml_prob*100:.0f}%'
        if ml_res:
            # line = f'>$50,000 ({mlconf*100:.0f}%)' 
            screenshot.color = 'royalblue'
            # all_feats[feat] = attributes[feat].values[0]
        else:
            # line = f'<$50,000 ({mlconf*100:.0f}%)'
            screenshot.color = 'red'
        #stim.append(line)
        #screenshot.text = '\n\n\n'.join(stim)
        screenshot.text = line
        # screenshot.pos = (0,0)
        screenshot.setAutoDraw(True)

        featlight.draw()
        #print(timer.getTime())############
        for frame in range(int(.5*frameRate)): # waits 0.5 seconds before next sample
            #print(screenshot.color)
            win.flip()
        screenshot.setAutoDraw(False)
        screenshot.color='white'
        for frame in range(int(.3*frameRate)): # waits 0.5 seconds before next sample
            #print(screenshot.color)
            win.flip()
        totalTime = timer.getTime()-startTime
        totalFrames = round(totalTime*frameRate)   

        if ml_res == ans:# or (key == [3] and ans == 1):
            correct = True
        else:
            correct = False
        # data = data.copy()
        # # if not train: ## should reference passed variable mlFeed, which is unchanged vs response of pass vs keep
        # data['Start Time (ms)'] =  startTime * 1000
        # data['Total Time (ms)']= totalTime * 1000
        # data['Total Frames']= totalFrames
        # data['Stim Type'] = type

        # return data

    
    
    elif type == 'response':
        if not train and data['Ask ML']: ### if it is not a training session and subject asked for ml to take the question
            print('Picked Model')
            key = data['Model Response']
        else:
            key = data['Response']
        # fixation.height = 50
        # photocell1 = visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(-930, -230))
        pcell2.setAutoDraw(True)
        
        # keep_going = True
        startTime = timer.getTime()
        cedrus_util.reset_timer(ser)    # reset responsebox timer
        totalFrames = 0
        print('='*20)
        print(key,ans)
        # if train:
        #     if ans:
        #         fixation.text = '> $50k'
        #     else:
        #         fixation.text = '< $50k'
        
        if (key == 0 and ans == 0) or (key == 1 and ans == 1):
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
            # totalFrames += correctFrameTime
        elif key == -1:
            if data['Reaction Time (ms)'] > 0:
                penaltywindow -= (pkwindow+.3)
            correct = False
            fixation.color = 'grey'
            incorrectFrameTime = int(penaltywindow * frameRate)
            fixation.setAutoDraw(True)
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
            for frame in range(incorrectFrameTime): # waits 0.5 seconds before next sample
                win.flip()
            # totalFrames += incorrectFrameTime
        fixation.setAutoDraw(False)
        pcell2.setAutoDraw(False)
        for frame in range(int(0.5*frameRate)): # waits .5 second before next trial. The ISI
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
    for frame in range(int(0.5*frameRate)): # waits .5 second before next trial. The ISI
        win.flip()
    storeData = []
    repeatedStimuli = True
    # totalStimuliDisplay = 0
    feat_lst = []
    options = list(perm[trial])
    #print(df1.iloc[[trial]]) 
    suppress = 2 #how many features to start - 1
    ## White fixation for 750 ms
    fixation = screens['fixation']#TextStim(win, text = '+', pos = (0,0))
    fixation.height = 50
    fixation.color = 'white'
    waitFrameTime = np.random.uniform(0,.5)
    # waitFrameTime = 0.75
    fixation.setAutoDraw(True)
    
    for frame in range(int(waitFrameTime*frameRate)): # waits .75 seconds before next trial
        win.flip()
    if thermcamera:
        msg = f'{msgCollect} {block} {trial}'
    	#print('MESASAGE',msg)
        msgCollectLabel = bytes(msg, 'utf-8')

		# send message to thermal camera for block 
        conn.sendall(msgCollectLabel)
        
    camStart = timer.getTime()
    for frame in range(int(.5*frameRate)): # waits .5 seconds before next trial with camera on
        win.flip()
    fixation.setAutoDraw(False)
    
    inc = df1.iloc[[trial]]['Income'].values[0]
    attr = df1.iloc[[trial]][list(start)]
    trialind = df1.iloc[[trial]]['index'].values[0]
    ml_res = df1.iloc[[trial]]['ML Pred'].values[0]
    ml_prob = df1.iloc[[trial]]['ML Conf'].values[0]

    
    

    ### display first n feats with response window
    data, all_feats = optiongenerate(win, ser, keymap, block = block, trial = trial, frameRate = frameRate, timer = timer, type = 'opt', feat_lst = start, attributes = attr, ans = inc, test = test, ml_res = ml_res,ml_prob = ml_prob, trialind = trialind,train = mlFeed,screens=screens)

    #### pick next feat and response
    if data['Ask ML'] and not mlFeed:
        optiongenerate(win, ser, keymap, block = block, trial = trial, frameRate = frameRate, timer = timer, type = 'select', feat_lst = feat_lst, attributes = attr, ans = inc, test = test, ml_res = ml_res,options = options,all_feats = all_feats,trialind = trialind, ml_prob = ml_prob, data=data, train = mlFeed,screens=screens)

    ### feedback
    data = optiongenerate(win, ser, keymap, block = block, trial = trial, frameRate = frameRate, timer = timer, type = 'response', feat_lst = feat_lst, attributes = attr, ans = inc, test = test, ml_res = ml_res,options = options,all_feats = all_feats,data = data, train = mlFeed,screens=screens)
    repeatedStimuli = False
    storeData.append(data)

    print('Recording Time',timer.getTime() - camStart)
    if thermcamera:
        conn.sendall(msgEndTrial)
        
        # check that the data has been saved.
        camdata = conn.recv(1024).decode()
        while camdata != 'Saved':
            camdata = conn.recv(1024).decode()
        print('Saved')

            
    if mlFeed:
        optiongenerate(win, ser, keymap, block = block, trial = trial, frameRate = frameRate, timer = timer, type = 'select', feat_lst = feat_lst, attributes = attr, ans = inc, test = test, ml_res = ml_res,options = options,all_feats = all_feats,trialind = trialind, ml_prob = ml_prob, data=data, train = mlFeed,screens=screens)
    ## return model correctness if not training and asking ML
    if not mlFeed and data['Ask ML']:
        return data['Model Correct'], storeData
    # waitFrameTime = np.random.uniform(.5,1)
    # for frame in range(int(waitFrameTime*frameRate)): # waits .5-1 second before next trial. The ISI
    #     win.flip()
    # screenshot.color = 'white'
    
    
    return data['Correct'], storeData
