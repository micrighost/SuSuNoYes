import google.generativeai as genai
import os
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數（例如 GOOGLE_API_KEY）
# 這樣可以安全地管理金鑰，不建議直接寫在程式碼裡
load_dotenv() 
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))  # 設定 Gemini API 金鑰

# 驗證者類別：用來管理是否需要重置聊天歷史紀錄
class TrueLimiter:
    def __init__(self):
        self.history_restore = True  # 初始化時預設需要重置，並藉此創建對話歷史並清空
        self.chat_session = None     # 預設沒有 session

    def is_history_restore(self) -> bool:
        """
        判斷是否需要重置對話歷史
        Returns:
            bool: True=需要重置, False=不需要重置
        """
        return self.history_restore  # 直接返回布林值

# 建立驗證者實例，管理聊天紀錄狀態
true_limiter = TrueLimiter()

def ai_chat(user_input, sys_instruct, reset_input): 
    """
    使用 Gemini 模型生成對話回應，具備對話歷史重置功能

    參數說明：
        user_input (str): 使用者輸入的對話內容
        sys_instruct (str): 定義 AI 的角色設定與行為指令（如「可愛的妹妹」）
        reset_input (str): 控制指令，當值為 'r' 時會重置對話歷史，其他值不重置

    回傳：
        str: AI 生成的回應內容，格式為純文字

    流程說明：
    1. 設定生成式 AI 模型的參數（如隨機性、回應長度等）
    2. 初始化 Gemini 生成式模型（GenerativeModel），並注入角色指令
    3. 根據 reset_input 判斷是否重置聊天歷史
    4. 若需重置，則建立新的 chat session
    5. 使用 chat session 發送訊息並取得 Gemini 回應
    6. 回傳 AI 回應內容（純文字）
    """

    # 設定生成式 AI 模型的參數配置
    generation_config = {
        "temperature": 1,       # 控制生成隨機性 (0.0~2.0)，1 為中等創造力
        "top_p": 0.95,          # 核採樣參數，保留累積機率 95% 的候選詞
        "top_k": 40,            # 從前 40 個最佳候選詞中採樣
        "max_output_tokens": 8192,  # 限制回應最大 token 數量，避免回應過長
        "response_mime_type": "text/plain",  # 指定回應格式為純文字
    }

    # 定義 AI 的角色設定與行為指令
    sys_instruct = (str(sys_instruct))

    # 初始化生成式模型實例，指定模型版本與參數
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",         # 指定 Gemini 1.5 flash 版本（可依需求更換）
        generation_config=generation_config,   # 套用上方生成參數
        system_instruction=sys_instruct        # 注入角色設定（如「可愛的妹妹」）
    )

    # 處理重置機制
    if reset_input == 'r':  # 當收到重置指令時
        true_limiter.history_restore = True    # 觸發歷史紀錄重置標記

    # 檢查是否需要初始化新對話
    if true_limiter.is_history_restore():  # 若需重置
        # 建立全新對話 session 並清空歷史紀錄
        # history=[] 代表對話歷史為空，可改為預載入歷史訊息
        true_limiter.chat_session = model.start_chat(history=[])
        true_limiter.history_restore = False  # 關閉重置標記

    # 發送使用者輸入至 AI 模型並獲取回應
    # chat_session 會自動維護完整的對話歷史，不需手動拼接
    response = true_limiter.chat_session.send_message(
        str(user_input)  # 確保輸入為字串格式
    )

    # 將 AI 回應轉換為字串格式並返回
    return str(response.text)



