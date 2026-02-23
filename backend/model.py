"""
模型调用模块 - 封装 AI 模型调用逻辑
"""

from openai import OpenAI
from typing import List, Dict, Any, cast
from backend.config import API_KEY, MODEL_NAME, BASE_URL


MessageType = List[Dict[str, str]]


class ModelClient:
    """模型客户端封装"""

    def __init__(self):
        self.client = OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL,
        )
        self.model_name = MODEL_NAME

    def chat(self, messages: MessageType, temperature: float = 0.7) -> str:
        """
        调用模型生成回复

        Args:
            messages: 消息历史列表，每条消息包含 role 和 content
            temperature: 温度参数，控制生成随机性

        Returns:
            模型生成的回复内容
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=cast(List[Any], messages),
                temperature=temperature,
            )
            content = response.choices[0].message.content
            return content if content else "模型未返回有效响应"
        except Exception as e:
            return f"调用模型出错: {str(e)}"


model_client = ModelClient()


def generate_code(prompt: str, language: str = "python") -> str:
    """生成代码"""
    full_prompt = f"""你是一个专业的程序员。请用 {language} 语言实现以下功能：
{prompt}

请只输出代码，不要包含其他解释。"""
    return model_client.chat([{"role": "user", "content": full_prompt}])


def explain_code(code: str) -> str:
    """解释代码"""
    full_prompt = f"""你是一个专业的程序员。请详细解释以下代码的功能：

```{code}
```"""
    return model_client.chat([{"role": "user", "content": full_prompt}])


def fix_code(code: str, error: str = "") -> str:
    """修复代码"""
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
    return model_client.chat([{"role": "user", "content": full_prompt}])


def chat_with_history(messages: List[Dict[str, str]]) -> str:
    """
    带上下文的对话

    Args:
        messages: 完整的消息历史，包含用户和助手的消息

    Returns:
        助手的回复
    """
    return model_client.chat(messages)
