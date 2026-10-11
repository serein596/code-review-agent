# 代码审查 Agent

基于大语言模型的代码审查助手，自动调用静态分析工具，输出结构化审查报告。

## 功能特性

- 🔍 **自动审查**：从代码质量、潜在 Bug、性能、安全性四个维度分析
- 🛠️ **工具调用**：集成 AST 结构统计和 radon 圈复杂度分析
- 🧠 **上下文记忆**：支持多轮审查，保留历史对话
- 🔁 **错误重试**：API 调用失败自动重试 3 次，指数退避
- 💻 **双入口**：命令行 + Streamlit Web 界面

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

在项目根目录创建 `.env` 文件：

```
DASHSCOPE_API_KEY=sk-你的阿里云百炼API Key
```

> 本项目使用阿里云百炼的 `qwen-plus` 模型。

### 3. 运行

**命令行模式：**

```bash
python main.py
```

**Web 界面模式：**

```bash
streamlit run app.py
```

然后在浏览器打开 `http://localhost:8501`。

## 使用示例

### 输入代码

```python
def divide(a, b):
    return a / b

def get_max(lst):
    return max(lst)

data = []
print(get_max(data))
```

### 输出报告

Agent 会先调用 `count_structures` 和 `analyze_complexity` 工具，
然后结合工具结果给出结构化报告，指出：

- `get_max([])` 会抛出 `ValueError`
- `divide(a, b)` 未处理 `b == 0`
- 顶层执行代码应放进 `if __name__ == "__main__":`

## 项目结构

```
code-review-agent/
├── main.py          # 命令行入口
├── app.py           # Web 界面
├── agent.py         # Agent 核心
├── tools.py         # 工具集合
├── prompts.py       # Prompt 模板
├── requirements.txt # 依赖
├── Design.md        # 设计文档
└── README.md        # 使用说明
```

## 技术栈

- **语言**：Python 3.13
- **LLM**：阿里云百炼 `qwen-plus`
- **静态分析**：`ast`（Python 标准库）、`radon`
- **Web 框架**：Streamlit
- **依赖管理**：`python-dotenv`、`openai`

## 作者

姓名：__郭婷婷__
学号：__2112190203__