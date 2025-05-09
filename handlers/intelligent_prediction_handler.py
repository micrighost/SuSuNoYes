
from linebot.v3.messaging import (
    ReplyMessageRequest,  # 回覆訊息請求
    ImageMessage,         # 圖片訊息物件
    TextMessage           # 文字訊息物件
)


from validators import allow_validator
from validators import training_validator
from validators import conversation_validator


# 引入生成圖片路徑模組
import get_https_url

# 引入智慧預測模組（假設為自訂模組）
from intelligent_prediction_strategies import ANN_OHLCV_output5_intelligent_prediction

def ANN_OHLCV_output5_intelligent_prediction_function(text, line_bot_api, event, user_id):

    # 檢查是否已完成數據準備階段
    if training_validator.training_validator.check_training_ready(user_id) == False:
        
        # 驗證輸入是否為4位數股票代號
        if text.isdigit() and len(text) == 4:
            
            # 格式化成台灣股票代號格式 (如 2330.TW)
            training_validator.training_validator.ticker = text + '.TW'
            
            # 抓取歷史股價數據
            df = ANN_OHLCV_output5_intelligent_prediction.fetch_stock_data(training_validator.training_validator.ticker)
            
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
                # 允許接受新的對話傳入
                conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)

            else:      
                # 準備訓練數據 (不洗牌以保留時間序列特性)
                X_train, y_train = ANN_OHLCV_output5_intelligent_prediction.prepare_data(df, shuffle=False)
                
                # 標記數據準備完成
                training_validator.training_validator.mark_as_ready(user_id, True)
                
                # 儲存訓練數據到多用戶狀態（你需要改 training_validator 支援多用戶）
                training_validator.training_validator.X_train = X_train
                training_validator.training_validator.y_train = y_train

                # 清空輸入內容避免干擾後續流程
                text = ""

                # 數據抓取成功回應
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(
                            text='我抓到資料了，接下來將要訓練模型，請輸入妳想要的訓練次數1-999，訓練時間依訓練次數會有所不同，並且不要覺得會很快'
                        )]
                    )
                )
                # 允許接受新的對話傳入
                conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)
                


        # 處理無效輸入
        elif ((text.isdigit() == False) or len(text) != 4) and text not in ["0", ""]:
            print(f"無效輸入: {text}")
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='現在是要查詢資料庫裡是否有資料可以幫你分析，請輸入妳想要分析的股票代號'
                    )]
                )
            )
            # 允許接受新的對話傳入
            conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)

    # 數據準備完成後的模型訓練階段
    if training_validator.training_validator.check_training_ready(user_id) and text not in ['', '0']:
        
        # 驗證訓練次數輸入 (1-3位數)
        if text.isdigit() and (len(text) < 4):
            
            # 模型訓練參數設定
            epochs = int(text)
            batch_size = 5
            validation_split = 0.25
            
            # 啟動模型訓練
            model = ANN_OHLCV_output5_intelligent_prediction.train_model(
                training_validator.training_validator.X_train,
                training_validator.training_validator.y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split
            )
            
            # 獲取最新股價數據
            stock_data_today_df = ANN_OHLCV_output5_intelligent_prediction.fetch_stock_data_today(training_validator.training_validator.ticker)
            
            # 提取特徵數據
            X_test = stock_data_today_df[['open', 'high', 'low', 'close', 'volume']]
            
            # 執行預測
            predictions = ANN_OHLCV_output5_intelligent_prediction.prediction(model, training_validator.training_validator.X_train, X_test)
            
            # 轉換預測結果為文字描述
            status_descriptions = ANN_OHLCV_output5_intelligent_prediction.convert_status(predictions)
            
            # 生成模型準確率圖表連結
            details_icon = get_https_url.get_https_image_url('model_accuracy.png')
            
            # 重置訓練狀態
            training_validator.training_validator.mark_as_ready(user_id, False)   

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
            # 允許接受新的對話傳入
            conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)
            


        # 處理訓練階段的無效輸入
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='現在是要訓練模型，請輸入你想要的訓練次數1-999'
                    )]
                )
            )
            # 允許接受新的對話傳入
            conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)

    # 處理退出指令
    if text == '0':
        # 關閉智能預測模式
        allow_validator.allow_validator.enable_intelligent_prediction(user_id, False)
        # 重置訓練狀態
        training_validator.training_validator.mark_as_ready(user_id, False)
        # 允許接受新的對話傳入
        conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)


