# class TrainingReadyValidator:
#     """訓練狀態管理器"""
#     def __init__(self):
#         """初始化訓練狀態相關參數"""
#         self.ticker: str = ""            # 股票代碼
#         self.is_ready: bool = False      # 準備訓練完成標誌
#         self.X_train = None              # 訓練特徵數據
#         self.y_train = None              # 訓練目標數據

#     def check_training_ready(self) -> bool:
#         """檢查訓練準備是否完成"""
#         return self.is_ready  # 直接返回布林值

#     # 新增訓練數據設置方法
#     def set_training_data(self, X_train, y_train):
#         """設置訓練數據"""
#         self.X_train = X_train
#         self.y_train = y_train

#     def mark_as_ready(self, ready: bool):
#         """標記訓練狀態"""
#         self.is_ready = ready

# # 實例化訓練狀態驗證器
# training_validator = TrainingReadyValidator()



class TrainingReadyValidator:
    """訓練狀態管理器，負責以下功能：
    - 記錄股票代碼
    - 管理訓練數據
    - 控制訓練流程狀態
    """
    
    def __init__(self):
        """初始化訓練狀態相關參數
        
        Attributes:
            ticker (str):   股票代碼 (格式: XXXX.TW)
            is_ready (bool): 訓練準備完成標誌
            X_train:        訓練特徵數據 (numpy.ndarray)
            y_train:        訓練目標數據 (numpy.ndarray)
        """
        self.ticker: str = ""
        self.is_ready: bool = False
        self.X_train = None 
        self.y_train = None 

    def check_training_ready(self) -> bool:
        """檢查訓練準備狀態
        
        Returns:
            bool: True=可開始訓練, False=需準備數據
        """
        return self.is_ready

    def set_training_data(self, X_train, y_train) -> None:
        """設置訓練數據集
        
        Args:
            X_train (np.ndarray): 特徵數據矩陣 (shape: [samples, features])
            y_train (np.ndarray): 目標數據向量 (shape: [samples])
        """
        self.X_train = X_train
        self.y_train = y_train

    def mark_as_ready(self, ready: bool) -> None:
        """設置訓練準備完成標誌
        
        Args:
            ready (bool): 
                True - 數據準備完成，進入訓練階段
                False - 重置訓練狀態，清除數據
        """
        self.is_ready = ready

# 實例化訓練狀態驗證器
training_validator = TrainingReadyValidator()