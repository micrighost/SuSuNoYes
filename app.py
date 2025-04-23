# 引入自訂的台灣證交所資料爬蟲模組
import WebCrawler_MIS_TWSE

# 引入 Google AI 相關模組（假設為自訂模組）
import google_ai

# 引入智慧預測模組（假設為自訂模組）
import intelligent_prediction

# 引入 pandas 做資料處理
import pandas as pd

# 引入 os 處理環境變數
import os
# 引入 dotenv 用來載入 .env 檔案中的環境變數
from dotenv import load_dotenv

# 引入 Flask 建立 Web 應用程式
from flask import Flask, request, abort

# 引入 LINE Bot SDK v3 的相關元件
from linebot.v3 import (
    WebhookHandler  # 用於處理 webhook 事件
)
from linebot.v3.exceptions import (
    InvalidSignatureError  # 用於處理簽名驗證錯誤
)
from linebot.v3.messaging import (
    Configuration,        # 設定 LINE Bot API 的存取權杖
    ApiClient,            # 建立 API 客戶端
    MessagingApi,         # 傳送訊息的 API
    BroadcastRequest,     # 廣播訊息請求
    PushMessageRequest,   # 推播訊息請求
    MulticastRequest,     # 多人推播請求
    ReplyMessageRequest,  # 回覆訊息請求
    TextMessage,          # 文字訊息物件
    Emoji,                # 貼圖表情物件
    VideoMessage,         # 影片訊息物件
    AudioMessage,         # 音訊訊息物件
    LocationMessage,      # 位置訊息物件
    StickerMessage,       # 貼圖訊息物件
    ImageMessage,         # 圖片訊息物件
    ConfirmTemplate,      # 確認模板
    TemplateMessage,      # 模板訊息
    ButtonsTemplate,      # 按鈕模板
    CarouselTemplate,     # 輪播模板
    CarouselColumn,       # 輪播欄位
    ImageCarouselTemplate,# 圖片輪播模板
    ImageCarouselColumn,  # 圖片輪播欄位
    MessageAction,        # 訊息動作
    URIAction,            # 網址動作
    PostbackAction,       # 回傳動作
    DatetimePickerAction, # 日期時間選擇動作
    CameraAction,         # 相機動作
    CameraRollAction,     # 相簿動作
    LocationAction,       # 位置動作
    QuickReply,           # 快速回覆
    QuickReplyItem,       # 快速回覆項目
)

# 引入 webhook 事件相關物件
from linebot.v3.webhooks import (
    MessageEvent,         # 訊息事件
    TextMessageContent,   # 文字訊息內容
    PostbackEvent         # 回傳事件
)

# 建立 Flask 應用程式實例
app = Flask(__name__)

# 載入 .env 檔案中的環境變數
load_dotenv()

# 以環境變數設定 LINE Bot 的存取權杖與密鑰
configuration = Configuration(access_token=os.getenv('YOUR_CHANNEL_ACCESS_TOKEN'))  # 設定存取權杖
handler = WebhookHandler(os.getenv('YOUR_CHANNEL_SECRET'))  # 設定 webhook handler 的密鑰


@app.route("/callback", methods=['POST'])  # 定義接收 LINE Webhook 的 POST 請求路由
def callback():
    # 從請求標頭中取得 LINE 的簽名(X-Line-Signature)
    signature = request.headers['X-Line-Signature']

    # 將請求主體(body)轉換為文字格式
    body = request.get_data(as_text=True)
    # 在 Flask 日誌中記錄請求內容(用於除錯)
    app.logger.info("Request body: " + body)

    # 處理 Webhook 請求主體
    try:
        # 用 handler 驗證簽名並處理事件
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 當簽名驗證失敗時記錄錯誤訊息
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)  # 返回 HTTP 400 錯誤

    # 返回 HTTP 200 OK 響應
    return 'OK'



from allow_validator import allow_validator
from training_validator import training_validator



def get_https_image_url(filename):
    """生成 HTTPS 圖片 URL"""
    # 獲取當前服務器根 URL 並拼接圖片路徑
    # 強制轉換為 HTTPS（LINE 要求圖片必須使用 HTTPS）
    base_url = request.url_root.replace("http://", "https://")
    return f"{base_url}static/{filename}"