# 引入智慧預測模組（假設為自訂模組）
from intelligent_prediction_strategies import ANN_OHLCV_output2_intelligent_prediction

def ANN_OHLCV_output2_intelligent_prediction_function(text, line_bot_api, event, user_id):

    # 檢查是否已完成數據準備階段
    if training_validator.training_validator.check_training_ready(user_id) == False:
        
        # 驗證輸入是否為4位數股票代號
        if text.isdigit() and len(text) == 4:
            
            # 格式化成台灣股票代號格式 (如 2330.TW)
            training_validator.training_validator.ticker = text + '.TW'
            
            # 抓取歷史股價數據
            df = ANN_OHLCV_output2_intelligent_prediction.fetch_stock_data(training_validator.training_validator.ticker)
            
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
                # 允許接受新的對話傳入
                conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)

            else:               
                # 準備訓練數據 (不洗牌以保留時間序列特性)
                X_train, y_train = ANN_OHLCV_output2_intelligent_prediction.prepare_data(df, shuffle=False)
                
                # 標記數據準備完成
                training_validator.training_validator.mark_as_ready(user_id, True)
                
                # 儲存訓練數據到多用戶狀態（你需要改 training_validator 支援多用戶）
                training_validator.training_validator.X_train = X_train
                training_validator.training_validator.y_train = y_train
                
                # 清空輸入內容避免干擾後續流程
                text = ""

                # 數據抓取成功回應
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(
                            text='我抓到資料了，接下來將要訓練模型，請輸入妳想要的訓練次數1-999，訓練時間依訓練次數會有所不同，並且不要覺得會很快'
                        )]
                    )
                )
                # 允許接受新的對話傳入
                conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)

        # 處理無效輸入
        elif ((text.isdigit() == False) or len(text) != 4) and text not in ["0", ""]:
            print(f"無效輸入: {text}")
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='現在是要查詢資料庫裡是否有資料可以幫你分析，請輸入妳想要分析的股票代號'
                    )]
                )
            )
            # 允許接受新的對話傳入
            conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)

    # 數據準備完成後的模型訓練階段
    if training_validator.training_validator.check_training_ready(user_id) and text not in ['', '0']:
        
        # 驗證訓練次數輸入 (1-3位數)
        if text.isdigit() and (len(text) < 4):
            
            # 模型訓練參數設定
            epochs = int(text)
            batch_size = 5
            validation_split = 0.25
            
            # 啟動模型訓練
            model = ANN_OHLCV_output2_intelligent_prediction.train_model(
                training_validator.training_validator.X_train,
                training_validator.training_validator.y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split
            )
            
            # 獲取最新股價數據
            stock_data_today_df = ANN_OHLCV_output2_intelligent_prediction.fetch_stock_data_today(training_validator.training_validator.ticker)
            
            # 提取特徵數據
            X_test = stock_data_today_df[['open', 'high', 'low', 'close', 'volume']]
            
            # 執行預測
            predictions = ANN_OHLCV_output2_intelligent_prediction.prediction(model, training_validator.training_validator.X_train, X_test)
            
            # 轉換預測結果為文字描述
            status_descriptions = ANN_OHLCV_output2_intelligent_prediction.convert_status(predictions)
            
            # 生成模型準確率圖表連結
            details_icon = get_https_url.get_https_image_url('model_accuracy.png')

            # 重置訓練狀態
            training_validator.training_validator.mark_as_ready(user_id, False)
            
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
            # 允許接受新的對話傳入
            conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)
            

        # 處理訓練階段的無效輸入
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='現在是要訓練模型，請輸入你想要的訓練次數1-999'
                    )]
                )
            )
            # 允許接受新的對話傳入
            conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)

    # 處理退出指令
    if text == '0':
        # 關閉智能預測模式
        allow_validator.allow_validator.enable_intelligent_prediction(user_id, False)
        # 重置訓練狀態
        training_validator.training_validator.mark_as_ready(user_id, False)
        # 允許接受新的對話傳入
        conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)


