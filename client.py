import socket
import threading
import customtkinter as ctk
from tkinter import messagebox

# 设置主题颜色
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ChatClient(ctk.CTk):
    def __init__(self, host, port):
        super().__init__()

        # --- 网络设置 ---
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = self.get_nickname()
        
        try:
            self.client.connect((host, port))
        except:
            messagebox.showerror("连接失败", f"无法连接到服务端 {host}")
            self.destroy()
            return

        # --- 窗口设置 ---
        self.title(f"极简聊天室 - {self.nickname}")
        self.geometry("500x650")

        # --- UI 布局 ---
        # 1. 顶部标题
        self.label = ctk.CTkLabel(self, text="🌐 局域网在线对话", font=("Heiti SC", 20, "bold"))
        self.label.pack(pady=10)

        # 2. 聊天记录显示框
        self.textbox = ctk.CTkTextbox(self, width=450, height=450, corner_radius=15, font=("Heiti SC", 14))
        self.textbox.pack(padx=20, pady=10, fill="both", expand=True)
        self.textbox.configure(state="disabled") # 初始锁定

        # 3. 底部输入区域容器
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=20, pady=20)

        # 输入框
        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="在这里输入消息...", 
                                 height=45, corner_radius=10, font=("Heiti SC", 14))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # 绑定回车键 (核心修复：直接绑定到 entry)
        self.entry.bind("<Return>", lambda event: self.send_message())

        # 发送按钮
        self.send_button = ctk.CTkButton(self.input_frame, text="发送", width=80, height=45, 
                                        corner_radius=10, command=self.send_message, font=("Heiti SC", 14, "bold"))
        self.send_button.pack(side="right")

        # --- 启动接收线程 ---
        self.running = True
        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

    def get_nickname(self):
        # 使用简单的 CTkInputDialog 获取昵称
        dialog = ctk.CTkInputDialog(text="请输入你的昵称:", title="加入聊天")
        name = dialog.get_input()
        return name if name else "匿名"

    def send_message(self):
        msg = self.entry.get().strip()
        if msg:
            full_msg = f"{self.nickname}: {msg}"
            self.client.send(full_msg.encode('utf-8'))
            self.entry.delete(0, 'end') # 发送完自动清空输入框

    def receive(self):
        while self.running:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self.client.send(self.nickname.encode('utf-8'))
                else:
                    self.display_message(message)
            except:
                self.running = False
                break

    def display_message(self, message):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", message + "\n\n") # 双换行增加间距，更好看
        self.textbox.see("end") # 自动滚动到底部
        self.textbox.configure(state="disabled")

# --- 运行部分 ---
if __name__ == "__main__":
    # 使用你提供的 IP 地址
    app = ChatClient("192.168.1.6",