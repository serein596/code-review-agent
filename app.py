"""
代码审查 Agent 的 Web 界面（基于 Streamlit）。
运行方式：streamlit run app.py
"""

import streamlit as st
from agent import CodeReviewAgent

# 页面配置
st.set_page_config(
    page_title="代码审查 Agent",
    page_icon="🔍",
    layout="wide",
)

# 标题和说明
st.title("🔍 代码审查 Agent")
st.markdown(
    "输入 Python 代码，Agent 会自动调用静态分析工具，"
    "结合大语言模型给出结构化的审查报告。"
)

# 初始化 Agent（缓存，避免每次刷新都重建）
@st.cache_resource
def get_agent():
    return CodeReviewAgent()

agent = get_agent()

# 侧边栏：清空历史记忆
with st.sidebar:
    st.header("⚙️ 控制面板")
    st.markdown("**上下文记忆**：当前已保存的对话轮数")
    st.write(f"{len(agent.history)} 条记录")
    if st.button("🗑️ 清空历史记忆"):
        agent.clear_history()
        st.success("历史记忆已清空")

# 代码输入区
st.subheader("📝 输入待审查代码")
code = st.text_area(
    "粘贴 Python 代码：",
    height=300,
    placeholder="# 在这里粘贴你的代码...",
)

# 审查按钮
if st.button("🚀 开始审查", type="primary"):
    if not code.strip():
        st.warning("请先输入代码。")
    else:
        with st.spinner("Agent 正在工作..."):
            try:
                # 进度提示
                progress_placeholder = st.empty()

                def on_progress(msg):
                    progress_placeholder.info(f"⏳ {msg}")

                result = agent.review(code, progress_callback=on_progress)
                progress_placeholder.empty()

                # 工具调用记录
                if result["tool_log"]:
                    st.subheader("🛠️ 工具调用记录")
                    for item in result["tool_log"]:
                        with st.expander(f"工具：{item['tool']}"):
                            st.code(item["result"], language="text")

                # 审查报告
                st.subheader("📋 审查报告")
                st.markdown(result["report"])

            except Exception as e:
                st.error(f"审查出错：{e}")