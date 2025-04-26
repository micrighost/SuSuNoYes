

from linebot.v3.messaging import (
    ReplyMessageRequest,  # 回覆訊息請求
    QuickReply,           # 快速回覆
    QuickReplyItem,       # 快速回覆項目
    PostbackAction,       # 回傳動作
    TextMessage           # 文字訊息物件
)

import get_https_url

# 引入自訂的台灣證交所資料爬蟲模組
import WebCrawler_MIS_TWSE

from allow_validator import allow_validator

# 載入個性和腳色
import ai_character_settings
adjective=ai_character_settings.AiCharacterSettings.adjective # AI的個性形容詞
role=ai_character_settings.AiCharacterSettings.role           # AI的角色設定

def fetch_stock_data_handler(text, line_bot_api, event):
    # 驗證股票代號是否有效（檢查是否能取得資料）
    if WebCrawler_MIS_TWSE.webcrawler_true(text):
        
        # ---------------------------
        # 設定快速選單圖示路徑
        # ---------------------------
        details_icon = get_https_url.get_https_image_url('自以為是的佩佩切出.png')
        current_transaction_price_icon = get_https_url.get_https_image_url('快樂的佩佩.png')
        best_five_tick_icon = get_https_url.get_https_image_url('悲傷的佩佩.png')
        datetime_icon = get_https_url.get_https_image_url('calendar.png')
        date_icon = get_https_url.get_https_image_url('calendar.png')
        time_icon = get_https_url.get_https_image_url('time.png')

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
                            text=f'{role}要給你報，請選擇你要的功能，你不選擇就算了',
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
    elif not WebCrawler_MIS_TWSE.webcrawler_true(text) and text not in ['', '0']:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f'沒有這股票不要騙{role}，給我輸入股票代號，或按0退出')]
            )
        )

    # ---------------------------
    # 處理退出指令
    # ---------------------------
    if text == '0':
        # 關閉爬蟲模式
        allow_validator.enable_fetch_stock_data(False)