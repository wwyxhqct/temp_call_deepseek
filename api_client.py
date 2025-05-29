from openai import OpenAI

class DeepSeekClient:
    def __init__(self):
        self.client = OpenAI(
            api_key="sk-9079e7eeb9ca4c3f89d0e9f13655399b",
            base_url="https://api.deepseek.com"
        )
    
    def stream_chat(self, messages):
        """流式聊天"""
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True
        )
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content