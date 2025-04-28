import psycopg2
import pandas as pd
import numpy as np

import os
from dotenv import load_dotenv
# 加載 .env 文件中的環境變數
load_dotenv()


def fetch_stock_data(ticker):
    """根據股票代碼從 PostgreSQL 資料庫中獲取股票數據。

    參數:
    ticker (str): 股票代碼，例如 '2330.TW'

    返回:
    pd.DataFrame: 包含股票數據open、high、low、close、volume、price_change_percent、status的 DataFrame
    """
    try:
        # 連接到 PostgreSQL 資料庫
        conn = psycopg2.connect(
            dbname = os.getenv('DB_NAME'), # 資料庫名稱
            user = os.getenv('DB_USER'), # 使用者名稱
            password = os.getenv('DB_PASSWORD'), # 密碼
            host = os.getenv('DB_HOST'), # 主機地址
            port = os.getenv('DB_PORT') # 端口號
        )

        # 創建一個游標對象
        cur = conn.cursor()

        # 定義查詢語句
        query = "SELECT * FROM stock_data WHERE ticker = %s;"

        # 執行查詢
        cur.execute(query, (ticker,))

        # 獲取查詢結果
        rows = cur.fetchall()

        # 獲取欄位名稱
        colnames = [desc[0] for desc in cur.description]

        # 將結果轉換為 Pandas DataFrame
        df = pd.DataFrame(rows, columns=colnames)

        # 計算隔天漲跌幅，隔天開盤價減去今天的收盤價
        # 最後一天沒有隔天開盤價，所以直接用今天的收盤價相減，讓值等於0
        price_change = df['open'].shift(-1).fillna(df['close'])

        # 計算漲跌幅的百分比
        price_change_percent = (price_change - df['close']) / df['close']

        # 新增欄位price_change_percent
        df['price_change_percent'] = price_change_percent

        
        # 根據漲跌幅設置狀態
        conditions = [
            (price_change_percent > 0.03),  # 漲幅大於3%，設為 1
            (price_change_percent > 0) & (price_change_percent <= 0.03),  # 漲幅大於0%且小於等於3%，設為 2
            (price_change_percent < 0) & (price_change_percent >= -0.03),  # 跌幅大於0%且小於等於-3%，設為 3
            (price_change_percent < -0.03)  # 跌幅大於-3%，設為 4
        ]
        choices = [1, 2, 3, 4]  # 對應的狀態值 

        # 使用 np.select 根據條件設置狀態
        df['status'] = np.select(conditions, choices, default=0)  # default=0 可選，表示不符合任何條件時的預設值


    except psycopg2.DatabaseError as e:
        print("資料庫錯誤：", e)
        df = pd.DataFrame()  # 返回空的 DataFrame

    except Exception as e:
        print("發生錯誤：", e)
        df = pd.DataFrame()  # 返回空的 DataFrame

    finally:
        # 確保游標和連接被關閉
        if cur:
            cur.close()
        if conn:
            conn.close()

    print("以下為獲取的資料表:")
    print(df)

    return df

#=========================================
def prepare_data(df,shuffle=False):
    """
    將數據標準化並創建訓練和測試數據集。

    參數:
    df : DataFrame
        至少包含open、high、low、close、volume、price_change_percent、status的數據。
    shuffle : bool
        為真值的時候觸發隨機洗牌 df
    

    返回:
    X_train : numpy.ndarray
        訓練集特徵數據。
    y_train : numpy.ndarray
        訓練集目標數據。
    """
    
    # 如果shuffle為true就會隨機洗牌 df
    # 隨機選擇所有行，frac=1 表示選擇 100% 的行。
    if shuffle:
        df = df.sample(frac=1).reset_index(drop=True)


    X = df[['open', 'high', 'low', 'close', 'volume']]
    y_train = df['status']


    # 資料歸一化（最大最小方法）
    # y不用轉換，因為是固定4種狀態
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    scaler.fit(X)           # 訓練
    X_train = scaler.transform(X) # 轉換

    print("成功返回X_train:")
    print(X_train)
    print("成功返回y_train:")
    print(y_train)
    return X_train, y_train




