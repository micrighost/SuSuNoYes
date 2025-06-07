
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


# 載入個性和腳色
import ai_character_settings
adjective=ai_character_settings.AiCharacterSettings.adjective # AI的個性形容詞
role=ai_character_settings.AiCharacterSettings.role           # AI的角色設定



from validators  import allow_validator
from validators  import training_validator
from validators  import conversation_validator


def set_states(user_id, fetch=False, chat=False, predict=False, train=False):
    """集中管理指定用戶的所有狀態設置"""
    allow_validator.allow_validator.enable_fetch_stock_data(user_id, fetch)
    allow_validator.allow_validator.enable_ai_chat(user_id, chat)
    allow_validator.allow_validator.enable_intelligent_prediction(user_id, predict)
    training_validator.training_validator.mark_as_ready(user_id, train)

def is_any_state_active(user_id):
    """檢查指定用戶是否有任一主要狀態激活"""
    return any([
        allow_validator.allow_validator.is_allow_fetch_stock_data(user_id),
        allow_validator.allow_validator.is_allow_ai_chat(user_id),
        allow_validator.allow_validator.is_allow_intelligent_prediction(user_id)
    ])



# 防鎖死機制
import threading

# 用於管理每個用戶的計時器
timers = {}

def reset_conversation_after_delay(user_id, delay=60):
    """
    在 delay 秒後，將指定用戶的對話狀態重置為允許(True)。
    若在倒數期間再次呼叫，會重置倒數時間。

    參數：
        user_id (str): 需要重置狀態的用戶ID
        delay (int): 延遲秒數，預設60秒
    """

    def reset():
        conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)
        print(f"[Reset] 用戶 {user_id} 的對話狀態已經過 {delay} 秒，已被重置為允許。")
        
        # 計時器執行完畢，從字典移除
        timers.pop(user_id, None)

    # 如果已有計時器，先取消它
    if user_id in timers:
        timers[user_id].cancel()

    # 建立新的計時器並啟動
    timer = threading.Timer(delay, reset)
    timers[user_id] = timer
    timer.start()



# 監聽所有文字訊息事件
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # 初始化 LINE Messaging API 客戶端
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        text = event.message.text # 取得使用者輸入的文字內容
        user_id = event.source.user_id  # 取得用戶ID


        # 如果有訊息未處理完，那就讓客戶稍等
        if not conversation_validator.conversation_validator.is_allow_conversation(user_id):
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='上一則訊息還在處理中，請稍後再試喔！')]
                )
            )
            reset_conversation_after_delay(user_id=user_id, delay=60) # 在60秒後，將指定用戶的對話狀態重置為允許(True)
            return

    
        # 如果目前沒有訊息未處理完，那就可以接受新訊息
        if conversation_validator.conversation_validator.is_allow_conversation(user_id):
            conversation_validator.conversation_validator.enable_allow_conversation(user_id, False)  # 如果接受了新訊息，就拒絕其他訊息


            if text == 'Deemo':  # 當用戶輸入的訊息是「Deemo」時觸發
                import Deemo_carousel_template  # 導入自定義的 Deemo_carousel_template 模組
                Deemo_carousel_template.reply_with_deemo_carousel(
                    line_bot_api,       # 傳入 LINE Bot API 實例，用於發送訊息
                    event.reply_token,   # 傳入當前事件的回覆令牌，確保訊息回覆給正確用戶
                    user_id=user_id
                )
                text = ""


            if is_any_state_active(user_id) == False:  # 帶入 user_id
                # 處理「股票查詢」指令
                if text in ['1', '叔叔我要報', '叔叔我要抱']:
                    # 回覆操作指引
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text=f'{role}要給你報，請輸入股票代號，或按0退出')]
                        )
                    )
                    text = ""
                    conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)  # 允許接受新傳入對話
                    
                    # 狀態機設定，帶入 user_id
                    set_states(user_id, fetch=True)

                # 處理「聊天模式」指令    
                elif text in ['2', '我要撩叔叔', '我要聊叔叔']:
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text=f'{role}跟你聊，請輸入你要的聊的，或按0退出')]
                        )
                    )
                    text = ""
                    conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)  # 允許接受新傳入對話

                    # 狀態機設定，帶入 user_id
                    set_states(user_id, chat=True)

                # 處理「股票分析」指令
                elif text in ['3', '叔叔我要分析']:
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text=f'{role}給你分析，請輸入你要詢問的股票代號，或按0退出')]
                        )
                    )
                    text = ""
                    conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)  # 允許接受新傳入對話

                    # 狀態機設定，帶入 user_id
                    set_states(user_id, predict=True)
                
                # 如果是無效字段，就繼續接受傳入對話
                else :
                    conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)  # 允許接受新傳入對話


#===============================================================================================

            # 檢查是否處於爬蟲模式（允許查詢股票資料的狀態），帶入 user_id
            if allow_validator.allow_validator.is_allow_fetch_stock_data(user_id):

                from handlers import fetch_stock_data_handler
                fetch_stock_data_handler.fetch_stock_data_handler(
                    text=text,
                    line_bot_api=line_bot_api,
                    event=event,
                    user_id=user_id
                )
                
            # 如果訪問叔叔AI（聊天模式）已經開啟則進入循環，帶入 user_id
            if allow_validator.allow_validator.is_allow_ai_chat(user_id):
                from handlers import ai_chat_handler
                # google_ai_chat_function >> 用google的AI
                # local_ai_chat_function >> 用本地的AI
                # rag_ai_chat_function >> 智能聊天與網路檢索（RAG）整合主流程，但是api消耗較大，可以換成本地AI
                ai_chat_handler.rag_ai_chat_function(  # 可替換為其他的方法(function)
                    text=text,
                    line_bot_api=line_bot_api,
                    event=event,
                    user_id=user_id
                )


            # 如果「智能預測模式」已開啟，帶入 user_id
            if allow_validator.allow_validator.is_allow_intelligent_prediction(user_id):
                from handlers import intelligent_prediction_handler
                # ANN_OHLCV_output5_intelligent_prediction_function >> 輸入開高低收，5輸出
                # ANN_OHLCV_output2_intelligent_prediction_function >> 輸入開高低收，2輸出
                # ANN_3DayKbar_output5_intelligent_prediction_function >> 輸入3天k棒，5輸出
                # ANN_3DayKbar_output2_intelligent_prediction_function >> 輸入3天k棒，2輸出  
                #   
                # 可替換為其他的方法(function)        
                intelligent_prediction_handler.ANN_3DayKbar_output2_intelligent_prediction_function( 
                    text=text,
                    line_bot_api=line_bot_api,
                    event=event,
                    user_id=user_id
                )
            

            
from handlers import postback_handler

# 處理 LINE 的 PostbackEvent (快速選單回傳事件)
@handler.add(PostbackEvent) # 註冊 Postback 事件處理器
def postback_event_handler(event):
    postback_handler.handle_postback(event, configuration)


            
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)