class AllowValidator:
    """功能權限集中控制器"""
    def __init__(self):
        """初始化所有功能權限開關"""
        self.allow_fetch_stock_data = False  # 股票數據爬取權限
        self.allow_ai_chat = False      # AI 聊天功能權限
        self.allow_intelligent_prediction = False  # 智能預測權限

    def is_allow_fetch_stock_data(self) -> bool:
        """檢查股票數據爬取權限"""
        return self.allow_fetch_stock_data  # 直接返回布林值

    def is_allow_ai_chat(self) -> bool:
        """檢查 AI 聊天功能權限"""
        return self.allow_ai_chat

    def is_allow_intelligent_prediction(self) -> bool:
        """檢查智能預測功能權限"""
        return self.allow_intelligent_prediction
    

    # 新增權限切換方法
    def enable_fetch_stock_data(self, enable: bool):
        """設置股票數據爬取權限"""
        self.allow_fetch_stock_data = enable

    def enable_ai_chat(self, enable: bool):
        """設置 AI 聊天功能權限"""
        self.allow_ai_chat = enable

    def enable_intelligent_prediction(self, enable: bool):
        """設置智能預測功能權限"""
        self.allow_intelligent_prediction = enable

# 實例化權限控制器
allow_validator = AllowValidator()