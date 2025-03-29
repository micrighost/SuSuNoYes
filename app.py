

# 引入WebCrawler_MIS_TWSE
import WebCrawler_MIS_TWSE

# 引入google_ai
import google_ai

import pandas as pd

import os
from dotenv import load_dotenv


from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    BroadcastRequest,
    PushMessageRequest,
    MulticastRequest,
    ReplyMessageRequest,
    TextMessage,
    Emoji,
    VideoMessage,
    AudioMessage,
    LocationMessage,
    StickerMessage,
    ImageMessage,
    ConfirmTemplate,
    TemplateMessage,
    ButtonsTemplate,
    CarouselTemplate,
    CarouselColumn,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    MessageAction,
    URIAction,
    PostbackAction,
    DatetimePickerAction,
    CameraAction,
    CameraRollAction,
    LocationAction,
    QuickReply,
    QuickReplyItem,
    


)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent
)

app = Flask(__name__)

# 載入.env
load_dotenv() 
configuration = Configuration(access_token=os.getenv('YOUR_CHANNEL_ACCESS_TOKEN')) # YOUR_CHANNEL_ACCESS_TOKEN
handler = WebhookHandler(os.getenv('YOUR_CHANNEL_SECRET')) # YOUR_CHANNEL_SECRET


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


# 創建一個驗證者，用來檢查現在是否需要訪問爬蟲
class TureLimiter:
    def __init__(self):
        self.allow_request = False
        self.allow_ai_susu_chat = False

    def is_allowed(self):

        if self.allow_request == True:
            return True
        return False
    
    def is_allowed_ai_susu_chat(self):

        if self.allow_ai_susu_chat == True:
            return True
        return False
    

# 創建一個驗證者實例
ture_limiter = TureLimiter()





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
            ture_limiter.allow_request = True
            # 如果訪問叔叔AI開啟，則關閉其他狀態(進到新的狀態前就把舊狀態關起來)
            ture_limiter.allow_ai_susu_chat = False



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
            ture_limiter.allow_ai_susu_chat = True
            # 如果訪問爬蟲狀態開啟，則關閉其他狀態(進到新的狀態前就把舊狀態關起來)
            ture_limiter.allow_request = False




#==========================================================
        # 如果訪問爬蟲已經開啟則進入循環
        if ture_limiter.is_allowed():
            print("我有盡到1")

            # 驗證是否有辦法抓到資料
            if WebCrawler_MIS_TWSE.webcrawler_ture(text):
                
                # 載入快速選單圖片
                details_icon = request.url_root + 'static/自以為是的佩佩切出.png'
                details_icon = details_icon.replace("http", "https")


                current_transaction_price_icon = request.url_root + 'static/快樂的佩佩.png'
                current_transaction_price_icon  = current_transaction_price_icon.replace("http", "https")

                best_five_tick_icon = request.url_root + 'static/悲傷的佩佩.png'
                best_five_tick_icon  = best_five_tick_icon.replace("http", "https")


                datetime_icon = request.url_root + 'static/calendar.png'
                datetime_icon = datetime_icon.replace("http", "https")
                date_icon = request.url_root + 'static/calendar.png'
                date_icon = date_icon.replace("http", "https")
                time_icon = request.url_root + 'static/time.png'
                time_icon = time_icon.replace("http", "https")

                
                # details_icon = "https://cdn2.ettoday.net/images/4224/4224901.jpg"
                # current_transaction_price_icon = "https://cdn2.ettoday.net/images/4224/4224901.jpg"
                # best_five_tick_icon  = "https://cdn2.ettoday.net/images/4224/4224901.jpg"
                # datetime_icon = "https://cdn2.ettoday.net/images/4224/4224901.jpg"
                # date_icon = "https://cdn2.ettoday.net/images/4224/4224901.jpg"
                # time_icon = "https://cdn2.ettoday.net/images/4224/4224901.jpg"
                print(details_icon)

                
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
                    ture_limiter.allow_request = False

                
            # 如果使用者輸入0，關閉訪問爬蟲狀態
            if text == '0':

                # 關閉用4個數字訪問爬蟲
                ture_limiter.allow_request = False



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




        # 如果訪問叔叔AI已經開啟則進入循環
        if ture_limiter.is_allowed_ai_susu_chat():
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
                ture_limiter.allow_ai_susu_chat = False





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
                    messages=[TextMessage(text='當盤成交價：' + df['當盤成交價'][0] + '\n'
                                                 + '當盤成交量：' + df['當盤成交量'][0])]                    
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
    app.run()