def train_model(X_train, y_train, epochs=50, batch_size=32, validation_split=0.25):
    """
    定義、編譯並訓練一個神經網絡模型。

    參數:
    X_train : numpy.ndarray
        訓練集特徵數據。
    y_train : numpy.ndarray
        訓練集目標數據。

    epochs : int
        訓練的輪數，預設為 50。
    batch_size : int
        每次訓練的批次大小，預設為 32。
    validation_split : float
        要拆分成測試集的比例，預設為 0.25。
    
    返回:
    model : keras.Model
        訓練好的模型。
    """
    

    import keras
    from keras import layers 

    # 順序模型：類似搭積木一樣一層、一層放上去
    # 用Sequential建立模型
    model = keras.Sequential()


    # input資料
    model.add(layers.Input(shape=(5,))) # 傳入5個特徵

    # input為5個特徵，output為64個神經元。
    # 用relu來收斂
    model.add(layers.Dense(64, activation='relu'))

    # input為64個特徵，output為32個神經元。
    # 用relu來收斂
    model.add(layers.Dense(32, activation='relu'))

    # 輸出5個神經元
    model.add(layers.Dense(5, activation='softmax'))# 5 個輸出對應於 4 個狀態(1.2.3.4)加一個沒有狀態(0)

    # 查看模型結構
    model.summary()

    # 編譯模型
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])


    # 訓練模型
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=validation_split)

    import matplotlib
    matplotlib.use('Agg')  # 使用非 GUI 後端，防止非主線程中嘗試執行 GUI而報錯
    import matplotlib.pyplot as plt

    # 繪製訓練 & 驗證的準確率值
    plt.figure()  # 創建新圖形
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('Model accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='best')


    # 保存model_accuracy的圖到static
    plt.savefig('static/model_accuracy.png')  # 可以選擇其他格式，如 .jpg 或 .pdf

    # 顯示圖片
    # plt.show()

    return model




def fetch_stock_data_today(ticker):
    """
    給股票代號，返回今日的開高收低量的資料表。

    參數:
    ticker (str): 
        股票代碼，例如 '2330.TW'。

    返回:
    df : DataFrame
        返回今日的開高收低量的資料表。
    """
    import yfinance as yf
    # 獲取股票數據
    stock = yf.Ticker(ticker)
    # 獲取今日的數據
    data = stock.history(period='1d')
    
    # 提取開盤價、最高價、最低價、收盤價和成交量
    open_price = data['Open'].iloc[0]
    high_price = data['High'].iloc[0]
    low_price = data['Low'].iloc[0]
    close_price = data['Close'].iloc[0]
    volume = data['Volume'].iloc[0]
    
    # 將數據放入字典中
    stock_data = {
        'open': [open_price],
        'high': [high_price],
        'low': [low_price],
        'close': [close_price],
        'volume': [volume]
    }

    # 將字典轉換為 DataFrame
    df = pd.DataFrame(stock_data)

    print("當天的股票資料為:")
    print(stock_data)

    print("成功返回資料表:")
    print(df)
    
    # 返回 DataFrame
    return df


def prediction(model, X_train, X_test):
    """
    把X_train導入用來得到標準化的轉換標準，然後用X_test做預測，返回預測結果。

    參數:
    model : keras.Model
        訓練好的模型。    
    X_train : numpy.ndarray
        訓練集特徵數據。
        用來得到標準化的轉換標準。
    X_test : numpy.ndarray
        要預測的目標數據。

    返回:
    predictions : numpy.ndarray
        輸出預測結果的狀態碼。
    """

    # 資料歸一化（最大最小方法）
    # y不用轉換，因為是固定4種狀態
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    scaler.fit(X_train)           # 用X_train訓練保持最大最小值相同
    X_test = scaler.transform(X_test) # 對X_test轉換

    # 預測
    predictions = model.predict(X_test)

    print("predictions預測的機率分布:")
    print(np.round(predictions[0],3))


    # 用np.argmax把[]中的最適結果印出來
    predictions = np.argmax(predictions,axis=1)

    print('prelabel:',predictions)

    return predictions


def convert_status(status_codes):
    """
    把預測結果的狀態碼轉換成文字。

    參數:
    status_codes : int
        預測結果的狀態碼。

    返回:
    status_descriptions : numpy.ndarray
        輸出預測結果
    """
    # 定義映射字典
    status_mapping = {
        0: '沒變化',
        1: '漲幅大於3%',
        2: '小漲',
        3: '小跌',
        4: '跌幅大於3%'
    }
    # 使用列表推導式進行轉換
    status_descriptions = [status_mapping[code] for code in status_codes]


    
    return str(status_descriptions[0])
    




if __name__ == "__main__":
    ticker = '2330.TW'  # 輸入的股票代碼

    # 給股票代號，返回股票資料開高收低量的資料表
    stock_data_df = fetch_stock_data(ticker)

    # 給股票資料表，返回X_train和y_train
    # shuffle為要不要開起洗牌df功能，這裡不開啟，
    # 因為Keras 通常會從提供的數據集中選擇最後的部分作為驗證數據，這樣的驗證方式更貼近要預測的時間點。
    X_train, y_train = prepare_data(stock_data_df,shuffle=False)

    # 輸入X_train和y_train去訓練，返回訓練好的模型
    model = train_model(X_train, y_train, epochs=10, batch_size=5, validation_split=0.25)

    # 給股票代號，返回今日的開高收低量的資料表
    stock_data_today_df = fetch_stock_data_today(ticker)

    # 把資料表的資料摳出來
    X_test = stock_data_today_df[['open', 'high', 'low', 'close', 'volume']]

    #給訓練好的模型並把X_train導入用來得到標準化的轉換標準，然後用X_test做預測，返回預測結果
    predictions = prediction(model, X_train, X_test)

    # 把輸出的預測結果轉換成文字
    status_descriptions = convert_status(predictions)

    print("預測結果為:" + status_descriptions)










  


