"""命令行测试入口。"""

from agent import CodeReviewAgent


def read_code():
    print("请粘贴代码，输入单独一行 END 结束：")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def main():
    print("=" * 55)
    print("  代码审查 Agent（阿里云百炼 Qwen + 工具调用）")
    print("=" * 55)
    agent = CodeReviewAgent()
    while True:
        code = read_code()
        if not code.strip():
            print("未检测到代码。\n")
            continue
        print("\nAgent 正在工作...\n")
        try:
            result = agent.review(code, progress_callback=lambda msg: print(f"  >> {msg}"))
            if result["tool_log"]:
                print("\n[工具调用记录]")
                for item in result["tool_log"]:
                    print(f"  - {item['tool']}")
                    print(f"    {item['result'][:200]}...")
            print("\n" + "=" * 55)
            print("  审查报告")
            print("=" * 55)
            print(result["report"])
        except Exception as e:
            print(f"出错：{e}")
        if input("\n继续？(y/n): ").strip().lower() != "y":
            break


if __name__ == "__main__":
    main()