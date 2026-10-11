"""
Prompt 模板：Agent 的系统提示词与用户提示词。
"""

from tools import list_tools

# 系统提示：告诉 LLM 它的角色、可用工具、输出格式
SYSTEM_PROMPT = f"""你是一名资深软件工程师，擅长代码审查。

你可以调用以下工具来辅助审查：
{list_tools()}

工作方式：
1. 如果需要工具的客观数据，请在回复中单独一行输出：
   TOOL_CALL: 工具名
2. 你会收到工具返回的结果，然后继续分析。
3. 当你认为信息足够时，输出最终审查报告，格式如下：

## 代码质量
（分析命名、结构、可读性）

## 潜在 Bug
（逻辑错误、异常处理、边界条件）

## 性能问题
（瓶颈、可优化点）

## 安全性
（安全隐患）

## 总体评分
（0-100 分，并简述理由）

注意：不要在最终报告中提"工具"这个词，直接给结论。

【强制要求】在输出最终审查报告之前，你必须先调用至少一个工具来获取客观数据。
即使代码看起来很简单，也要先调用 count_structures 统计一下结构，或调用 analyze_complexity 分析复杂度。
不调用工具就直接输出报告，视为违规。
"""


def build_user_prompt(code: str, history: str = "") -> str:
    """构造用户提示词，可带历史对话。"""
    prompt = ""
    if history:
        prompt += f"【历史对话】\n{history}\n\n"
    prompt += f"【待审查代码】\n```\n{code}\n```\n\n请开始审查。"
    return prompt


def build_tool_result_prompt(tool_name: str, result: str) -> str:
    """工具执行后，把结果喂回给 LLM。"""
    return f"TOOL_RESULT for `{tool_name}`:\n{result}\n\n请继续分析，或输出最终报告。"