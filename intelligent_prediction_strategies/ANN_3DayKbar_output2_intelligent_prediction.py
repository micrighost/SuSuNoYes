import psycopg2
import pandas as pd
import numpy as np

import os
from dotenv import load_dotenv
# 加載 .env 文件中的環境變數
load_dotenv()


def get_k_type(row):
    """簡化版 K 棒型態判斷
    
    參數說明:
    row : pd.Series - 需包含 open, high, low, close 四個價格欄位
    
    返回狀態碼:
    0: 無效數據     1: 紅K鎚子線     2: 大陽線     3: 倒鎚紅K線
    4: 紡錘紅K線    5: 十字線  6: 紡錘黑K線    7: 倒鎚黑K線
    8: 黑K鎚子線    9: 大陰線
    """
    # 解構價格數據：從輸入的 Series 中提取四個關鍵價格
    o = row['open']   # 開盤價
    h = row['high']   # 最高價
    l = row['low']    # 最低價
    c = row['close']  # 收盤價

    # 異常數據檢查區塊
    # 檢查缺失值與價格合理性 (排除異常數據)
    if any(pd.isna([o, h, l, c])):  # 任一價格為缺失值
        return 0
    if h < l:                       # 最高價低於最低價
        return 0
    if o > h or o < l or c > h or c < l:  # 開盤/收盤超出高低範圍
        return 0

    # 核心指標計算區塊
    body = c - o                # 實體方向與大小 (正值為陽線，負值為陰線)
    body_size = abs(body)       # 實體絕對長度
    upper_shadow = h - max(o, c)  # 上影線長度 = 最高價 - 實體頂部
    lower_shadow = min(o, c) - l  # 下影線長度 = 實體底部 - 最低價
    total_range = h - l         # 當日總波動範圍

    # 防除零處理：當 total_range=0 時，設定 body_ratio=0 (一字線情況已單獨處理)
    body_ratio = body_size / total_range if total_range != 0 else 0  # 身體比例
    is_bullish = body > 0       # 判斷陰陽線 (body > 0 會寫入值 = 陽線, body = 0 就不寫入 = 陰線)

    # 極端型態優先判斷區塊
    # 一字線判斷：四價相同，視為十字線變體
    if h == l:
        return 5  # 狀態碼5=十字線

    # 大陽線判斷：開盤=最低價，收盤接近最高價 (允許5%以內上影線)
    # 條件：開盤在最低點 且 收盤達到最高價的95%以上
    if o == l and c >= h * 0.95:
        return 2  # 狀態碼2=大陽線

    # 大陰線判斷：開盤=最高價，收盤接近最低價 (允許5%以內下影線)
    # 條件：開盤在最高點 且 收盤低於最低價的105% (因允許5%影線，實際應為 c <= l * 1.05)
    if o == h and c <= l * 1.05:
        return 9  # 狀態碼9=大陰線

    # 影線主導型態判斷區塊
    # 倒鎚線判斷：長上影(>=1.8倍實體) + 短下影(<=0.5倍實體)
    # 此處使用絕對值比較，避免除零問題
    if upper_shadow >= 1.8 * body_size and lower_shadow <= 0.5 * body_size:
        return 3 if is_bullish else 7  # 陽線=倒鎚紅K(3)，陰線=倒鎚黑K(7)

    # 鎚子線判斷：長下影(>=1.8倍實體) + 短上影(<=0.5倍實體)
    if lower_shadow >= 1.8 * body_size and upper_shadow <= 0.5 * body_size:
        return 1 if is_bullish else 8  # 陽線=紅鎚(1)，陰線=黑鎚(8)

    # 紡錘線判斷區塊
    # 條件：實體佔比20%~40% 且 影線對稱(差異<30%總波動)
    if 0.2 < body_ratio < 0.4 and abs(upper_shadow - lower_shadow) < 0.3 * total_range:
        return 4 if is_bullish else 6  # 陽線=紡錘紅(4)，陰線=紡錘黑(6)

    # 十字線判斷區塊
    # 條件：實體佔比<20% 且 有波動(total_range>0)
    if body_ratio < 0.2 and total_range > 0:
        return 5  # 狀態碼5=十字線

    # 最終回退機制
    # 當不滿足任何明確型態時，根據陰陽線返回對應紡錘線
    return 4 if is_bullish else 6  # 陽線回退紡錘紅(4)，陰線回退紡錘黑(6)




