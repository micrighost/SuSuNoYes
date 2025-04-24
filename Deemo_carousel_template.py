from linebot.v3.messaging import (
    TemplateMessage,      # 模板訊息
    CarouselTemplate,     # 輪播模板
    CarouselColumn,       # 輪播欄位
    URIAction,            # 網址動作
    ReplyMessageRequest   # 回覆訊息請求
)


def reply_with_deemo_carousel(line_bot_api, reply_token, get_https_image_url):
    """
    傳入line_bot_api和reply_token和get_https_image_url，把Deemo的訊息用輪播方式呈現
    
    參數:
        line_bot_api：
            這是 LINE Messaging API 的物件，用來與 LINE 平台溝通，發送各種訊息。
        event.reply_token：
            這是 LINE 傳來的事件物件中的回覆權杖，每次用戶互動時 LINE 伺服器都會給一個唯一的 token，必須用這個 token 才能正確回覆該用戶。
        get_https_image_url：
            生成 HTTPS 圖片 URL的方法
    """

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

    carousel_message =  TemplateMessage(
        alt_text='你也想認識Deemo?', # 顯示的預覽訊息
        template=carousel_template
    )

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages =[carousel_message]
        )
    )
