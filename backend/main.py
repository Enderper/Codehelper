"""
FastAPI 应用入口
"""

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from backend.router import router


app = FastAPI(
    title="Codehelper - 编码助手",
    description="基于 AI 的代码生成、解释、修复工具",
    version="2.0.0",
)

templates = Jinja2Templates(directory="templates")

app.include_router(router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """渲染主页"""
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
