# 使用官方 Python 3.10 鏡像作為基礎鏡像
# 用python作為基礎鏡像通常可以適用在python開發的程式，因為裡面會有包含一些基礎依賴
FROM python:3.10

# 設定工作目錄
WORKDIR /app

# 這條指令將 requirements.txt 文件複製到 Docker 鏡像的當前工作目錄中，然後安裝依賴。
COPY requirements.txt .

# 安裝應用所需的依賴
# --no-cache-dir：這個選項告訴 pip 在安裝過程中不使用緩存。這樣做的好處是可以減少最終生成的 Docker 鏡像的大小
RUN pip install --no-cache-dir -r requirements.txt

# 這條指令將當前目錄下的所有文件和子目錄複製到 Docker 鏡像的當前工作目錄中。這通常包括應用程序的源代碼、配置文件和其他必要的資源。
COPY . .

# 暴露應用運行的端口
# EXPOSE 指令用來告訴 Docker 這個容器會在運行時監聽指定的端口。這是一種文檔化的方式，讓其他開發者知道容器的網絡接口。
EXPOSE 5000

# 定義容器啟動時執行的命令
# 這意味著 Python 解釋器將運行名為 app.py 的 Python 腳本
CMD ["python", "app.py"]