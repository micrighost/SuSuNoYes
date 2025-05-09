class TrainingReadyValidator:
    """訓練狀態管理器，負責以下功能：
    - 記錄股票代碼
    - 管理訓練數據
    - 控制訓練流程狀態
    並支援多用戶狀態管理
    """
    
    def __init__(self):
        """初始化多用戶訓練狀態字典
        
        Attributes:
            _user_states (dict): 儲存多用戶狀態，key為user_id，value為該用戶狀態字典
                - ticker (str): 股票代碼 (格式: XXXX.TW)
                - is_ready (bool): 訓練準備完成標誌
                - X_train: 訓練特徵數據 (numpy.ndarray)
                - y_train: 訓練目標數據 (numpy.ndarray)
        """
        self._user_states = {}

    def _init_user_state(self, user_id: str):
        """初始化指定用戶的狀態，若尚未存在則建立預設值"""
        if user_id not in self._user_states:
            self._user_states[user_id] = {
                'ticker': "",
                'is_ready': False,
                'X_train': None,
                'y_train': None,
            }

    def check_training_ready(self, user_id: str) -> bool:
        """檢查指定用戶的訓練準備狀態
        
        Args:
            user_id (str): 用戶ID
        
        Returns:
            bool: True=可開始訓練, False=需準備數據
        """

        # 確保該用戶在狀態字典中有初始化的狀態資料（如果沒有，會建立一筆預設狀態）
        self._init_user_state(user_id)

        # 回傳該用戶目前的訓練準備狀態，True 表示準備完成，可以開始訓練
        return self._user_states[user_id]['is_ready']

    def set_training_data(self, user_id: str, X_train, y_train) -> None:
        """設置指定用戶的訓練數據集
        
        Args:
            user_id (str): 用戶ID
            X_train (np.ndarray): 特徵數據矩陣 (shape: [samples, features])
            y_train (np.ndarray): 目標數據向量 (shape: [samples])
        """
        self._init_user_state(user_id)
        self._user_states[user_id]['X_train'] = X_train
        self._user_states[user_id]['y_train'] = y_train

    def mark_as_ready(self, user_id: str, ready: bool) -> None:
        """設置指定用戶的訓練準備完成標誌
        
        Args:
            user_id (str): 用戶ID
            ready (bool): 
                True - 數據準備完成，進入訓練階段
                False - 重置訓練狀態，清除數據
        """
        self._init_user_state(user_id)
        self._user_states[user_id]['is_ready'] = ready
        if not ready:
            # 若重置狀態，清空該用戶的股票代碼與訓練數據
            self._user_states[user_id]['ticker'] = ""
            self._user_states[user_id]['X_train'] = None
            self._user_states[user_id]['y_train'] = None

    def set_ticker(self, user_id: str, ticker: str) -> None:
        """設置指定用戶的股票代碼
        
        Args:
            user_id (str): 用戶ID
            ticker (str): 股票代碼 (格式: XXXX.TW)
        """
        self._init_user_state(user_id)
        self._user_states[user_id]['ticker'] = ticker

    def get_ticker(self, user_id: str) -> str:
        """取得指定用戶的股票代碼
        
        Args:
            user_id (str): 用戶ID
        
        Returns:
            str: 股票代碼
        """
        self._init_user_state(user_id)
        return self._user_states[user_id]['ticker']


# 實例化訓練狀態驗證器
training_validator = TrainingReadyValidator()