"""
工具模块：Agent 可以调用的工具集合。
每个工具都接收字符串参数，返回字符串结果。
"""

import ast
from radon.complexity import cc_visit


def analyze_complexity(code: str) -> str:
    """分析代码的圈复杂度。"""
    try:
        results = cc_visit(code)
        if not results:
            return "未检测到函数或方法。"
        lines = []
        for item in results:
            lines.append(f"- 函数 `{item.name}`（第 {item.lineno} 行）: 圈复杂度 = {item.complexity}")
        high = [r for r in results if r.complexity > 10]
        if high:
            lines.append("\n[警告] 以下函数圈复杂度较高（>10），建议拆分：")
            for h in high:
                lines.append(f"  - `{h.name}`: {h.complexity}")
        return "\n".join(lines)
    except SyntaxError as e:
        return f"代码存在语法错误，无法分析复杂度：{e}"
    except Exception as e:
        return f"分析出错：{e}"


def count_structures(code: str) -> str:
    """统计代码中的函数和类数量。"""
    try:
        tree = ast.parse(code)
        funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        return f"函数数量：{len(funcs)}，类数量：{len(classes)}"
    except SyntaxError as e:
        return f"语法错误：{e}"
    except Exception as e:
        return f"统计出错：{e}"


# 工具注册表：名字 -> (函数, 描述)
TOOLS = {
    "analyze_complexity": {
        "func": analyze_complexity,
        "desc": "分析代码的圈复杂度，识别复杂度过高的函数。",
    },
    "count_structures": {
        "func": count_structures,
        "desc": "统计代码中函数和类的数量，快速了解代码规模。",
    },
}


def call_tool(name: str, code: str) -> str:
    """根据工具名调用对应工具。"""
    if name not in TOOLS:
        return f"未知工具：{name}"
    return TOOLS[name]["func"](code)


def list_tools() -> str:
    """返回所有可用工具的文本描述，用于放进 Prompt。"""
    lines = []
    for name, info in TOOLS.items():
        lines.append(f"- `{name}`：{info['desc']}")
    return "\n".join(lines)