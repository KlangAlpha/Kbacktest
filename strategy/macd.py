import os, sys

p = os.path.abspath('.')
sys.path.insert(1, p)

from backtest import execute


#
# MACD 金叉，死叉买卖法
# 


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



if __name__ == '__main__':
    #### Klang #####
    # 
    from Klang import Kl,Klang
    Klang.Klang_init(); #加载所有股票列表
    ####
   
    execute(sourcecode,lambda x:x,Kl)
