# 導入 LINE Messaging API 必要元件
from linebot.v3.messaging import (
    MessagingApi,       # LINE 訊息發送核心類別
    ReplyMessageRequest, # 回覆請求封裝物件
    TextMessage,        # 文字訊息格式
    ApiClient           # API 客戶端管理器
)
import pandas as pd  # 數據處理套件

# 引入自訂的台灣證交所資料爬蟲模組
import WebCrawler_MIS_TWSE

from conversation_validator import conversation_validator

def handle_postback(event, configuration):
    """
    處理 LINE 的 Postback 事件入口函數
    
    Args:
        event (PostbackEvent): LINE 平台傳入的 postback 事件物件
        configuration (Configuration): LINE Bot 配置物件，包含 channel access token 等認證資訊
    """
    # 建立 API 客戶端連線 (自動處理連線池與重試機制)
    with ApiClient(configuration) as api_client:
        # 初始化 Messaging API 實例
        line_bot_api = MessagingApi(api_client)
        
        # 從 postback 事件提取數據 (格式範例: "2330,詳細資料")
        postback_data = event.postback.data
        
        # 解析數據為股票代號與指令類型
        postback_data_stock_code = postback_data.split(',')[0]  # 提取股票代號部分
        postback_data_text = postback_data.split(',')[1]        # 提取指令類型部分

        # ---------------------------
        # 處理「詳細資料」請求
        # ---------------------------
        if postback_data_text == '詳細資料':
            # 呼叫爬蟲模組獲取股票歷史數據
            df = WebCrawler_MIS_TWSE.webcrawler(postback_data_stock_code)
            
            # 將 DataFrame 轉置後發送 (T 屬性為轉置快捷方式)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,  # 使用事件內建的回覆 token
                    messages=[
                        TextMessage(
                            # 轉置後數據轉字串，\n 強制換行增加可讀性
                            text='詳細資料：\n' + str(df.T)  
                        )
                    ]                    
                )
            )
            conversation_validator.enable_allow_conversation(True) # 允許接受新傳入對話
        
        # ---------------------------
        # 處理「當盤成交價」請求
        # ---------------------------
        elif postback_data_text == '當盤成交價':
            # 取得即時交易數據
            df = WebCrawler_MIS_TWSE.webcrawler(postback_data_stock_code)
            
            # 提取最新成交價與成交量
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            # iloc[0] 確保取得第一筆(最新)數據
                            text=(
                                '當盤成交價：' + df['當盤成交價'].iloc[0] + '\n'
                                '當盤成交量：' + df['當盤成交量'].iloc[0]
                            )
                        )
                    ]                    
                )
            )
            conversation_validator.enable_allow_conversation(True) # 允許接受新傳入對話

        # ---------------------------
        # 處理「最佳五檔」請求
        # ---------------------------
        elif postback_data_text == '最佳五檔':
            # 獲取盤口數據
            df = WebCrawler_MIS_TWSE.webcrawler(postback_data_stock_code)
            
            # 篩選五檔相關欄位
            df = pd.DataFrame(
                df,
                columns=[
                    '五檔賣價(從低到高，以_分隔資料)',  # 賣方價格檔位 (價格遞增)
                    '五檔賣量(從低到高，以_分隔資料)',  # 對應賣量
                    '五檔買價(從高到低，以_分隔資料)',  # 買方價格檔位 (價格遞減)
                    '五檔買量(從高到低，以_分隔資料)'   # 對應買量
                ]
            )

            # 發送轉置後的五檔數據
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            # 轉置後以垂直方式顯示各檔位資訊
                            text=str(df.T)  
                        )
                    ]                    
                )
            )
            conversation_validator.enable_allow_conversation(True) # 允許接受新傳入對話