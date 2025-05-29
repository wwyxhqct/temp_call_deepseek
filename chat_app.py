import tkinter as tk
import threading
import queue
from widgets import MarkdownText, ChatInput 
from api_client import DeepSeekClient        

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DeepSeek Chat")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # 初始化API客户端
        self.client = DeepSeekClient()
        
        # 对话历史
        self.messages = [
            {"role": "system", "content": "你是一个乐于助人的助手。"}
        ]
        
        # 创建界面
        self.create_widgets()
        
        # 流式响应队列
        self.response_queue = queue.Queue()
        self.current_response = ""
        self.response_active = False
        
        # 添加欢迎消息
        self.history_text.add_message("assistant", "欢迎使用 DeepSeek 聊天机器人！输入 'exit' 退出对话。")
    
    def create_widgets(self):
        # 创建主框架
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建聊天历史区域
        history_frame = tk.LabelFrame(main_frame, text="聊天记录", bg="#ffffff", 
                                    font=("Arial", 10, "bold"))
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.history_text = MarkdownText(history_frame)
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建输入区域
        input_frame = tk.Frame(main_frame, bg="#f0f0f0")
        input_frame.pack(fill=tk.X, padx=5, pady=(5, 10))
        
        self.input_text = ChatInput(input_frame)
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_text.bind("<Return>", self.on_enter_pressed)
        
        # 发送按钮
        send_button = tk.Button(
            input_frame, text="发送", command=self.send_message,
            bg="#26a269", fg="white", font=("Arial", 10, "bold"),
            width=10, height=2, relief=tk.FLAT
        )
        send_button.pack(side=tk.RIGHT)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪 | DeepSeek 聊天机器人")
        status_bar = tk.Label(
            self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, 
            anchor=tk.W, bg="#e0e0e0", fg="#555555", font=("Arial", 9)
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def on_enter_pressed(self, event):
        """处理回车键按下事件"""
        if event.state == 0x4:  # 检查 Control 键是否按下
            self.send_message()
            return "break"  # 阻止默认的换行行为
        return None  # 允许默认行为（换行）
    
    def send_message(self):
        """发送用户消息"""
        # 获取输入内容
        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input:
            return
        
        # 检查退出命令
        if user_input.lower() == "exit":
            self.root.destroy()
            return
        
        # 清空输入框
        self.input_text.delete("1.0", tk.END)
        
        # 添加到聊天历史
        self.history_text.add_message("user", user_input)
        self.messages.append({"role": "user", "content": user_input})
        
        # 更新状态
        self.status_var.set("正在与 DeepSeek API 通信...")
        
        # 在新线程中发送请求
        threading.Thread(target=self.get_response, daemon=True).start()
        
        # 启动流式响应处理
        self.response_active = True
        self.current_response = ""
        self.history_text.start_stream()  # 初始化流式显示
        self.process_stream()
    
    def get_response(self):
        """从 API 获取响应"""
        try:
            # 发起流式请求
            response_generator = self.client.stream_chat(self.messages)
            
            # 处理流式响应
            for content in response_generator:
                self.response_queue.put(content)
            
            # 添加结束标记
            self.response_queue.put(None)
            
        except Exception as e:
            self.response_queue.put(f"发生错误：{e}")
            self.response_queue.put(None)
    
    def process_stream(self):
        """处理流式响应"""
        try:
            while not self.response_queue.empty():
                chunk = self.response_queue.get_nowait()
                
                if chunk is None:
                    # 结束流式响应
                    self.response_active = False
                    self.messages.append({"role": "assistant", "content": self.current_response})
                    self.status_var.set("就绪 | DeepSeek 聊天机器人")
                    return
                
                # 更新当前响应
                self.current_response += chunk
                
                # 更新聊天历史
                self.history_text.update_stream(self.current_response)
        
        except queue.Empty:
            pass
        
        # 如果仍在接收响应，继续检查
        if self.response_active:
            self.root.after(100, self.process_stream)