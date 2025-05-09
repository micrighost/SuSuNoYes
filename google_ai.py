import google.generativeai as genai
import os
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數（例如 GOOGLE_API_KEY）
# 這樣可以安全地管理金鑰，不建議直接寫在程式碼裡
load_dotenv() 
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))  # 設定 Gemini API 金鑰

# 多用戶聊天狀態管理器：每個 user_id 都有自己獨立的 session 與重置狀態
class ChatLimiter:
    def __init__(self):
        self.user_states = {}  # key: user_id, value: {'history_restore': bool, 'chat_session': session}

    def _init_user_state(self, user_id):
        if user_id not in self.user_states:
            self.user_states[user_id] = {
                'history_restore': True,  # 預設需要重置
                'chat_session': None,
            }

    def is_history_restore(self, user_id) -> bool:
        """
        判斷指定用戶是否需要重置對話歷史
        Args:
            user_id (str): 用戶唯一識別ID
        Returns:
            bool: True=需要重置, False=不需要重置
        """
        self._init_user_state(user_id)
        return self.user_states[user_id]['history_restore']

    def set_history_restore(self, user_id, value: bool):
        """
        設定指定用戶是否需要重置對話歷史
        Args:
            user_id (str): 用戶唯一識別ID
            value (bool): True=重置, False=不重置
        """
        self._init_user_state(user_id)
        self.user_states[user_id]['history_restore'] = value

    def get_chat_session(self, user_id):
        """
        取得指定用戶的聊天 session
        Args:
            user_id (str): 用戶唯一識別ID
        Returns:
            chat_session: Gemini chat session 物件
        """
        self._init_user_state(user_id)
        return self.user_states[user_id]['chat_session']

    def set_chat_session(self, user_id, session):
        """
        設定指定用戶的聊天 session
        Args:
            user_id (str): 用戶唯一識別ID
            session: Gemini chat session 物件
        """
        self._init_user_state(user_id)
        self.user_states[user_id]['chat_session'] = session

# 建立 ChatLimiter 實例，管理多用戶聊天狀態
chat_limiter = ChatLimiter()

def ai_chat(user_input, sys_instruct, reset_input, user_id): 
    """
    使用 Gemini 模型生成對話回應，支援多用戶對話歷史與重置

    參數說明：
        user_input (str): 使用者輸入的對話內容
        sys_instruct (str): 定義 AI 的角色設定與行為指令
        reset_input (str): 控制指令，'r' 代表重置對話歷史
        user_id (str): 用戶唯一識別ID（每個用戶獨立 session）

    回傳：
        str: AI 生成的回應內容，格式為純文字
    """

    # 設定生成式 AI 模型的參數配置
    generation_config = {
        "temperature": 1,       # 控制生成隨機性 (0.0~2.0)，1 為中等創造力
        "top_p": 0.95,          # 核採樣參數，保留累積機率 95% 的候選詞
        "top_k": 40,            # 從前 40 個最佳候選詞中採樣
        "max_output_tokens": 8192,  # 限制回應最大 token 數量
        "response_mime_type": "text/plain",  # 指定回應格式為純文字
    }

    # 定義 AI 的角色設定與行為指令
    sys_instruct = str(sys_instruct)

    # 初始化生成式模型實例，指定模型版本與參數
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=sys_instruct
    )

    # 處理重置機制
    if reset_input == 'r':
        chat_limiter.set_history_restore(user_id, True)

    # 檢查是否需要初始化新對話
    if chat_limiter.is_history_restore(user_id):
        # 建立全新對話 session 並清空歷史紀錄
        chat_session = model.start_chat(history=[])  # 建立一個空的聊天陣列
        chat_limiter.set_chat_session(user_id, chat_session) # 用空的聊天陣列取代特定用戶的聊天陣列
        chat_limiter.set_history_restore(user_id, False) # 關必須要重置的狀態

    # 發送使用者輸入至 AI 模型並獲取回應（每個用戶 session 獨立）
    chat_session = chat_limiter.get_chat_session(user_id)
    response = chat_session.send_message(str(user_input))

    # 將 AI 回應轉換為字串格式並返回
    return str(response.text)