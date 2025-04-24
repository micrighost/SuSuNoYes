from linebot.v3.messaging import (
    ReplyMessageRequest,  # 回覆訊息請求
    TextMessage           # 文字訊息物件
)

# 引入 Google AI 相關模組（假設為自訂模組）
import google_ai


def ai_chat_handler(text, line_bot_api, event, allow_validator):
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