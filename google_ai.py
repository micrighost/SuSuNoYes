import google.generativeai as genai


import os
from dotenv import load_dotenv



# 載入.env
load_dotenv() 
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))



# 創建一個驗證者，用來檢查現在是否需要洗掉之前的聊天紀錄history
class TureLimiter:
    def __init__(self):
        self.history_restore = True
    
    def is_history_restore(self):
        if self.history_restore == True:
            return True
        
        if self.history_restore == False:
            return False
        


    
# 創建一個驗證者實例
ture_limiter = TureLimiter()



def ai_model(user_input,r_input): # r_input = 接受到r會清空聊天紀錄
    # Create the model
    generation_config = {
        "temperature": 1, # 選用設定。控制輸出的隨機性。 值的範圍為 [0.0, 2.0]。
        
        # Top-p 也是用來控製材料策略的，不過它是挑選評分（機率）加起來達到 p的最小集合作為候選集，然後從中隨機選一個作為下一個輸出的字。 
        # p值為0-1之間，通常設定為較高的值，例如0.75，這樣可以過濾掉那些低評分的長尾。
        "top_p": 0.95,

        # Top-k 是用來控制取樣策略的，也就是從所有結果中依照評分排名，取前 k 個字作為候選集，然後從中隨機選一個作為下一個輸出的字。 
        # 當k=1 時，就和貪心策略效果是一樣的，總是選排名第一個的那個。
        "top_k": 40, 


        "max_output_tokens": 8192, # 回應候選項中可納入的符記數量上限
        "response_mime_type": "text/plain", # 產生的候選文字類型。text/plain：(預設) 純文字輸出。
    }


    # 腳色設定
    sys_instruct="你是一個整天懶惰的妹妹，很愛哥哥，很溫柔，很可愛，有點害羞，很愛撒嬌，愛用顏文字和可愛貼圖，使用繁體中文"

    model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # 選用模型
    generation_config=generation_config, # 載入參數
    system_instruction=sys_instruct # 載入腳色設定
    )

    # 如果接受到'r'，就把就把歷史聊天清空設定為True
    if r_input == 'r':
        ture_limiter.history_restore = True

    # 預設歷史聊天清空為True，觸發後關閉，開始不斷聊天，直到接受到重製的命令
    if ture_limiter.is_history_restore() == True:

        if ture_limiter.is_history_restore():
            # 創建一個儲存空間來存之前的對話
            ture_limiter.chat_session = model.start_chat(
            history=[]
            )
            ture_limiter.history_restore = False # 關閉歷史聊天清空

    
    # 把使用者訊息輸入模型得到回答
    response = ture_limiter.chat_session.send_message(str(user_input))



    return str(response.text)






