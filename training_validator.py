class TrainingReadyValidator:
    """訓練狀態管理器"""
    def __init__(self):
        """初始化訓練狀態相關參數"""
        self.ticker: str = ""            # 股票代碼
        self.is_ready: bool = False      # 準備訓練完成標誌
        self.X_train = None              # 訓練特徵數據
        self.y_train = None              # 訓練目標數據

    def check_training_ready(self) -> bool:
        """檢查訓練準備是否完成"""
        return self.is_ready  # 直接返回布林值

    # 新增訓練數據設置方法
    def set_training_data(self, X_train, y_train):
        """設置訓練數據"""
        self.X_train = X_train
        self.y_train = y_train

    def mark_as_ready(self, ready: bool):
        """標記訓練狀態"""
        self.is_ready = ready

# 實例化訓練狀態驗證器
training_validator = TrainingReadyValidator()