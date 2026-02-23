"""
配置模块 - 管理应用配置和环境变量
"""

import os
from dotenv import load_dotenv

load_dotenv(".env")

API_KEY = os.getenv("SILICONFLOW_API_KEY")
MODEL_NAME = "Qwen/Qwen2.5-Coder-7B-Instruct"
BASE_URL = "https://api.siliconflow.cn/v1"
