
from Kdata import get_date,API
import requests
import pandas as pd
import polars as pl
import os,sys,time

from Klang import (
    OPEN, O,
    HIGH, H,
    LOW, L,
    CLOSE, C,
    VOLUME, V, VOL,
    DATETIME,

    SMA,MA,EMA,WMA,

    SUM,ABS,STD,

    CROSS,
    REF,BARSLAST,BARSCOUNT,BARSLASTFIND,
    MAX,
    MIN,
    EVERY,
    COUNT,
    HHV,
    LLV,
    IF, IIF,
    MACD,APPROX)

#### backtest #####
import btr
####


end = get_date(0)
kapi = API() #klang data api

#
#  初始化股票列表
#
stocklist = kapi.get_stocklist().json()
stockindex = {}

i = 0 
for stock in stocklist:
    stockindex[stock['code']] = i
    i += 1

def getname(code):
    return stocklist[stockindex[code]]['name']



#
# tdxgn A类因子适合产生股票列表
#
def get_gn(gnname):
    data = kapi.get_factor('tdxgn',date=end).json()

    df1 = pl.DataFrame(data)
    df1 = df1.select([
    'factorname',
    'code',
    'value',
    'date'
    ])

    df1 = df1.filter(
        pl.col("value").str.contains(gnname)
    )


    codelist = df1['code'].to_list()
    return codelist 


def parseValue(data,n):

    result = data.split(",")
    if len(result) <= n :
        return 0
    try:   
        return float(result[n])
    except:
        return 0


sourcecode =\
"""
codelist = get_gn('光伏')
#
# MACD B类因子，适合产生数据和算法加工
# data = diff,dea,macd,金叉,死叉
#

#
# 获取macd因子，分析金叉，死叉数据
#
df_macd = None
def strategy(code):
    global df_macd
    data = kapi.get_factor('macd',date=end,code=code,limit=200).json()

    df_macd = pl.DataFrame(data)
    df_macd = df_macd.with_columns([
        pl.col("macd").apply(lambda data: parseValue(data,3)).alias('buy'),
        pl.col("macd").apply(lambda data: parseValue(data,4)).alias('sell')
    ])
   
def buy_flag(dt):
    retdf = df_macd[df_macd['date'] == dt]
    if len(retdf) < 1:
        return 0
    return retdf.buy[0] == 1
    
def sell_flag(dt):
    retdf = df_macd[df_macd['date'] == dt]
    if len(retdf) < 1:
        return 0
    return retdf.sell[0] == 1
"""




def execute(sourcecode,msg,Kl):
    if 'import' in sourcecode: #禁止用户导入模块
        print('禁止使用import')
        return

    """
    禁止使用系统函数
    """
    close = open = system = None;

    ecode = compile(sourcecode,"",'exec')
    exec(ecode,globals())
    

    btr.set_buy_sell(buy_flag,sell_flag)
    btr.setmsg(msg)

    msg({"flag":"stocklength","value":len(codelist)})

    for code in codelist:

        Kl.code(code)   
        print(code,getname(code))

        msg({"flag":"info","code":code,"name":getname(code)})
        df = Kl.currentdf['df'] 
    
        strategy(code)
    
        btr.init_btr(df)
    
    time.sleep(2) #等待2秒发送完成
    if sys.platform == 'linux' or sys.platform =='linux2':
        os._exit(0)

if __name__ == '__main__':
    #### Klang #####
    # 
    from Klang import Kl,Klang
    Klang.Klang_init(); #加载所有股票列表
    ####
   
    execute(sourcecode,lambda x:x,Kl)
