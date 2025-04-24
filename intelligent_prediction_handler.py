
from linebot.v3.messaging import (
    ReplyMessageRequest,  # 回覆訊息請求
    ImageMessage,         # 圖片訊息物件
    TextMessage           # 文字訊息物件
)



# 引入智慧預測模組（假設為自訂模組）
import intelligent_prediction


def intelligent_prediction_handler(text, line_bot_api, event, allow_validator, training_validator, get_https_image_url):
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