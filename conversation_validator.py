class ConversationValidator:
    """對話權限集中控制器"""
    def __init__(self):
        """初始化所有功能權限開關"""
        self.allow_conversation = True  # 預設可以接受對話

    def is_allow_conversation(self) -> bool:
        """檢查接受對話權限"""
        return self.allow_conversation  # 直接返回布林值
    
    # 權限切換方法
    def enable_allow_conversation(self, enable: bool):
        """設置接受對話權限"""
        self.allow_conversation = enable


# 實例化權限控制器
conversation_validator = ConversationValidator()