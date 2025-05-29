import tkinter as tk
from tkinter import scrolledtext, messagebox
import markdown

class MarkdownText(scrolledtext.ScrolledText):
    """支持Markdown渲染的文本组件"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.tag_config("user", foreground="#1a5fb4", font=("Arial", 11, "bold"))
        self.tag_config("assistant", foreground="#26a269", font=("Arial", 11, "bold"))
        self.tag_config("markdown", foreground="#333333")
        self.config(state=tk.DISABLED, padx=10, pady=10, bg="#fafafa")
    
    def add_message(self, role, content):
        """添加消息"""
        self.config(state=tk.NORMAL)
        
        # 添加角色标签
        tag = "user" if role == "user" else "assistant"
        role_text = "用户：" if role == "user" else "助手："
        self.insert(tk.END, role_text, tag)
        
        # 添加消息内容
        self.insert(tk.END, f" {content}\n\n")
        
        # 如果是助手消息，尝试渲染 Markdown
        if role == "assistant":
            self.render_markdown(content)
        
        self.config(state=tk.DISABLED)
        self.yview(tk.END)
    
    def render_markdown(self, content):
        """渲染Markdown内容"""
        try:
            # 将Markdown转换为HTML
            html_content = markdown.markdown(content)
            
            # 添加渲染内容
            self.insert(tk.END, "渲染内容：\n", "assistant")
            self.insert(tk.END, html_content + "\n\n", "markdown")
            
        except Exception as e:
            self.insert(tk.END, f"Markdown渲染错误: {str(e)}\n", "assistant")
    
    def start_stream(self):
        """开始流式响应显示"""
        self.config(state=tk.NORMAL)
        
        # 添加助手标签
        self.insert(tk.END, "助手：", "assistant")
        
        # 标记响应开始位置
        self.mark_set("response_start", "end-1c")
        self.mark_gravity("response_start", tk.LEFT)
        
        # 添加初始空响应
        self.insert(tk.END, "")
        self.mark_set("response_end", "end-1c")
        
        self.config(state=tk.DISABLED)
        self.yview(tk.END)
    
    def update_stream(self, content):
        """更新流式响应"""
        self.config(state=tk.NORMAL)
        
        # 删除旧的响应显示
        if self.tag_ranges("response_start") and self.tag_ranges("response_end"):
            self.delete("response_start", "response_end")
        
        # 添加新的响应内容
        self.insert("response_start", content)
        
        # 标记响应区域
        self.mark_set("response_end", "insert")
        
        self.config(state=tk.DISABLED)
        self.yview(tk.END)

class ChatInput(scrolledtext.ScrolledText):
    """聊天输入框"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config(height=4, wrap=tk.WORD, font=("Arial", 11), padx=10, pady=10)