# 引入智慧預測模組（假設為自訂模組）
from intelligent_prediction_strategies import ANN_3DayKbar_output5_intelligent_prediction

def ANN_3DayKbar_output5_intelligent_prediction_function(text, line_bot_api, event, user_id):

    # 檢查是否已完成數據準備階段
    if training_validator.training_validator.check_training_ready(user_id) == False:
        
        # 驗證輸入是否為4位數股票代號
        if text.isdigit() and len(text) == 4:
            
            # 格式化成台灣股票代號格式 (如 2330.TW)
            training_validator.training_validator.ticker = text + '.TW'
            
            # 抓取歷史股價數據
            df = ANN_3DayKbar_output5_intelligent_prediction.fetch_stock_data(training_validator.training_validator.ticker)
            
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
                # 允許接受新的對話傳入
                conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)
                
            else:              
                # 準備訓練數據 (不洗牌以保留時間序列特性)
                X_train, y_train = ANN_3DayKbar_output5_intelligent_prediction.prepare_data(df, shuffle=False)
                
                # 標記數據準備完成
                training_validator.training_validator.mark_as_ready(user_id, True)
                
                # 儲存訓練數據到多用戶狀態（你需要改 training_validator 支援多用戶）
                training_validator.training_validator.X_train = X_train
                training_validator.training_validator.y_train = y_train
                
                # 清空輸入內容避免干擾後續流程
                text = ""

                # 數據抓取成功回應
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(
                            text='我抓到資料了，接下來將要訓練模型，請輸入妳想要的訓練次數1-999，訓練時間依訓練次數會有所不同，並且不要覺得會很快'
                        )]
                    )
                )
                # 允許接受新的對話傳入
                conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)

        # 處理無效輸入
        elif ((text.isdigit() == False) or len(text) != 4) and text not in ["0", ""]:
            print(f"無效輸入: {text}")
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='現在是要查詢資料庫裡是否有資料可以幫你分析，請輸入妳想要分析的股票代號'
                    )]
                )
            )
            # 允許接受新的對話傳入
            conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)

    # 數據準備完成後的模型訓練階段
    if training_validator.training_validator.check_training_ready(user_id) and text not in ['', '0']:
        
        # 驗證訓練次數輸入 (1-3位數)
        if text.isdigit() and (len(text) < 4):
            
            # 模型訓練參數設定
            epochs = int(text)
            batch_size = 5
            validation_split = 0.25
            
            # 啟動模型訓練
            model = ANN_3DayKbar_output5_intelligent_prediction.train_model(
                training_validator.training_validator.X_train,
                training_validator.training_validator.y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split
            )
            
            # 獲取最新股價數據
            stock_data_today_df = ANN_3DayKbar_output5_intelligent_prediction.fetch_stock_data_today(training_validator.training_validator.ticker)
            
            # 提取特徵數據
            X_test = stock_data_today_df[['volume', 'k-2_status', 'k-1_status', 'k_status']]
    
            # 執行預測
            predictions = ANN_3DayKbar_output5_intelligent_prediction.prediction(model, training_validator.training_validator.X_train, X_test)
            
            # 轉換預測結果為文字描述
            status_descriptions = ANN_3DayKbar_output5_intelligent_prediction.convert_status(predictions)
            
            # 生成模型準確率圖表連結
            details_icon = get_https_url.get_https_image_url('model_accuracy.png')

            # 重置訓練狀態
            training_validator.training_validator.mark_as_ready(user_id, False)
            
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
            # 允許接受新的對話傳入
            conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)
            

        # 處理訓練階段的無效輸入
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='現在是要訓練模型，請輸入你想要的訓練次數1-999'
                    )]
                )
            )
            # 允許接受新的對話傳入
            conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)

    # 處理退出指令
    if text == '0':
        # 關閉智能預測模式
        allow_validator.allow_validator.enable_intelligent_prediction(user_id, False)
        # 重置訓練狀態
        training_validator.training_validator.mark_as_ready(user_id, False)
        # 允許接受新的對話傳入
        conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)





