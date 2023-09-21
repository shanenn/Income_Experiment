'''Makes new csvs according to split and accuracy'''
import pickle
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import RepeatedStratifiedKFold
import pandas as pd
import numpy as np
from itertools import combinations, permutations
import os

# subject = int(input('Enter Subject Number: '))
def subject_csv_read(subject,split):
    np.random.seed(subject)
    currentPath = os.getcwd()
    dirpath = os.path.join(currentPath, '../data/Subject' +str(subject))

    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)
        
    ## Check Session 1-2 dfs
    df_list = ['trial_435_7030.csv','train_100_7030.csv','select_168_7030.csv']
    for fn in df_list:
        fp = f'../inc_csvs/{fn}'
        df = pd.read_csv(fp)
        df = df.sample(frac=1).reset_index(drop=False)
        df2 = df.copy()
        subdf = os.path.join(os.getcwd(), '../data/' + 'Subject' + str(subject)+ '/' +'subject'+str(subject)+'_'+fn)
        try: ###check for shuffled df for the model to run through eventually
            pd.read_csv(subdf)
            print(f'{subject} {fn} already exists')
        except FileNotFoundError:
            df2.to_csv(subdf,index=False)
        print('Matches:',(pd.read_csv(subdf)['index'] == df2['index']).all())
        if fn == df_list[0]:
            subdf = os.path.join(os.getcwd(), '../data/' + 'Subject' + str(subject)+ '/' +str(subject)+'_datashuffle.csv')
            try: ###check for shuffled df for the model to run through eventually
                pd.read_csv(subdf)
                print(f'{subject}_datashuffle.csv already exists')
            except FileNotFoundError:
                df2.to_csv(subdf,index=False)
            print('Matches:',(pd.read_csv(subdf)['index'] == df2['index']).all())
            
        
    ## Check Session 1-2 dfs
    df_list = [f'{i}{split}.csv' for i in ['Train_','Prac1_','Prac2_']]
    # df_list = ['Train_8020.csv','Prac1_8020.csv','Prac2_8020.csv']
    start = list(combinations(['Workclass','Highest Degree','Marital Status','Race','Gender','Occupation','Hours per Week','Age'],3))#,'Years of Education'],3)) 
    np.random.shuffle(start)    
    for fn in df_list:
        preds = []
        confs = []
        fp = f'../inc_csvs/{fn}'
        df = pd.read_csv(fp)
        df = df.sample(frac=1).reset_index(drop=False)
        df2 = df.copy()
        # print(df.head())
        if len(start) < len(df):
            start = start * int(np.ceil((len(df)/len(start))))
        for ind,row in df.iterrows():
            combo = sorted(start[ind])
            row = pd.DataFrame(row[list(combo)]).T
            with open('../model_work/models/'+'_'.join(combo)+'.pkl', 'rb') as f:
                model = pickle.load(f)
            # print('./py_models/'+'_'.join(combo)+'_model.pkl')
            ml_res = model.predict(row)[0]
            ml_prob = model.predict_proba(row)[0][ml_res]
            # print(ml_res,ml_prob)
            preds.append(ml_res)
            confs.append(ml_prob)
        df2['ML Pred'] = preds
        df2['ML Conf'] = confs
        print((preds==df2['Income']).sum()/len(df2))
        subdf = os.path.join(os.getcwd(), '../data/' + 'Subject' + str(subject)+ '/' +'subject'+str(subject)+'_'+fn)
        try: ###check for shuffled df for the model to run through eventually
            pd.read_csv(subdf)
            print(f'{subject} {fn} already exists')
        except FileNotFoundError:
            df2.to_csv(subdf,index=False)
        print('Matches:',(pd.read_csv(subdf)['index'] == df2['index']).all())
        # print(pd.read_csv(subdf)['index'],df2['index'])

