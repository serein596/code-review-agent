"""
代码审查 Agent 核心模块。
实现：ReAct 循环、上下文记忆、错误重试。
"""

import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT, build_user_prompt, build_tool_result_prompt
from tools import call_tool, TOOLS

load_dotenv()

API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen-plus"

MAX_TOOL_ROUNDS = 5   # 最多允许几轮工具调用
MAX_RETRIES = 3       # API 调用失败最多重试几次


class CodeReviewAgent:
    """代码审查 Agent。"""

    def __init__(self):
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.history = []   # 上下文记忆：保存每轮对话

    def _call_llm(self, messages: list) -> str:
        """调用 LLM，带重试机制。"""
        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=0.3,
                )
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                wait = 2 ** attempt   # 指数退避：2, 4, 8 秒
                print(f"[重试 {attempt}/{MAX_RETRIES}] 调用失败：{e}，{wait} 秒后重试...")
                time.sleep(wait)
        raise RuntimeError(f"LLM 调用失败（已重试 {MAX_RETRIES} 次）：{last_error}")

    def review(self, code: str, progress_callback=None) -> dict:
        """
        执行一次完整的审查。
        progress_callback: 可选的进度回调，用于在 Web 界面显示中间状态。
        返回：{"report": 最终报告, "tool_log": 工具调用记录}
        """
        tool_log = []

        # 拼接历史记忆
        history_text = "\n".join(self.history[-4:]) if self.history else ""
        user_prompt = build_user_prompt(code, history_text)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        # ReAct 循环：推理 -> 工具调用 -> 输出
        for round_idx in range(MAX_TOOL_ROUNDS):
            reply = self._call_llm(messages)

            # 检查 LLM 是否要调用工具
            tool_name = self._extract_tool_call(reply)

            if tool_name is None:
                # 没有工具调用，说明是最终报告
                self.history.append(f"用户提交代码审查（{len(code)} 字符）")
                self.history.append(f"审查完成")
                return {"report": reply, "tool_log": tool_log}

            # 执行工具
            if progress_callback:
                progress_callback(f"正在调用工具：{tool_name}")

            tool_result = call_tool(tool_name, code)
            tool_log.append({"tool": tool_name, "result": tool_result})

            # 把工具结果喂回给 LLM
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": build_tool_result_prompt(tool_name, tool_result)})

        # 超过最大轮数，强制要求输出报告
        messages.append({"role": "user", "content": "请立即输出最终审查报告，不要再调用工具。"})
        final = self._call_llm(messages)
        return {"report": final, "tool_log": tool_log}

    @staticmethod
    def _extract_tool_call(text: str):
        """从 LLM 回复中提取工具调用指令，格式：TOOL_CALL: 工具名"""
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("TOOL_CALL:"):
                name = line.replace("TOOL_CALL:", "").strip()
                if name in TOOLS:
                    return name
        return None

    def clear_history(self):
        """清空上下文记忆。"""
        self.history = []