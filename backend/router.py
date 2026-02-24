"""
API 路由模块 - 定义所有 API 端点
"""

import subprocess
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.model import chat_with_history


router = APIRouter()


class GenerateRequest(BaseModel):
    prompt: str
    language: str = "python"


class ExplainRequest(BaseModel):
    code: str


class FixRequest(BaseModel):
    code: str
    error: str = ""


class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    mode: str = "general"
    action: str = "explain"


def execute_code(code: str, language: str = "python") -> Dict[str, Any]:
    """执行代码并返回结果"""
    try:
        result = subprocess.run(
            ["python", "-c", code], capture_output=True, text=True, timeout=10
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": str(result.returncode),
        }
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": "-1"}


@router.post("/api/generate")
async def api_generate_code(request: GenerateRequest):
    """代码生成接口"""
    from backend.model import generate_code

    result = generate_code(request.prompt, request.language)
    return {"result": result}


@router.post("/api/explain")
async def api_explain_code(request: ExplainRequest):
    """代码解释接口"""
    from backend.model import explain_code

    result = explain_code(request.code)
    return {"result": result}


@router.post("/api/fix")
async def api_fix_code(request: FixRequest):
    """代码修复接口"""
    from backend.model import fix_code

    result = fix_code(request.code, request.error)
    return {"result": result}


@router.post("/api/chat")
async def api_chat(request: ChatRequest):
    """
    对话接口（带历史上下文）

    支持模式：
    - general: 普通对话
    - generate: 代码生成模式
    - explain: 代码解释模式
    - fix: 代码修复模式

    支持操作：
    - explain: 只解释代码
    - run: 执行代码并解释结果
    """
    messages = request.messages.copy()
    action = request.action

    # 处理运行模式
    if action == "run" and request.mode == "explain":
        user_code = messages[-1]["content"] if messages else ""

        # 执行代码
        exec_result = execute_code(user_code)

        # 构建执行结果消息
        if exec_result["success"]:
            exec_output = (
                "✅ 代码执行成功！\n\n输出结果：\n```\n"
                + exec_result["stdout"]
                + "\n```\n"
            )
        else:
            exec_output = (
                "❌ 代码执行失败！\n\n错误信息：\n```\n"
                + exec_result["stderr"]
                + "\n```\n"
            )

        # 发送给 AI 分析
        analysis_prompt = (
            exec_output
            + "\n这是一段代码的执行结果。请先返回上面的执行结果，然后解释这段代码的功能。如果执行失败，请分析错误原因并给出修复建议。"
        )

        analysis_messages = messages.copy()
        analysis_messages[-1]["content"] = analysis_prompt

        system_prompt = "你是一个专业的程序员。用户给你一段代码的执行结果，请先显示执行结果，然后解释代码的功能。如果有错误，分析原因并给出修复建议。"
        analysis_messages.insert(0, {"role": "system", "content": system_prompt})

        result = chat_with_history(analysis_messages)
        return {"result": result, "role": "assistant", "executed": True}

    # 正常模式
    if request.mode == "generate":
        system_prompt = "你是一个专业的程序员。用户会描述想要实现的代码功能，请用指定的编程语言生成代码。只输出代码，不要包含其他解释。"
        messages.insert(0, {"role": "system", "content": system_prompt})

    elif request.mode == "explain":
        system_prompt = "你是一个专业的程序员。用户会给你代码，请详细解释代码的功能。请用通俗易懂的语言解释。"
        messages.insert(0, {"role": "system", "content": system_prompt})

    elif request.mode == "fix":
        system_prompt = "你是一个专业的程序员。用户会给你代码和错误信息，请修复代码中的错误。先解释错误原因，然后给出修复后的代码。"
        messages.insert(0, {"role": "system", "content": system_prompt})

    result = chat_with_history(messages)
    return {"result": result, "role": "assistant"}
