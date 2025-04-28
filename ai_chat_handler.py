from linebot.v3.messaging import (
    ReplyMessageRequest,  # 回覆訊息請求
    TextMessage           # 文字訊息物件
)

from allow_validator import allow_validator
from conversation_validator import conversation_validator



# 載入個性和腳色
import ai_character_settings
adjective=ai_character_settings.AiCharacterSettings.adjective # AI的個性形容詞
role=ai_character_settings.AiCharacterSettings.role           # AI的角色設定

# 引入 Google AI 相關模組（假設為自訂模組）
import google_ai

def google_ai_chat_function(text, line_bot_api, event):
# 過濾掉進入聊天模式的指令本身與退出指令
    if text not in ['', '0']:
        # 如果使用者輸入'r'，讓AI「失憶」（重置對話）
        if text == 'r':
            # 呼叫google_ai的ai_model方法，傳入特殊指令讓AI重置
            ai_return = google_ai.ai_chat(f'你是誰?', {adjective}+{role}, 'r')

            # 回覆訊息給使用者，提示可繼續對話
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text=f'快跟{role}說說話吧，或按0退出\n===================\n' + ai_return 
                    )]
                )
            )
            conversation_validator.enable_allow_conversation(True) # 允許接受新傳入對話

        # 處理一般聊天輸入
        if text != 'r':
            # 將使用者輸入傳給AI模型，取得回覆
            ai_return = google_ai.ai_chat(text, f'{adjective}+{role}', "1")

            # 回覆訊息給使用者，並提示可讓AI失憶或退出
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text=f'按r讓{role}失憶，或按0退出\n===================\n' + ai_return 
                    )]
                )
            )
            conversation_validator.enable_allow_conversation(True) # 允許接受新傳入對話

    # 如果使用者輸入0，關閉訪問叔叔AI（退出聊天模式）
    if text == '0':
        allow_validator.enable_ai_chat(False)
        conversation_validator.enable_allow_conversation(True) # 允許接受新傳入對話



# 引入 Local AI 相關模組（假設為自訂模組）
import local_ai

def local_ai_chat_function(text, line_bot_api, event):
# 過濾掉進入聊天模式的指令本身與退出指令
    if text not in ['', '0']:
        # 如果使用者輸入'r'，讓AI「失憶」（重置對話）
        if text == 'r':
            # 呼叫google_ai的ai_model方法，傳入特殊指令讓AI重置
            ai_return = local_ai.ai_chat(f'你是誰?', {adjective}+{role}, 'r')

            # 回覆訊息給使用者，提示可繼續對話
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text=f'快跟{role}說說話吧，或按0退出\n===================\n' + ai_return 
                    )]
                )
            )
            conversation_validator.enable_allow_conversation(True) # 允許接受新傳入對話

        # 處理一般聊天輸入
        if text != 'r':
            # 將使用者輸入傳給AI模型，取得回覆
            ai_return = local_ai.ai_chat(text, f'{adjective}+{role}', "1")

            # 回覆訊息給使用者，並提示可讓AI失憶或退出
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text=f'按r讓{role}失憶，或按0退出\n===================\n' + ai_return 
                    )]
                )
            )
            conversation_validator.enable_allow_conversation(True) # 允許接受新傳入對話

    # 如果使用者輸入0，關閉訪問叔叔AI（退出聊天模式）
    if text == '0':
        allow_validator.enable_ai_chat(False)
        conversation_validator.enable_allow_conversation(True) # 允許接受新傳入對話




# 引入 Local AI 相關模組（假設為自訂模組）
import rag_ai_chat

def rag_ai_chat_function(text, line_bot_api, event):
# 過濾掉進入聊天模式的指令本身與退出指令
    if text not in ['', '0']:
        # 如果使用者輸入'r'，讓AI「失憶」（重置對話）
        if text == 'r':
            # 呼叫google_ai的ai_model方法，傳入特殊指令讓AI重置
            ai_return = rag_ai_chat.rag_ai_chat(f'你是誰?', {adjective}, {role}, 'r')

            # 回覆訊息給使用者，提示可繼續對話
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text=f'快跟{role}說說話吧，或按0退出\n===================\n' + ai_return 
                    )]
                )
            )
            conversation_validator.enable_allow_conversation(True) # 允許接受新傳入對話

        # 處理一般聊天輸入
        if text != 'r':
            # 將使用者輸入傳給AI模型，取得回覆
            ai_return = rag_ai_chat.rag_ai_chat(text, f'{adjective}', f'{role}', "1")

            # 回覆訊息給使用者，並提示可讓AI失憶或退出
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text=f'按r讓{role}失憶，或按0退出\n===================\n' + ai_return 
                    )]
                )
            )
            conversation_validator.enable_allow_conversation(True) # 允許接受新傳入對話

    # 如果使用者輸入0，關閉訪問叔叔AI（退出聊天模式）
    if text == '0':
        allow_validator.enable_ai_chat(False)
        conversation_validator.enable_allow_conversation(True) # 允許接受新傳入對話