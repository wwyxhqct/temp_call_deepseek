from openai import OpenAI
import sys
import time

def typewriter_print(text, delay=0.1):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# 初始化 OpenAI 客户端，设置 DeepSeek API 的 base_url
client = OpenAI(
    api_key="sk-9079e7eeb9ca4c3f89d0e9f13655399b",  # 替换为您的 DeepSeek API 密钥
    base_url="https://api.deepseek.com"
)

# 初始化对话上下文
messages = [
    {"role": "system", "content": "你是一个乐于助人的助手。"}
]

typewriter_print("欢迎使用 DeepSeek 聊天机器人！输入 'exit' 退出对话。")

while True:
    # 获取用户输入
    user_input = input("\n你：")
    if user_input.strip().lower() == "exit":
        typewriter_print("再见！感谢使用 DeepSeek 聊天机器人。")
        break

    # 将用户输入添加到对话上下文
    messages.append({"role": "user", "content": user_input})

    try:
        # 发起流式请求
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True
        )

        print("助手：", end='', flush=True)
        assistant_reply = ""

        # 逐块接收并输出模型的回复内容
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end='', flush=True)
                assistant_reply += content

        # 将助手的回复添加到对话上下文
        messages.append({"role": "assistant", "content": assistant_reply})

    except Exception as e:
        print(f"\n发生错误：{e}")
        break
