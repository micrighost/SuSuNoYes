def webcrawler(stock_symbol):
    """傳入股票代號回傳資料表"""
    # 設定目標股票的代號
    stock_symbol

    # 引入requests庫
    import requests
    # 定義API的URL
    url = 'https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_' + str(stock_symbol) + '.tw'
    # 發送GET請求
    res = requests.get(url)
    res

    # 用json解析出資料
    import json

    jsondata = json.loads(res.text)
    jsondata

    # 提取股票相關資訊
    jsondata['msgArray']

    # 引入pandas庫
    import pandas as pd
    # 將JSON數據轉換為DataFrame
    df = pd.DataFrame(jsondata['msgArray'])
    # 將空字符串替換為'0'
    df.replace('', '0', inplace=True) # inplace=True 不建立新的對象，直接對原始對象進行修改

    # 顯示DataFrame
    df

    # 用直的觀察DataFrame
    # print(df.T)

    # 選取有價值的代號
    df = pd.DataFrame(df, columns=['a','b','c','d','f','g','ot','o','h','l','n','ex','t','u','v','w','nf','y','tv','z'])
    df

    # 將英文代號轉換成中文
    df = df.rename(columns={
                'a': '五檔賣價(從低到高，以_分隔資料)',
                'b': '五檔買價(從高到低，以_分隔資料)',
                'c': '股票代號',
                'd': '最近交易日(YYYYMMDD)',
                'f': '五檔賣量(從低到高，以_分隔資料)',
                'g': '五檔買量(從高到低，以_分隔資料)',
                'ot': '最近成交時刻(HH:MM:SS)',
                'o': '開盤',
                'h': '最高',
                'l': '最低',
                'n': '公司簡稱',
                'ex': '上市或上櫃 (tse / otc)',
                't': '撮合時間',
                'u': '漲停價',
                'v': '累積成交量',
                'w': '跌停價',
                'nf': '公司全名',
                'y': '昨收價',
                'tv': '當盤成交量',
                'z': '當盤成交價'
                        })
    # print(df.T)

    # 將股票代號設為索引
    df.set_index("股票代號" , inplace=True)

    # print(df.T)

    # 轉換類型為string
    df = df.astype("string")

    # 查看類型
    df.dtypes


    # 如果沒有當盤成交價，就使用五檔買價的最高價
    if df['當盤成交價'].iloc[0] == '-' :
        # 抓取df['五檔買價(從高到低，以_分隔資料)']的第一個值，分割後取第一個
        df['當盤成交價'] = df['五檔買價(從高到低，以_分隔資料)'][0].split('_')[0]

    # 用直的觀察DataFrame
    # print(df.T)

    # 回傳資料表
    return df




def webcrawler_true(stock_symbol):
    """傳入股票代號，回傳是否有抓到資料"""

    # 設定目標股票的代號
    stock_symbol

    # 引入requests庫
    import requests
    # 定義API的URL
    url = 'https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_' + str(stock_symbol) + '.tw'
    # 發送GET請求
    res = requests.get(url)
    res

    # 用json解析出資料
    import json

    jsondata = json.loads(res.text)
    jsondata

    # 提取股票相關資訊
    jsondata['msgArray']

    # 如果股票代號(c)的位置有數字，就判定為有抓到
    if jsondata['msgArray'][0]['c'].isdigit() and len(jsondata['msgArray'][0]['c']) == 4:
      return True
    else:
      return False





