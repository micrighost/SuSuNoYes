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



class TrueLimiter:
    def __init__(self):
        """初始化所有功能權限開關"""
        self.allow_fetch_stock_data = False  # 股票數據爬取權限
        self.allow_ai_susu_chat = False      # AI 聊天功能權限
        self.allow_intelligent_prediction = False  # 智能預測權限

    def is_allow_fetch_stock_data(self) -> bool:
        """檢查股票數據爬取權限 (簡化寫法)"""
        return self.allow_fetch_stock_data  # 直接返回布林值

    def is_allow_ai_susu_chat(self) -> bool:
        """檢查 AI 聊天功能權限"""
        return self.allow_ai_susu_chat

    def is_allow_intelligent_prediction(self) -> bool:
        """檢查智能預測功能權限"""
        return self.allow_intelligent_prediction

    # 新增權限切換方法
    def enable_fetch_stock_data(self, enable: bool):
        """設置股票數據爬取權限"""
        self.allow_fetch_stock_data = enable

    def enable_ai_susu_chat(self, enable: bool):
        """設置 AI 聊天功能權限"""
        self.allow_ai_susu_chat = enable

    def enable_intelligent_prediction(self, enable: bool):
        """設置智能預測功能權限"""
        self.allow_intelligent_prediction = enable

# 實例化權限控制器
true_limiter = TrueLimiter()

# 訓練狀態控制器 (修正命名並添加型別提示)
class TrainingReadyValidator:
    def __init__(self):
        """初始化訓練狀態相關參數"""
        self.ticker: str = ""            # 股票代碼
        self.is_ready: bool = False      # 準備訓練完成標誌
        self.X_train = None              # 訓練特徵數據 (建議使用具體數據結構)
        self.y_train = None              # 訓練目標數據

    def check_training_ready(self) -> bool:
        """檢查訓練是否完成 (簡化寫法)"""
        return self.is_ready  # 直接返回布林值

    # 新增訓練數據設置方法
    def set_training_data(self, X_train, y_train):
        """設置訓練數據"""
        self.X_train = X_train  # 實際使用時應驗證數據格式
        self.y_train = y_train

    def mark_as_ready(self, ready: bool):
        """標記訓練狀態"""
        self.is_ready = ready

# 實例化訓練狀態驗證器
training_validator = TrainingReadyValidator()





# 監聽叔叔事件
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text # 取得訊息資訊
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)




        # 當接收到這些訊息，開啟訪問爬蟲
        if text == '1' or text == '叔叔我要報' or text == '叔叔我要抱':

            # 提示使用者輸入的信息
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='叔叔要給你報，請輸入股票代號，或按0退出'
                    )]
                )
            )

            # 允許用4個數字訪問爬蟲
            true_limiter.enable_fetch_stock_data(True)
            # 如果訪問叔叔AI的狀態開啟，則關閉其他狀態(進到新的狀態前就把舊狀態關起來)
            true_limiter.enable_ai_susu_chat(False)
            # 如果訪問叔叔推薦股票的狀態開啟，則關閉其他狀態(進到新的狀態前就把舊狀態關起來)
            true_limiter.enable_intelligent_prediction(False)
            # 關閉訓練準備狀態
            training_validator.mark_as_ready(False)



        # 當接收到這些訊息，開啟訪問叔叔AI
        if text == '2' or text == '我要撩叔叔' or text == '我要聊叔叔':

            # 提示使用者輸入的信息
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='叔叔跟你聊，請輸入你要的聊的，或按0退出'
                    )]
                )
            )

            # 允許訪問叔叔AI
            true_limiter.enable_ai_susu_chat(True)
            # 如果訪問爬蟲股票資料的狀態開啟，則關閉其他狀態(進到新的狀態前就把舊狀態關起來)
            true_limiter.enable_fetch_stock_data(False)
            # 如果訪問叔叔推薦股票的狀態開啟，則關閉其他狀態(進到新的狀態前就把舊狀態關起來)
            true_limiter.enable_intelligent_prediction(False)
            # 關閉訓練準備狀態
            training_validator.mark_as_ready(False)


        # 當接收到這些訊息，開啟訪問叔叔AI
        if text == '3' or text == '我要推叔叔':

            # 提示使用者輸入的信息
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='叔叔給你推，請輸入你要詢問的股票代號，或按0退出'
                    )]
                )
            )

            # 允許訪問叔叔推薦股票
            true_limiter.enable_intelligent_prediction(True)
            # 如果訪問爬蟲股票資料的狀態開啟，則關閉其他狀態(進到新的狀態前就把舊狀態關起來)
            true_limiter.enable_fetch_stock_data(False)
            # 如果訪問叔叔AI的狀態開啟，則關閉其他狀態(進到新的狀態前就把舊狀態關起來)
            true_limiter.enable_ai_susu_chat(False)
            # 關閉訓練準備狀態
            training_validator.mark_as_ready(False)


