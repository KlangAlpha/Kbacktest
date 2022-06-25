import os, sys

p = os.path.abspath('.')
sys.path.insert(1, p)

from backtest import execute


#
# 倍量柱买入法
# 买入条件：1. 当天量是前10天 均线的 2.0 倍。2. 当日收盘价在120日均线之上
# 卖出条件：1. 跌破10日均线


sourcecode =\
"""
codelist = get_gn('光伏')
#
# volr 倍量柱
# vr10,vr20,vr30 
#
# ma5,ma10,ma20,ma30,ma60,ma120,ma250


df_volr = None
df_ma = None
def strategy(code):
    global df_volr,df_ma
    data = kapi.get_factor('volr',date=end,code=code,limit=200).json()
    data1 = kapi.get_factor('ma',date=end,code=code,limit=200).json()
    df_ma = pl.DataFrame(data1)
    df_volr = pl.DataFrame(data)
    
    # 0 是取10日量柱做对比
    df_volr = df_volr.with_columns([
        pl.col("volr").apply(lambda data: parseValue(data,0)).alias('buy'),
    ])

    # 0是 10日均线，就是半月线
    # 5是 120日均线，也就是半年线
    df_ma = df_ma.with_columns([
        pl.col('ma').apply(lambda data: parseValue(data,5)).alias('buy'),
        pl.col('ma').apply(lambda data: parseValue(data,0)).alias('sell'),
    ])
   
def buy_flag(dt):
    retdf = df_volr[df_volr['date'] == dt]
    retdf1 = df_ma[df_ma['date'] == dt] 

    c0 = C[str(dt)] 
    o0 = O[str(dt)]
 
    if len(retdf) < 1 or len(retdf1) < 1:
        return 0
    # 倍量柱 2倍,并且当天为阳线
    return retdf1.buy[0] < c0 and retdf.buy[0] > 2.0 and c0 > o0
    
def sell_flag(dt):
    retdf = df_ma[df_ma['date'] == dt]
    if len(retdf) < 1:
        return 0
    c0 = C[str(dt)] 
    # 跌破10日均线卖出    
    return retdf.sell[0] > c0
"""



if __name__ == '__main__':
    #### Klang #####
    # 
    from Klang import Kl,Klang
    Klang.Klang_init(); #加载所有股票列表
    ####
   
    execute(sourcecode,lambda x:x,Kl)