def fetch_stock_data(ticker):
    """根據股票代碼從 PostgreSQL 資料庫中獲取股票數據並標註K棒型態
    
    參數:
    ticker (str): 股票代碼，例如 '2330.TW'
    
    返回:
    pd.DataFrame: 包含 open, high, low, close, volume, k-2_status, k-1_status, k_status 的 DataFrame
    """
    try:
        # 連接資料庫
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )

        # 獲取數據
        cur = conn.cursor()
        query = "SELECT date, open, high, low, close, volume FROM stock_data WHERE ticker = %s ORDER BY date;"
        cur.execute(query, (ticker,))
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(rows, columns=colnames)

        # 應用型態判斷
        df['k_status'] = df.apply(get_k_type, axis=1)
        
        # 新增歷史狀態欄位
        df['k-1_status'] = df['k_status'].shift(1)  # 前一日狀態
        df['k-2_status'] = df['k_status'].shift(2)  # 前兩日狀態

        # 填充前兩日不存在的狀態為 0 (無效數據)
        df[['k-1_status', 'k-2_status']] = df[['k-1_status', 'k-2_status']].fillna(0).astype(int)



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
            (price_change_percent > 0) & (price_change_percent <= 0.03),  # 漲幅大於0%且小於等於3%，設為 1
            (price_change_percent < 0) & (price_change_percent >= -0.03),  # 跌幅大於0%且小於等於-3%，設為 2
            (price_change_percent < -0.03)  # 跌幅大於-3%，設為 2
        ]
        choices = [1, 1, 2, 2]  # 對應的狀態值 

        # 使用 np.select 根據條件設置狀態
        df['status'] = np.select(conditions, choices, default=0)  # default=0 可選，表示不符合任何條件時的預設值

    except psycopg2.DatabaseError as e:
        print("資料庫錯誤：", e)
        df = pd.DataFrame()

    except Exception as e:
        print("發生錯誤：", e)
        df = pd.DataFrame()

    finally:
        if cur: cur.close()
        if conn: conn.close()

    print("K棒型態編號說明:") 
    print("0: 無效數據 1: 大陽線 2: 大陰線 3: 十字線 4: 倒鎚紅K線 5: 倒鎚黑K線")
    print("6: 紅K鎚子線 7: 黑K鎚子線 8: 紡錘紅K線 9: 紡錘黑K線")
    print(df[['open', 'high', 'low', 'close', 'volume', 'k-2_status', 'k-1_status', 'k_status', 'price_change_percent', 'status']])
    return df[['open', 'high', 'low', 'close', 'volume', 'k-2_status', 'k-1_status', 'k_status', 'price_change_percent', 'status']]




def prepare_data(df,shuffle=False):
    """
    將數據標準化並創建訓練和測試數據集。

    參數:
    df : DataFrame
        至少包含volume、k-2_status、k-1_status、k_status、status的數據。
    if shuffle : bool
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


    X = df[['volume', 'k-2_status', 'k-1_status', 'k_status']]
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
    model.add(layers.Input(shape=(4,))) # 傳入4個特徵

    # input為4個特徵，output為64個神經元。
    # 用relu來收斂
    model.add(layers.Dense(64, activation='relu'))

    # input為64個特徵，output為32個神經元。
    # 用relu來收斂
    model.add(layers.Dense(32, activation='relu'))

    # 輸出3個神經元
    model.add(layers.Dense(3, activation='softmax')) # 3 個輸出對應於 2 個狀態(1.2)加一個沒有狀態(0)

    # 查看模型結構
    model.summary()

    # 編譯模型
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])


    # 訓練模型
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=validation_split)

    import matplotlib
    matplotlib.use('Agg')  # 使用非GUI的Agg後端，這樣 Matplotlib 就不會嘗試開啟視窗或用 GUI，只會把圖存成檔案
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

    # 獲取3日的數據
    data = stock.history(period='3d')

    # 直接轉換為DataFrame
    df = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    df.columns = ['open', 'high', 'low', 'close', 'volume']  # 統一欄位名稱
    

    # 應用型態判斷
    df['k_status'] = df.apply(get_k_type, axis=1)
    
    # 新增歷史狀態欄位
    df['k-1_status'] = df['k_status'].shift(1)  # 前一日狀態
    df['k-2_status'] = df['k_status'].shift(2)  # 前兩日狀態

    # 填充前兩日不存在的狀態為 0 (無效數據)
    df[['k-1_status', 'k-2_status']] = df[['k-1_status', 'k-2_status']].fillna(0).astype(int)

    # 調整欄位順序
    columns_order = ['open', 'high', 'low', 'close', 'volume', 'k-2_status', 'k-1_status', 'k_status']
    df = df.reindex(columns=columns_order)

    # 過濾最新日
    df = df.iloc[[-1]]  # 取最後一筆(最新日)

    print("成功返回資料表:")
    print(df)
    
    # 返回 DataFrame
    return df


def prediction(model, X_train, X_test):
    """
    把X_train導入用來得到標準化的轉換標準，然後用X_test做預測，返回預測結果。

    參數:
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
        1: '會漲',
        2: '會跌'
    }
    # 使用列表推導式進行轉換
    status_descriptions = [status_mapping[code] for code in status_codes]

    # 顯示結果
    print("預測結果為:" + str(status_descriptions))
    
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
    model = train_model(X_train, y_train, epochs=100, batch_size=5, validation_split=0.25)

    # 給股票代號，返回今日的開高收低量的資料表
    stock_data_today_df = fetch_stock_data_today(ticker)

    # # 把資料表的資料摳出來
    X_test = stock_data_today_df[['volume', 'k-2_status', 'k-1_status', 'k_status']]

    # # 給訓練好的模型並把X_train導入用來得到標準化的轉換標準，然後用X_test做預測，返回預測結果
    predictions = prediction(model, X_train, X_test)

    # # 把輸出的預測結果轉換成文字
    convert_status(predictions)