# 引入智慧預測模組（假設為自訂模組）
from intelligent_prediction_strategies import ANN_3DayKbar_output2_intelligent_prediction

def ANN_3DayKbar_output2_intelligent_prediction_function(text, line_bot_api, event, user_id):

    # 檢查是否已完成數據準備階段
    if training_validator.training_validator.check_training_ready(user_id) == False:
        
        # 驗證輸入是否為4位數股票代號
        if text.isdigit() and len(text) == 4:
            
            # 格式化成台灣股票代號格式 (如 2330.TW)
            training_validator.training_validator.ticker = text + '.TW'
            
            # 抓取歷史股價數據
            df = ANN_3DayKbar_output2_intelligent_prediction.fetch_stock_data(training_validator.training_validator.ticker)
            
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
                # 允許接受新的對話傳入
                conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)

            else:               
                # 準備訓練數據 (不洗牌以保留時間序列特性)
                X_train, y_train = ANN_3DayKbar_output2_intelligent_prediction.prepare_data(df, shuffle=False)
                
                # 標記數據準備完成
                training_validator.training_validator.mark_as_ready(user_id, True)
                
                # 儲存訓練數據到多用戶狀態（你需要改 training_validator 支援多用戶）
                training_validator.training_validator.X_train = X_train
                training_validator.training_validator.y_train = y_train
                
                # 清空輸入內容避免干擾後續流程
                text = ""

                # 數據抓取成功回應
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(
                            text='我抓到資料了，接下來將要訓練模型，請輸入妳想要的訓練次數1-999，訓練時間依訓練次數會有所不同，並且不要覺得會很快'
                        )]
                    )
                )
                # 允許接受新的對話傳入
                conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)

        # 處理無效輸入
        elif ((text.isdigit() == False) or len(text) != 4) and text not in ["0", ""]:
            print(f"無效輸入: {text}")
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='現在是要查詢資料庫裡是否有資料可以幫你分析，請輸入妳想要分析的股票代號'
                    )]
                )
            )
            # 允許接受新的對話傳入
            conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)

    # 數據準備完成後的模型訓練階段
    if training_validator.training_validator.check_training_ready(user_id) and text not in ['', '0']:
        
        # 驗證訓練次數輸入 (1-3位數)
        if text.isdigit() and (len(text) < 4):
            
            # 模型訓練參數設定
            epochs = int(text)
            batch_size = 5
            validation_split = 0.25
            
            # 啟動模型訓練
            model = ANN_3DayKbar_output2_intelligent_prediction.train_model(
                training_validator.training_validator.X_train,
                training_validator.training_validator.y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split
            )
            
            # 獲取最新股價數據
            stock_data_today_df = ANN_3DayKbar_output2_intelligent_prediction.fetch_stock_data_today(training_validator.training_validator.ticker)
            
            # 提取特徵數據
            X_test = stock_data_today_df[['volume', 'k-2_status', 'k-1_status', 'k_status']]
    
            # 執行預測
            predictions = ANN_3DayKbar_output2_intelligent_prediction.prediction(model, training_validator.training_validator.X_train, X_test)
            
            # 轉換預測結果為文字描述
            status_descriptions = ANN_3DayKbar_output2_intelligent_prediction.convert_status(predictions)
            
            # 生成模型準確率圖表連結
            details_icon = get_https_url.get_https_image_url('model_accuracy.png')

            # 重置訓練狀態
            training_validator.training_validator.mark_as_ready(user_id, False)
            
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
            # 允許接受新的對話傳入
            conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)
            

        # 處理訓練階段的無效輸入
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='現在是要訓練模型，請輸入你想要的訓練次數1-999'
                    )]
                )
            )
            # 允許接受新的對話傳入
            conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)

    # 處理退出指令
    if text == '0':
        # 關閉智能預測模式
        allow_validator.allow_validator.enable_intelligent_prediction(user_id, False)
        # 重置訓練狀態
        training_validator.training_validator.mark_as_ready(user_id, False)
        # 允許接受新的對話傳入
        conversation_validator.conversation_validator.enable_allow_conversation(user_id, True)








