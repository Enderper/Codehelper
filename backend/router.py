"""
API 路由模块 - 定义所有 API 端点
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List, Dict, Optional
from backend.model import generate_code, explain_code, fix_code, chat_with_history


router = APIRouter()


class GenerateRequest(BaseModel):
    """代码生成请求"""

    prompt: str
    language: str = "python"


class ExplainRequest(BaseModel):
    """代码解释请求"""

    code: str


class FixRequest(BaseModel):
    """代码修复请求"""

    code: str
    error: str = ""


class ChatRequest(BaseModel):
    """对话请求（带历史）"""

    messages: List[Dict[str, str]]
    mode: str = "general"  # general, generate, explain, fix


@router.post("/api/generate")
async def api_generate_code(request: GenerateRequest):
    """代码生成接口"""
    result = generate_code(request.prompt, request.language)
    return {"result": result}


@router.post("/api/explain")
async def api_explain_code(request: ExplainRequest):
    """代码解释接口"""
    result = explain_code(request.code)
    return {"result": result}


@router.post("/api/fix")
async def api_fix_code(request: FixRequest):
    """代码修复接口"""
    result = fix_code(request.code, request.error)
    return {"result": result}


@router.post("/api/chat")
async def api_chat(request: ChatRequest):
    """
    对话接口（带历史上下文）

    支持三种模式：
    - general: 普通对话
    - generate: 代码生成模式
    - explain: 代码解释模式
    - fix: 代码修复模式
    """
    messages = request.messages.copy()

    if request.mode == "generate":
        last_user_msg = messages[-1]["content"] if messages else ""
        system_prompt = """你是一个专业的程序员。用户会描述想要实现的代码功能，
请用指定的编程语言生成代码。只输出代码，不要包含其他解释。"""
        messages.insert(0, {"role": "system", "content": system_prompt})

    elif request.mode == "explain":
        last_user_msg = messages[-1]["content"] if messages else ""
        system_prompt = """你是一个专业的程序员。用户会给你代码，请详细解释代码的功能。
请用通俗易懂的语言解释。"""
        messages.insert(0, {"role": "system", "content": system_prompt})

    elif request.mode == "fix":
        last_user_msg = messages[-1]["content"] if messages else ""
        system_prompt = """你是一个专业的程序员。用户会给你代码和错误信息，请修复代码中的错误。
先解释错误原因，然后给出修复后的代码。"""
        messages.insert(0, {"role": "system", "content": system_prompt})

    result = chat_with_history(messages)
    return {"result": result, "role": "assistant"}
