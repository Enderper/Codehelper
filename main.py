"""
编码助手 - 阿里云 Qwen2.5-Coder API 集成
功能：代码生成、代码解释、代码改错
"""

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from openai import OpenAI
import os
from dotenv import load_dotenv
import uvicorn

# 加载 .env 文件中的环境变量
load_dotenv(".env")

# 测试打印
api_key = os.getenv("SILICONFLOW_API_KEY")
print(f"API Key loaded: {api_key[:10] if api_key else 'None'}...")
# 初始化 OpenAI 客户端（兼容 SiliconFlow API）
client = OpenAI(
    api_key=api_key,
    base_url="https://api.siliconflow.cn/v1",
)

# 模型名称
MODEL_NAME = "Qwen/Qwen2.5-Coder-7B-Instruct"

app = FastAPI(title="编码助手")
templates = Jinja2Templates(directory="templates")


def call_model(prompt: str) -> str:
    """
    调用阿里云 Qwen 模型生成回复

    Args:
        prompt: 输入的提示词

    Returns:
        模型生成的回复内容
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"调用模型出错: {str(e)}"


@app.get("/")
def home(request: Request):
    """渲染主页"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/generate")
async def generate_code(request: Request):
    """
    代码生成接口
    接收用户的需求描述和语言，返回生成的代码
    """
    data = await request.json()
    prompt = data.get("prompt", "")
    language = data.get("language", "python")

    # 构建提示词
    full_prompt = f"""你是一个专业的程序员。请用 {language} 语言实现以下功能：
{prompt}

请只输出代码，不要包含其他解释。"""

    result = call_model(full_prompt)
    return {"result": result}


@app.post("/api/explain")
async def explain_code(request: Request):
    """
    代码解释接口
    接收用户的代码，返回代码的解释
    """
    data = await request.json()
    code = data.get("code", "")

    # 构建提示词
    full_prompt = f"""你是一个专业的程序员。请详细解释以下代码的功能：

```{code}
```"""

    result = call_model(full_prompt)
    return {"result": result}


@app.post("/api/fix")
async def fix_code(request: Request):
    """
    代码改错接口
    接收用户的代码和错误信息，返回修复后的代码
    """
    data = await request.json()
    code = data.get("code", "")
    error = data.get("error", "")

    # 构建提示词
    if error:
        full_prompt = f"""你是一个专业的程序员。请修复以下代码的错误。

错误信息：{error}

原始代码：
```{code}
```

请先解释错误原因，然后给出修复后的代码。"""
    else:
        full_prompt = f"""你是一个专业的程序员。请检查并修复以下代码中的错误。

原始代码：
```{code}
```

请先指出可能的问题，然后给出修复后的代码。"""

    result = call_model(full_prompt)
    return {"result": result}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
