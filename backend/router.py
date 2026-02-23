"""
API 路由模块 - 定义所有 API 端点
"""

import os
import re
import tempfile
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
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
    action: str = "plan"
    folder: str = ""


def extract_code_blocks(content: str) -> List[Dict[str, str]]:
    """从响应中提取代码块"""
    code_blocks = []
    pattern = r"```(\w+)?\n([\s\S]*?)```"
    matches = re.findall(pattern, content)

    for lang, code in matches:
        filename = extract_filename(code) or "untitled"
        if lang:
            filename = f"{Path(filename).stem}.{lang}"
        code_blocks.append({"filename": filename, "code": code.strip()})

    return code_blocks


def extract_filename(code: str) -> Optional[str]:
    """尝试从代码中提取文件名"""
    patterns = [
        r"#\s*filename:\s*(.+)",
        r"//\s*filename:\s*(.+)",
        r"/\*\s*filename:\s*(.+?)\s*\*/",
    ]

    for pattern in patterns:
        match = re.search(pattern, code, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def save_code_files(
    folder: str, code_blocks: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """保存代码文件到指定目录"""
    saved_files = []

    for block in code_blocks:
        try:
            file_path = Path(folder) / block["filename"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(block["code"], encoding="utf-8")
            saved_files.append({"path": str(file_path), "filename": block["filename"]})
        except Exception as e:
            saved_files.append(
                {
                    "path": block["filename"],
                    "filename": block["filename"],
                    "error": str(e),
                }
            )

    return saved_files


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
    - plan: 只对话，不创建文件
    - build: 对话并创建代码文件
    """
    messages = request.messages.copy()
    action = request.action
    folder = request.folder

    if request.mode == "generate":
        system_prompt = """你是一个专业的程序员。用户会描述想要实现的代码功能，
请用指定的编程语言生成代码。只输出代码，不要包含其他解释。
如果用户要求创建文件，请在代码顶部添加注释说明文件名，例如：# filename: main.py"""
        messages.insert(0, {"role": "system", "content": system_prompt})

    elif request.mode == "explain":
        system_prompt = """你是一个专业的程序员。用户会给你代码，请详细解释代码的功能。
请用通俗易懂的语言解释。"""
        messages.insert(0, {"role": "system", "content": system_prompt})

    elif request.mode == "fix":
        system_prompt = """你是一个专业的程序员。用户会给你代码和错误信息，请修复代码中的错误。
先解释错误原因，然后给出修复后的代码。"""
        messages.insert(0, {"role": "system", "content": system_prompt})

    result = chat_with_history(messages)

    files = []
    if action == "build" and folder:
        code_blocks = extract_code_blocks(result)
        if code_blocks:
            files = save_code_files(folder, code_blocks)

    return {"result": result, "role": "assistant", "files": files}
