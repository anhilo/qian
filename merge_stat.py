#-*- coding:utf-8 -*-
import os
import re 
import pandas as pd
import numpy as np
from functools import partial

if __name__ == "__main__":
    avail=pd.read_csv('瞬时空号检测/available.txt',header=None)
    avail = pd.DataFrame({'number':avail[0],'dead':0})
    dis=pd.read_csv('瞬时空号检测/disable.txt',header=None)
    dis=pd.DataFrame({'number':dis[0],'dead':1})
    df_tb = pd.concat([avail,dis],ignore_index=True)
    df_tb.rename_axis({'dead':'taobao'},axis=1,inplace=True)

    TAGS = {u'正常号码':'normal',u'关机':'poweroff',u'空号':'dead',u'垃圾号码':'junk',u'来电提醒':'reminder',u'其它':'other',u'请勿来电':'do_not_call',u'停机':'halt',u'呼入限制':'barring',u'无法接通':'not_available'}

    TAGS_AVAIL ={u'正常号码':'normal',u'关机':'poweroff',u'来电提醒':'reminder',u'其它':'other',u'请勿来电':'do_not_call',u'呼入限制':'barring',u'无法接通':'not_available'}


    part = {}
    for filename in os.listdir('瞬时空号检测'):
        for tag,name in TAGS.items():
            if re.search(tag,filename.decode('utf-8')):
                print tag
                try: 
                    if name == "normal":
                        part[tag] = pd.read_csv(os.path.join('瞬时空号检测',filename),skiprows=19,header=None)
                    else:
                        part[tag] = pd.read_csv(os.path.join('瞬时空号检测',filename),skiprows=12,header=None)
                except ValueError:
                    part[tag] = None
    dfs = []
    for tag,df in part.items():
        try:
            if tag in TAGS_AVAIL:
                new_df = pd.DataFrame({'number':df[0],'dead':0})
            else:
                new_df = pd.DataFrame({'number':df[0],'dead':1})
        except TypeError:
            pass
        else:
            dfs.append(new_df)
            
    df_mf = reduce(lambda x,y: pd.concat([x,y],ignore_index=True),dfs)
    df_mf.rename_axis({'dead':'mofang'},axis=1,inplace=True)

    dfs = []
    for filename in os.listdir('blacklist'):
        df = pd.read_csv(os.path.join('blacklist',filename),header=None)
        if re.search("不可用",filename):
            dfs.append(pd.DataFrame({'number':df[0],'dead':1}))
        else:
            dfs.append(pd.DataFrame({'number':df[0],'dead':0}))
    df_black = reduce(lambda x,y: pd.concat([x,y],ignore_index=True),dfs)
    df_black = df_black.groupby('number')['dead'].mean().reset_index()
    df_black.rename_axis({'dead':'blacklist'},axis=1,inplace=True)

    result = reduce(partial(pd.merge,on="number",how='outer'),[df_black,df_tb,df_mf])
    print result.describe()





