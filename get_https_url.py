# 引入 request
from flask import request


def get_https_image_url(filename):
    """生成 HTTPS 圖片 URL"""
    # 獲取當前服務器根 URL 並拼接圖片路徑
    # 強制轉換為 HTTPS（LINE 要求圖片必須使用 HTTPS）
    base_url = request.url_root.replace("http://", "https://")
    return f"{base_url}static/{filename}"