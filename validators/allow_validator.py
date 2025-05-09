class AllowValidator:
    """功能權限集中控制器，支援多用戶狀態管理"""
    def __init__(self):
        """初始化多用戶功能權限字典"""
        # key: user_id, value: dict，存放各功能權限布林值
        self._user_states = {}

    def _init_user_state(self, user_id: str):
        """初始化指定用戶的權限狀態，若不存在則建立預設值"""
        if user_id not in self._user_states:
            self._user_states[user_id] = {
                'fetch_stock_data': False,
                'ai_chat': False,
                'intelligent_prediction': False,
            }

    def is_allow_fetch_stock_data(self, user_id: str) -> bool:
        """檢查指定用戶的股票數據爬取權限"""
        self._init_user_state(user_id)
        return self._user_states[user_id]['fetch_stock_data']

    def is_allow_ai_chat(self, user_id: str) -> bool:
        """檢查指定用戶的 AI 聊天功能權限"""
        self._init_user_state(user_id)
        return self._user_states[user_id]['ai_chat']

    def is_allow_intelligent_prediction(self, user_id: str) -> bool:
        """檢查指定用戶的智能預測功能權限"""
        self._init_user_state(user_id)
        return self._user_states[user_id]['intelligent_prediction']

    def enable_fetch_stock_data(self, user_id: str, enable: bool):
        """設置指定用戶的股票數據爬取權限"""
        self._init_user_state(user_id)
        self._user_states[user_id]['fetch_stock_data'] = enable

    def enable_ai_chat(self, user_id: str, enable: bool):
        """設置指定用戶的 AI 聊天功能權限"""
        self._init_user_state(user_id)
        self._user_states[user_id]['ai_chat'] = enable

    def enable_intelligent_prediction(self, user_id: str, enable: bool):
        """設置指定用戶的智能預測功能權限"""
        self._init_user_state(user_id)
        self._user_states[user_id]['intelligent_prediction'] = enable


# 實例化多用戶權限控制器
allow_validator = AllowValidator()