# 監聽所有文字訊息事件
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # 取得使用者輸入的文字內容
    text = event.message.text
    
    # 初始化 LINE Messaging API 客戶端
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # 處理「股票查詢」指令
        if text in ['1', '叔叔我要報', '叔叔我要抱']:
            # 回覆操作指引
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='叔叔要給你報，請輸入股票代號，或按0退出')]
                )
            )
            
            # 狀態機設定
            allow_validator.enable_fetch_stock_data(True)  # 啟用爬蟲模式
            allow_validator.enable_ai_chat(False)     # 關閉聊天模式
            allow_validator.enable_intelligent_prediction(False)  # 關閉推薦模式
            training_validator.mark_as_ready(False)      # 關閉訓練模式

        # 處理「聊天模式」指令    
        elif text in ['2', '我要撩叔叔', '我要聊叔叔']:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='叔叔跟你聊，請輸入你要的聊的，或按0退出')]
                )
            )
            
            # 狀態機設定
            allow_validator.enable_ai_chat(True)      # 啟用聊天模式
            allow_validator.enable_fetch_stock_data(False)  # 關閉爬蟲模式
            allow_validator.enable_intelligent_prediction(False)  # 關閉推薦模式
            training_validator.mark_as_ready(False)      # 關閉訓練模式

        # 處理「股票推薦」指令
        elif text in ['3', '我要推叔叔']:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='叔叔給你推，請輸入你要詢問的股票代號，或按0退出')]
                )
            )
            
            # 狀態機設定
            allow_validator.enable_intelligent_prediction(True)  # 啟用推薦模式
            allow_validator.enable_fetch_stock_data(False)       # 關閉爬蟲模式
            allow_validator.enable_ai_chat(False)           # 關閉聊天模式
            training_validator.mark_as_ready(False)           # 關閉訓練模式


