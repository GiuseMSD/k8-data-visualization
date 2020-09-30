import requests
import pandas as pd 
import json
import os
from pandas.io.json import json_normalize #package for flattening json in pandas df
import flatjson

import warnings
warnings.filterwarnings('ignore')



def show_table():
    jtoken                = os.getenv('GITHUB_TOKEN', '')
    ztoken                = ''
    url                   = f"https://api.github.com/repositories/292545304/issues"
    urlz                  = 'https://api.zenhub.io/p1/repositories/292545304/board'
    headers               = {'Authorization': f'token {jtoken}'}
    r                     = requests.get(url, headers=headers, params={'state': 'all'}).json()
    data                  = json_normalize(r, max_level=1)
    dfn                   = pd.DataFrame.from_dict(data)
    dfn1                  = dfn[['created_at', 'state','closed_at','user.login','author_association','title','body', 'number', 'assignee.login']]
    dfn                   = dfn[['state', 'number', 'assignee.login']]
    
    headersz              = {'X-Authentication-Token': ztoken, }
    rz                    = requests.get(urlz, headers=headersz).json()
    dataz                 = flatjson.dumps(rz)
    data1                 = json_normalize(dataz)
    df                    = pd.DataFrame.from_dict(data1)
    df                    = df.loc[:, ~df.columns.str.endswith('id')]
    df                    = df.loc[:, ~df.columns.str.endswith('is_epic')]
    df                    = df.loc[:, ~df.columns.str.endswith('position')]
    
    new                   = df[df.columns[pd.Series(df.columns).str.startswith('pipelines[0]')]]
    new                   = new.transpose() 
    new.columns           = new.iloc[0]
    new                   = new[1:]
    new                   = new.rename({'New Issues':'number'}, axis=1)
    new['New Issues']     = 'New Issues'
    
    bak                   = df[df.columns[pd.Series(df.columns).str.startswith('pipelines[1]')]]
    bak                   = bak.transpose() 
    bak.columns           = bak.iloc[0]
    bak                   = bak[1:]
    bak                   = bak.rename({'Backlog':'number'}, axis=1)
    bak['Backlog']        = 'Backlog'
    
    prog                  = df[df.columns[pd.Series(df.columns).str.startswith('pipelines[2]')]]
    prog                  = prog.transpose() 
    prog.columns          = prog.iloc[0]
    prog                  = prog[1:]
    prog                  = prog.rename({'In Progress':'number'}, axis=1)
    prog['In Progress']   = 'In Progress'
    
    peer                  = df[df.columns[pd.Series(df.columns).str.startswith('pipelines[3]')]]
    peer                  = peer.transpose() 
    peer.columns          = peer.iloc[0]
    peer                  = peer[1:]
    peer                  = peer.rename({'Peer Review':'number'}, axis=1)
    peer['Peer Review']   = 'Peer Review'
    
    gw                    = df[df.columns[pd.Series(df.columns).str.startswith('pipelines[4]')]]
    gw                    = gw.transpose() 
    gw.columns            = gw.iloc[0]
    gw                    = gw[1:]
    gw                    = gw.rename({'GW Team Review':'number'}, axis=1)
    gw['GW Team Review']  = 'GW Team Review'
    
    dfv                   = pd.concat([new, bak, prog, peer, gw])
    df_merge              = pd.merge(dfn, dfv, on='number')
    df_merge              = df_merge.rename({'assignee.login':'Assigned'}, axis=1)
    df_merge              = df_merge.rename({'state':'Status'}, axis=1)
    df_merge              = df_merge.rename({'number':'Total'}, axis=1)
    
    table                 = df_merge.groupby(['Assigned', 'Status']).count()
    
    return table
    
            