#==========================================================
        # 如果訪問爬蟲股票資料已經開啟則進入循環
        if true_limiter.is_allow_fetch_stock_data():

            # 驗證是否有辦法抓到資料
            if WebCrawler_MIS_TWSE.webcrawler_ture(text):
                
                # 載入快速選單圖片
                # 取得目前請求的url並加上static裡圖片的地址
                details_icon = request.url_root + 'static/自以為是的佩佩切出.png'
                # 把http://轉成"https://"
                details_icon  = details_icon.replace("http://", "https://")
                current_transaction_price_icon = request.url_root + 'static/快樂的佩佩.png'
                current_transaction_price_icon  = current_transaction_price_icon.replace("http://", "https://")
                best_five_tick_icon = request.url_root + 'static/悲傷的佩佩.png'
                best_five_tick_icon  = best_five_tick_icon.replace("http://", "https://")
                datetime_icon = request.url_root + 'static/calendar.png'
                datetime_icon = datetime_icon.replace("http://", "https://")
                date_icon = request.url_root + 'static/calendar.png'
                date_icon = date_icon.replace("http://", "https://")
                time_icon = request.url_root + 'static/time.png'
                time_icon = time_icon.replace("http://", "https://")


                # 如果正確輸入股票代號
                if text.isdigit() and len(text) == 4:   # 要是數字，還要剛好4個字節

                    # 快速選單
                    quickReply = QuickReply(
                        items=[

                            # 詳細資料的quickReply
                            QuickReplyItem(
                                action=PostbackAction(
                                    label="詳細資料",   # 選單上的文字
                                    data=text + ",詳細資料", # 把股票代號跟辨別哪個事件的文字打包入data傳入快速選單的事件
                                    display_text="這是詳細資料" # 按下後的自動回復語
                                ),
                                image_url=details_icon # 選單圖片
                            ),
                            
                            # 當盤成交價的quickReply
                            QuickReplyItem(
                                action=PostbackAction(
                                    label="當盤成交價", # 選單上的文字
                                    data=text + ",當盤成交價",  # 把股票代號跟辨別哪個事件的文字打包入data傳入快速選單的事件
                                    display_text="這是當盤成交價" # 按下後的自動回復語
                                ),
                                image_url=current_transaction_price_icon # 選單圖片
                            ),

                            # 最佳五檔的quickReply
                            QuickReplyItem(
                                action=PostbackAction(
                                    label="最佳五檔", # 選單上的文字
                                    data=text + ",最佳五檔",  # 把股票代號跟辨別哪個事件的文字打包入data傳入快速選單的事件
                                    display_text="這是最佳五檔" # 按下後的自動回復語
                                ),
                                image_url=best_five_tick_icon # 選單圖片
                            )
                        ]
                    )


                    
                    # 提示使用者輸入的信息
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(
                                text='叔叔要給你報，請選擇你要的功能，你不選擇就算了',
                                quick_reply=quickReply # 傳送上面訊息後，把快速選單啟動起來
                            )]
                        )
                    )
                    # 關閉用4個數字訪問爬蟲
                    true_limiter.enable_fetch_stock_data(False)

                

            if WebCrawler_MIS_TWSE.webcrawler_ture(text) == False and text != '1' and text != '0' and  text != '叔叔我要報' and  text != '叔叔我要抱' :
                # 提示使用者輸入的信息
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(
                            text='沒有這股票不要騙叔叔，給我輸入股票代號，或按0退出'
                        )]
                    )
                )

            # 如果使用者輸入0，關閉訪問爬蟲狀態
            if text == '0':

                # 關閉用4個數字訪問爬蟲
                true_limiter.enable_fetch_stock_data(False)


        # 如果訪問叔叔AI已經開啟則進入循環
        if true_limiter.is_allow_ai_susu_chat():
            if text != '2' and text != '0' and text != '我要撩叔叔' and text != '我要聊叔叔':
                if text == 'r':
                    susureturn = google_ai.ai_model('你是誰?','r')


                    # 提示使用者輸入的信息
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(
                                text='快跟叔叔說說話吧\n===================\n' + susureturn 
                            )]
                        )
                    )

                if text != 'r':
                    susureturn = google_ai.ai_model(text,"1")
                    print(susureturn)
                    # 提示使用者輸入的信息
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(
                                text='按r讓叔叔失憶，或按0退出\n===================\n' + susureturn 
                            )]
                        )
                    )




            # 如果使用者輸入0，關閉訪問叔叔AI
            if text == '0':

                # 關閉訪問叔叔AI
                true_limiter.enable_ai_susu_chat(False)




        # 如果訪問叔叔推薦股票已經開啟則進入循環
        if true_limiter.is_allow_intelligent_prediction():




            # 如果還沒進入training_is_ready狀態，就先抓取資料，並製作X_train, y_train
            if training_validator.check_training_ready() == False :

                # 防止text = 3 直接丟入fetch_stock_data產生報錯
                if text.isdigit() and len(text) == 4:   # 要是數字，還要剛好4個字節
        
                    # 轉換4個數字為台股編號
                    training_validator.ticker = text + '.TW'

                    # 嘗試獲取台股資料，錯誤時返回空df
                    df = intelligent_prediction.fetch_stock_data(training_validator.ticker)

                    # 如果df為空
                    if df.empty:
                        # 提示使用者輸入的信息
                        line_bot_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token,
                                messages=[TextMessage(
                                    text='沒抓到資料：換檔股票或是輸入的股票代號不正確，請輸入4個數字'
                                )]
                            )
                        )

                    else:
                        # 提示使用者輸入的信息
                        line_bot_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token,
                                messages=[TextMessage(
                                    text='我抓到資料了，接下來將要訓練模型，請輸入妳想要的訓練次數4-999，訓練時間依訓練次數會有所不同，並且不要覺得會很快'
                                )]
                            )
                        )
                        # 給股票資料表，返回X_train和y_train
                        # shuffle為要不要開起洗牌df功能，這裡不開啟，
                        # 因為Keras 通常會從提供的數據集中選擇最後的部分作為驗證數據，這樣的驗證方式更貼近要預測的時間點。
                        X_train, y_train = intelligent_prediction.prepare_data(df,shuffle=False)

                        # 設定訓練準備完成標記為True
                        training_validator.mark_as_ready(True)

                        # 把X_train和y_train傳入全域變數
                        training_validator.X_train = X_train
                        training_validator.y_train = y_train


                        # 把text清空，防止訊息繼續傳遞
                        text=""


            # 如果開啟了training_is_ready狀態，就準備訓練模型了
            if training_validator.check_training_ready():

                # 如果這時候
                if text.isdigit() and (len(text) < 4):   # 要是數字，字節還要小於4

                    # 輸入X_train和y_train去訓練，返回訓練好的模型
                    model = intelligent_prediction.train_model(training_validator.X_train, training_validator.y_train, epochs=int(text), batch_size=5, validation_split=0.25)
                    # 給股票代號，返回今日的開高收低量的資料表
                    stock_data_today_df = intelligent_prediction.fetch_stock_data_today(training_validator.ticker)

                    # 把資料表的資料摳出來
                    X_test = stock_data_today_df[['open', 'high', 'low', 'close', 'volume']]

                    #給訓練好的模型並把X_train導入用來得到標準化的轉換標準，然後用X_test做預測，返回預測結果
                    predictions = intelligent_prediction.prediction(model, training_validator.X_train, X_test)

                    # 把輸出的預測結果轉換成文字
                    status_descriptions = intelligent_prediction.convert_status(predictions)


                    details_icon = request.url_root + 'static/model_accuracy.png'
                    # 把http://轉成"https://"
                    details_icon  = details_icon.replace("http://", "https://")
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[
                                TextMessage(text='訓練完成，明日預測結果為:' + "\n" + status_descriptions + "\n" '以下是模型的訓練圖:'),
                                ImageMessage(original_content_url=details_icon, preview_image_url=details_icon)
                            ]
                        )
                    )

                    # 關閉訓練準備狀態
                    training_validator.mark_as_ready(False)

                    

                else:
                    # 如果已經在訓練準備階段，但是傳入的字又不是上個階段留下來的空字串，那就提示再次輸入
                    if text != "":
                        # 提示使用者輸入的信息
                        line_bot_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token,
                                messages=[TextMessage(
                                    text='現在是要訓練模型，請輸入妳想要的訓練次數0-999'
                                )]
                            )
                        )

            if ((text.isdigit() == False) or len(text) != 4) and text != "0" and text != "3" and text != "":
                print(text)
                # 提示使用者輸入的信息
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(
                            text='現在是要查詢資料庫裡是否有資料可以幫你分析，請輸入妳想要分析的股票代號'
                        )]
                    )
                )



            # 如果使用者輸入0，關閉訪問叔叔推薦股票
            if text == '0':
                # 關閉叔叔推薦股票
                TrueLimiter.enable_intelligent_prediction(False)
                # 關閉training_is_ready狀態
                training_validator.check_training_ready(False)
           
            




