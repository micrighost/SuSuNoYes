from linebot.v3.messaging import (
    TemplateMessage,      # 模板訊息
    CarouselTemplate,     # 輪播模板
    CarouselColumn,       # 輪播欄位
    URIAction,            # 網址動作
    ReplyMessageRequest   # 回覆訊息請求
)


# 引入 Flask 的 request
from flask import request

def generate_social_media_carousel():
    """生成 carousel_message 用來填充要回覆的 messages """

    def get_https_image_url(filename):
        """生成 HTTPS 圖片 URL"""
        # 獲取當前服務器根 URL 並拼接圖片路徑
        # 強制轉換為 HTTPS（LINE 要求圖片必須使用 HTTPS）
        base_url = request.url_root.replace("http://", "https://")
        return f"{base_url}static/{filename}"

    # 圖片資源
    eating_meat = get_https_image_url('eating_meat.gif')
    
    instagram_icon = get_https_image_url('instagram.png')
    github_icon = get_https_image_url('github.png')

    # 輪播模板結構
    carousel_template = CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url=instagram_icon,
                title='這是Deemo的IG',
                text='我要吃肉',
                actions=[
                    URIAction(
                        label='按我前往 IG',
                        uri='https://www.instagram.com/deemo9067?igsh=MXdkdnQyMXIwbmxwcQ=='
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url=github_icon,
                title='這是Deemo的GitHub',
                text='我的小小代碼庫',
                actions=[
                    URIAction(
                        label='按我前往 GitHub',
                        uri='https://github.com/micrighost'
                    )
                ]
            )
        ]
    )

    return TemplateMessage(
        alt_text='你也想認識Deemo?', # 顯示的預覽訊息
        template=carousel_template
    )


def reply_with_carousel(line_bot_api, reply_token):
    """
    傳入line_bot_api和reply_token，把Deemo訊息用輪播方式呈現
    
    參數:
        line_bot_api：
            這是 LINE Messaging API 的物件，用來與 LINE 平台溝通，發送各種訊息。
        event.reply_token：
            這是 LINE 傳來的事件物件中的回覆權杖，每次用戶互動時 LINE 伺服器都會給一個唯一的 token，必須用這個 token 才能正確回覆該用戶。
    """
    carousel_message = generate_social_media_carousel()
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages =[carousel_message]
        )
    )


