class ConversationValidator:
    """對話權限集中控制器，用 user_id 管理多用戶狀態"""
    def __init__(self):
        """初始化多用戶狀態字典"""
        self._user_states = {}  # key: user_id, value: bool (是否允許對話)

    def _get_state(self, user_id: str) -> bool:
        """取得指定用戶的對話權限狀態，預設 True"""
        # 檢查 user_id 是否已存在於狀態字典中
        if user_id in self._user_states:
            # 如果存在，回傳該用戶目前的對話權限狀態 (True 或 False)
            return self._user_states[user_id]
        else:
            # 如果不存在，表示該用戶尚未被設定過狀態
            # 預設回傳 True，代表允許對話
            # 注意：此處並不會將預設值寫入字典，只是查詢時的預設回傳值
            return True

    def is_allow_conversation(self, user_id: str) -> bool:
        """檢查指定用戶是否允許對話"""
        return self._get_state(user_id)

    def enable_allow_conversation(self, user_id: str, enable: bool):
        """設置指定用戶的對話權限"""
        self._user_states[user_id] = enable


# 實例化權限控制器
conversation_validator = ConversationValidator()