# quick_reply(快速選單的事件)PostbackEvent
@handler.add(PostbackEvent)
def handle_postback(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        postback_data = event.postback.data

        # 把quick_reply傳過來的資料分裝成股票代號和訊息
        postback_data_stock_code = postback_data.split(',')[0]
        postback_data_text = postback_data.split(',')[1]
        
   
        # 詳細資料的事件
        if postback_data_text == '詳細資料':
            df = WebCrawler_MIS_TWSE.webcrawler(postback_data_stock_code) # 丟入股票代號，獲取資料表

            # 用token傳訊息給使用者
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='詳細資料：\n' + str(df.T))]                    
                )
            )
        
        # 當盤成交價的事件
        if postback_data_text == '當盤成交價':
            df = WebCrawler_MIS_TWSE.webcrawler(postback_data_stock_code) # 丟入股票代號，獲取資料表

            # 用token傳訊息給使用者
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='當盤成交價：' + df['當盤成交價'].iloc[0] + '\n'
                                                 + '當盤成交量：' + df['當盤成交量'].iloc[0])]                    
                )
            )
        # 當盤成交價的事件
        if postback_data_text == '最佳五檔':
            df = WebCrawler_MIS_TWSE.webcrawler(postback_data_stock_code) # 丟入股票代號，獲取資料表

            # 從資料表選取需要的列
            df = pd.DataFrame(df, columns=['五檔賣價(從低到高，以_分隔資料)','五檔賣量(從低到高，以_分隔資料)',
                                           '五檔買價(從高到低，以_分隔資料)','五檔買量(從高到低，以_分隔資料)'])


            # 用token傳訊息給使用者
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=str(df.T))]                    
                )
            )




            
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)