#==========================================================
        # 檢查是否處於爬蟲模式（允許查詢股票資料的狀態）
        if allow_validator.is_allow_fetch_stock_data():
            
            # 驗證股票代號是否有效（檢查是否能取得資料）
            if WebCrawler_MIS_TWSE.webcrawler_true(text):
                
                # ---------------------------
                # 設定快速選單圖示路徑
                # ---------------------------
                details_icon = get_https_image_url('自以為是的佩佩切出.png')
                current_transaction_price_icon = get_https_image_url('快樂的佩佩.png')
                best_five_tick_icon = get_https_image_url('悲傷的佩佩.png')
                datetime_icon = get_https_image_url('calendar.png')
                date_icon = get_https_image_url('calendar.png')
                time_icon = get_https_image_url('time.png')

                # ---------------------------
                # 處理有效股票代號（4位數字）
                # ---------------------------
                if text.isdigit() and len(text) == 4:
                    # 建立快速回覆選單
                    quickReply = QuickReply(
                        items=[
                            # 詳細資料選項
                            QuickReplyItem(
                                action=PostbackAction(
                                    label="詳細資料",          # 選項顯示文字
                                    data=f"{text},詳細資料",   # 格式：股票代號,指令類型
                                    display_text="這是詳細資料" # 用戶點擊後顯示的文字
                                ),
                                image_url=details_icon  # 自定義圖示
                            ),
                            
                            # 當盤成交價選項
                            QuickReplyItem(
                                action=PostbackAction(
                                    label="當盤成交價",
                                    data=f"{text},當盤成交價",
                                    display_text="這是當盤成交價"
                                ),
                                image_url=current_transaction_price_icon
                            ),
                            
                            # 最佳五檔選項
                            QuickReplyItem(
                                action=PostbackAction(
                                    label="最佳五檔",
                                    data=f"{text},最佳五檔",
                                    display_text="這是最佳五檔"
                                ),
                                image_url=best_five_tick_icon
                            )
                        ]
                    )

                    # 回覆帶有快速選單的訊息
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[
                                TextMessage(
                                    text='叔叔要給你報，請選擇你要的功能，你不選擇就算了',
                                    quick_reply=quickReply  # 附加快速選單
                                )
                            ]
                        )
                    )
                    
                    # 關閉爬蟲模式（避免重複觸發）
                    allow_validator.enable_fetch_stock_data(False)

            # ---------------------------
            # 處理無效輸入
            # ---------------------------
            # 若股票代號無效且不是指令關鍵字
            elif not WebCrawler_MIS_TWSE.webcrawler_true(text) and text not in ['1', '0', '叔叔我要報', '叔叔我要抱']:
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text='沒有這股票不要騙叔叔，給我輸入股票代號，或按0退出')]
                    )
                )

            # ---------------------------
            # 處理退出指令
            # ---------------------------
            if text == '0':
                # 關閉爬蟲模式
                allow_validator.enable_fetch_stock_data(False)



        # 如果訪問叔叔AI（聊天模式）已經開啟則進入循環
        if allow_validator.is_allow_ai_chat():
            # 過濾掉進入聊天模式的指令本身與退出指令
            if text not in ['2', '0', '我要撩叔叔', '我要聊叔叔']:
                # 如果使用者輸入'r'，讓AI「失憶」（重置對話）
                if text == 'r':
                    # 呼叫google_ai的ai_model方法，傳入特殊指令讓AI重置
                    susureturn = google_ai.ai_model('你是誰?', 'r')

                    # 回覆訊息給使用者，提示可繼續對話
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(
                                text='快跟叔叔說說話吧\n===================\n' + susureturn 
                            )]
                        )
                    )

                # 處理一般聊天輸入
                if text != 'r':
                    # 將使用者輸入傳給AI模型，取得回覆
                    susureturn = google_ai.ai_model(text, "1")
                    print(susureturn)
                    # 回覆訊息給使用者，並提示可讓AI失憶或退出
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(
                                text='按r讓叔叔失憶，或按0退出\n===================\n' + susureturn 
                            )]
                        )
                    )

            # 如果使用者輸入0，關閉訪問叔叔AI（退出聊天模式）
            if text == '0':
                allow_validator.enable_ai_chat(False)




        # 如果「智能預測模式」已開啟
        if allow_validator.is_allow_intelligent_prediction():
            
            # 檢查是否已完成數據準備階段
            if training_validator.check_training_ready() == False:
                
                # 驗證輸入是否為4位數股票代號
                if text.isdigit() and len(text) == 4:
                    
                    # 格式化成台灣股票代號格式 (如 2330.TW)
                    training_validator.ticker = text + '.TW'
                    
                    # 抓取歷史股價數據
                    df = intelligent_prediction.fetch_stock_data(training_validator.ticker)
                    
                    if df.empty:
                        # 數據抓取失敗回應
                        line_bot_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token,
                                messages=[TextMessage(
                                    text='沒抓到資料：換檔股票或是輸入的股票代號不正確，請輸入4個數字'
                                )]
                            )
                        )
                    else:
                        # 數據抓取成功回應
                        line_bot_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token,
                                messages=[TextMessage(
                                    text='我抓到資料了，接下來將要訓練模型，請輸入妳想要的訓練次數4-999，訓練時間依訓練次數會有所不同，並且不要覺得會很快'
                                )]
                            )
                        )
                        
                        # 準備訓練數據 (不洗牌以保留時間序列特性)
                        X_train, y_train = intelligent_prediction.prepare_data(df, shuffle=False)
                        
                        # 標記數據準備完成
                        training_validator.mark_as_ready(True)
                        
                        # 儲存訓練數據到全局變數
                        training_validator.X_train = X_train
                        training_validator.y_train = y_train
                        
                        # 清空輸入內容避免干擾後續流程
                        text = ""

                # 處理無效輸入
                elif ((text.isdigit() == False) or len(text) != 4) and text not in ["0", "3", ""]:
                    print(f"無效輸入: {text}")
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(
                                text='現在是要查詢資料庫裡是否有資料可以幫你分析，請輸入妳想要分析的股票代號'
                            )]
                        )
                    )

            # 數據準備完成後的模型訓練階段
            if training_validator.check_training_ready():
                
                # 驗證訓練次數輸入 (1-3位數)
                if text.isdigit() and (len(text) < 4):
                    
                    # 模型訓練參數設定
                    epochs = int(text)
                    batch_size = 5
                    validation_split = 0.25
                    
                    # 啟動模型訓練
                    model = intelligent_prediction.train_model(
                        training_validator.X_train,
                        training_validator.y_train,
                        epochs=epochs,
                        batch_size=batch_size,
                        validation_split=validation_split
                    )
                    
                    # 獲取最新股價數據
                    stock_data_today_df = intelligent_prediction.fetch_stock_data_today(training_validator.ticker)
                    
                    # 提取特徵數據
                    X_test = stock_data_today_df[['open', 'high', 'low', 'close', 'volume']]
                    
                    # 執行預測
                    predictions = intelligent_prediction.prediction(model, training_validator.X_train, X_test)
                    
                    # 轉換預測結果為文字描述
                    status_descriptions = intelligent_prediction.convert_status(predictions)
                    
                    # 生成模型準確率圖表連結
                    details_icon = get_https_image_url('model_accuracy.png')
                    
                    # 發送預測結果與圖表
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[
                                TextMessage(text='訓練完成，明日預測結果為:' + "\n" + status_descriptions + "\n" '以下是模型的訓練圖:'),
                                ImageMessage(original_content_url=details_icon, preview_image_url=details_icon)
                            ]
                        )
                    )
                    
                    # 重置訓練狀態
                    training_validator.mark_as_ready(False)


                # 處理訓練階段的無效輸入
                elif text != "":
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(
                                text='現在是要訓練模型，請輸入妳想要的訓練次數4-999'
                            )]
                        )
                    )

            # 處理退出指令
            if text == '0':
                # 關閉智能預測模式
                allow_validator.enable_intelligent_prediction(False)
                # 重置訓練狀態
                training_validator.check_training_ready(False)
           
            


from postback_handler import handle_postback

# 處理 LINE 的 PostbackEvent (快速選單回傳事件)
@handler.add(PostbackEvent) # 註冊 Postback 事件處理器
def postback_event_handler(event):
    handle_postback(event, configuration)




            
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)