def full_model_csv_read(subject,split):
    np.random.seed(subject)
    currentPath = os.getcwd()
    dirpath = os.path.join(currentPath, '../data/Subject' +str(subject))

    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)
        
    # ## Check Session 1-2 dfs
    # df_list = ['trial_435_7030.csv','train_45_7030.csv','select_168_7030.csv']
    # for fn in df_list:
    #     df = pd.read_csv(fn)
    #     df = df.sample(frac=1).reset_index(drop=False)
    #     df2 = df.copy()
    #     subdf = os.path.join(os.getcwd(), 'data/' + 'Subject' + str(subject)+ '/' +'subject'+str(subject)+'_'+fn)
    #     try: ###check for shuffled df for the model to run through eventually
    #         pd.read_csv(subdf)
    #         print(f'{subject} {fn} already exists')
    #     except FileNotFoundError:
    #         df2.to_csv(subdf,index=False)
    #     print('Matches:',(pd.read_csv(subdf)['index'] == df2['index']).all())
    #     if fn == df_list[0]:
    #         with open('./py_models/'+'fullmodel.pkl', 'rb') as f:
    #             model = pickle.load(f)
    #         x = 
    #         subdf = os.path.join(os.getcwd(), 'data/' + 'Subject' + str(subject)+ '/' +str(subject)+'_datashuffle.csv')
    #         try: ###check for shuffled df for the model to run through eventually
    #             pd.read_csv(subdf)
    #             print(f'{subject}_datashuffle.csv already exists')
    #         except FileNotFoundError:
    #             df2.to_csv(subdf,index=False)
    #         print('Matches:',(pd.read_csv(subdf)['index'] == df2['index']).all())
            
    ## Check Session 1-2 dfs
    attributes = ['Workclass','Highest Degree','Marital Status','Race','Gender','Occupation','Hours per Week','Age','Native Country']
    # df_list = ['Train_8020.csv','Prac1_8020.csv','Prac2_8020.csv']
    df_list = [f'{i}{split}.csv' for i in ['Train_','Prac1_','Prac2_']]
    start = list(combinations(['Workclass','Highest Degree','Marital Status','Race','Gender','Occupation','Hours per Week','Age'],3))#,'Years of Education'],3)) 
    np.random.shuffle(start)    
    for fn in df_list:
        preds = []
        confs = []
        fp = f'../inc_csvs/{fn}'
        df = pd.read_csv(fp)
        df = df.sample(frac=1).reset_index(drop=False)
        df2 = df.copy()
        # print(df.head())
        if len(start) < len(df):
            start = start * int(np.ceil((len(df)/len(start))))
        for ind,row in df.iterrows():
            combo = sorted(start[ind])
            # row = pd.DataFrame(row[list(combo)]).T
            row = pd.DataFrame(row[attributes]).T
            for i in [i for i in attributes if i not in combo]:
                if i in ['Hours per Week','Age']:
                    row[i] = np.nan
                else:
                    row[i] = ''
            # row = pd.DataFrame(row.drop(['Income','Income Adjust','income-actual','ML Pred','ML Conf'])).T
            # print(row)
            with open('../model_work/models/'+'fullmodel.pkl', 'rb') as f:
                model = pickle.load(f)
            ml_res = model.predict(row)[0]
            ml_prob = model.predict_proba(row)[0][int(ml_res)]
            preds.append(int(ml_res))
            confs.append(ml_prob)
        df2['ML Pred'] = preds
        df2['ML Conf'] = confs
        print((preds==df2['Income']).sum()/len(df2))
        subdf = os.path.join(os.getcwd(), '../data/' + 'Subject' + str(subject)+ '/' +'subject'+str(subject)+'_fullmodel_'+fn)
        try: ###check for shuffled df for the model to run through eventually
            pd.read_csv(subdf)
            print(f'Full Model {subject} {fn} already exists')
        except FileNotFoundError:
            df2.to_csv(subdf,index=False)
        print('Matches:',(pd.read_csv(subdf)['index'] == df2['index']).all())
if __name__=="__main__":
    sub = 218
    split = 7525
    print(f'Testing with subject {sub}')
    subject_csv_read(sub)
    full_model_csv_read(sub)