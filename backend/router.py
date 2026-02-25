"""
API 路由模块 - 定义所有 API 端点
"""

import subprocess
import re
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from backend.model import chat_with_history


router = APIRouter()


class ChatRequest(BaseModel):
    """对话请求（带历史上下文）"""

    messages: List[Dict[str, str]]
    mode: str = "general"
    action: str = "explain"
    fileContent: Optional[str] = None
    fileName: Optional[str] = None


# 危险命令黑名单
DANGEROUS_PATTERNS = [
    r"rm\s+-rf",
    r"del\s+/[fqs]",
    r"format\s+",
    r"mkfs",
    r"shutdown",
    r"reboot",
    r"kill\s+-9",
    r"pkill",
    r"curl.*\|\s*sh",
    r"wget.*\|\s*sh",
    r"import\s+os.*system",
    r'__import__\s*\(\s*[\'"]os[\'"]',
]


def is_code_safe(code: str) -> tuple[bool, str]:
    """
    检查代码是否安全

    Returns:
        (是否安全, 错误信息)
    """
    code_lower = code.lower()

    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, code_lower):
            return False, f"检测到危险命令: {pattern}"

    return True, ""


def execute_code(code: str, language: str = "python") -> Dict[str, Any]:
    """安全地执行代码并返回结果"""

    # 检查是否有 input() 调用
    if "input(" in code:
        return {
            "success": False,
            "stdout": "",
            "stderr": "⚠️ 检测到 input() 调用，当前模式不支持需要用户交互输入的代码。请修改代码后重试。",
            "returncode": "-1",
        }

    is_safe, error_msg = is_code_safe(code)
    if not is_safe:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"安全检查失败: {error_msg}",
            "returncode": "-1",
        }

    try:
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
            if hasattr(subprocess, "CREATE_NO_WINDOW")
            else 0,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": str(result.returncode),
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "执行超时（超过10秒）",
            "returncode": "-1",
        }
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": "-1"}


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
        user_code = (
            request.fileContent if request.fileContent else messages[-1]["content"]
        )

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

    # 处理文件上传
    if request.fileContent:
        file_info = f"文件名: {request.fileName}\n\n文件内容:\n```\n{request.fileContent}\n```\n\n"
        if messages:
            messages[-1]["content"] = file_info + messages[-1]["content"]

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
