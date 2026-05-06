import ollama

def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]

def match(input_text, dataset):
    prompt = f"""你是专业健康匹配助手，根据用户描述从数据集中找出最相关的内容，返回结果，并且解释一下选择原因。
用户描述：{input_text}
数据集：{dataset}"""
    res = ollama.chat(model="gemma3:4b", messages=[{"role": "user", "content": prompt}])
    return res["message"]["content"]

if __name__ == "__main__":
    path = r"D:\project\diagnose.txt"
    try:
        data = load_data(path)
    except:
        print("❌ 数据集路径错误，请检查文件位置！")
        exit()

    print("=" * 40)
    print("🏥 本地健康病例匹配系统已启动")
    print("💡 请输入你的症状描述，系统将自动匹配病例方案")
    print("💡 输入 'exit' 可退出程序")
    print("=" * 40)

    while True:
        text = input("\n请输入症状描述：")
        if text.lower() == "exit":
            print("\n👋 感谢使用，再见！")
            break
        print("🔍 正在匹配最佳病例方案...")
        print(f"✅ 匹配结果：\n{match(text, data)}\n")