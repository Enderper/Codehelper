"""
编码助手 - 主入口文件
向后兼容旧版本，直接导入 backend 模块
"""

from backend.main import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
