# 导入必要的网络编程库
import socket  # UDP通信核心库
import threading  # 实现多线程并发处理
from tkinter import (  # 图形界面库
    Tk, Text, Listbox, Scrollbar, END
)
from datetime import datetime  # 时间戳生成

class ChatServerGUI:
    def __init__(self, host='localhost', port=12002):
        """服务器主类初始化方法
        :param host: 服务器IP地址，默认本地回环地址
        :param port: 监听端口号，默认12002
        """
        self.host = host  # 存储服务器地址
        self.port = port  # 存储服务器端口
        self.clients = {}  # 客户端管理字典 {地址元组: 昵称}
        
        # ===== GUI界面初始化 =====
        self.window = Tk()  # 创建主窗口对象
        self.window.title("UDP聊天室服务器")  # 设置窗口标题
        self.window.geometry("1000x800")  # 设置窗口尺寸（宽x高）
        
        # ===== 聊天记录显示区初始化 =====
        self.chat_display = Text(
            self.window, 
            wrap='word',  # 自动换行模式
            state='disabled',  # 初始禁用编辑（只读）
            font=('Consolas', 12)  # 设置等宽字体
        )
        self.chat_display.pack(
            expand=True,  # 填充可用空间
            fill='both',  # 同时填充水平和垂直空间
            padx=10, 
            pady=10  # 内边距
        )
        
        # ===== 在线用户列表初始化 =====
        self.user_list = Listbox(
            self.window, 
            height=15,  # 固定显示15条用户信息
            font=('Consolas', 10)
        )
        self.user_list.pack(side='left', fill='y', padx=10)  # 左侧垂直填充
        
        # ===== 滚动条配置 =====
        scrollbar = Scrollbar(
            self.window, 
            command=self.chat_display.yview  # 关联文本框的垂直滚动
        )
        scrollbar.pack(side='right', fill='y')  # 右侧垂直填充
        self.chat_display.config(yscrollcommand=scrollbar.set)  # 双向绑定滚动
        
        # ===== UDP服务器初始化 =====
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # AF_INET: IPv4地址族 | SOCK_DGRAM: UDP协议类型
        self.server_socket.bind((self.host, self.port))  # 绑定监听地址和端口
        self.log_message("[系统] 服务器已启动，正在监听端口 12002")  # 启动提示
        
        # ===== 接收线程初始化 =====
        self.recv_thread = threading.Thread(target=self.receive_messages)
        # 创建独立线程处理消息接收，避免阻塞GUI主线程
        self.recv_thread.daemon = True  # 设置为守护线程（主程序退出时自动终止）
        self.recv_thread.start()  # 启动接收线程
        
        self.window.mainloop()  # 进入GUI事件循环

    def receive_messages(self):
        """持续接收客户端消息的线程函数
        实现逻辑：
        1. 无限循环监听端口
        2. 接收并解析数据包
        3. 根据消息类型分发处理
        4. 异常处理保障稳定性
        """
        while True:
            try:
                # 接收数据（最大1024字节）和客户端地址
                data, addr = self.server_socket.recvfrom(1024)
                message = data.decode('utf-8').strip()  # 解码并去除首尾空白字符
                
                # ===== 用户注册处理 =====
                if message.startswith("/nick "):
                    # 提取昵称（分割字符串，最多分割一次）
                    nickname = message.split(" ", 1)[1]
                    self.clients[addr] = nickname  # 更新客户端信息
                    self.update_user_list()  # 刷新用户列表显示
                    # 记录系统日志并广播通知
                    self.log_system(f"{addr[0]}:{addr[1]} {nickname} 已加入聊天室")
                    self.broadcast(f"{nickname} 加入了聊天室！")
                    
                # ===== 用户退出处理 =====
                elif message.startswith("/quit"):
                    # 安全移除客户端信息（默认值防止KeyError）
                    nickname = self.clients.pop(addr, "匿名用户")
                    self.log_system(f"{addr[0]}:{addr[1]} {nickname} 已离开聊天室")
                    self.broadcast(f"{nickname} 退出了聊天室")
                    self.update_user_list()  # 刷新用户列表显示
                    
                # ===== 普通消息处理 =====
                else:
                    # 获取昵称（未注册用户显示"未知用户"）
                    sender_nickname = self.clients.get(addr, "未知用户")
                    # 生成带时间戳的日志消息
                    log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] {addr[0]}:{addr[1]} {sender_nickname}: {message}"
                    self.log_chat(log_msg)  # 记录聊天日志
                    self.broadcast(f"[{sender_nickname}]: {message}")  # 广播消息
                    
            except Exception as e:
                # 捕获所有异常防止程序崩溃
                self.log_system(f"[错误] 接收数据异常: {str(e)}")
                break  # 终止接收循环

    def log_message(self, message):
        """显示普通日志信息
        实现细节：
        - 临时启用文本框编辑
        - 插入新消息并自动滚动
        - 恢复只读状态防止篡改
        """
        self.chat_display.config(state='normal')  # 设为可编辑状态
        self.chat_display.insert(END, message + "\n")  # 追加消息并换行
        self.chat_display.see(END)  # 自动滚动到底部
        self.chat_display.config(state='disabled')  # 恢复只读保护

    def broadcast(self, message):
        """向所有客户端转发消息
        设计考量：
        - 遍历所有已注册客户端地址
        - 使用try-except防止单个客户端异常影响整体
        - UDP无连接特性需要主动发送到每个地址
        """
        for addr in self.clients:
            try:
                # 将消息编码为字节流发送
                self.server_socket.sendto(message.encode('utf-8'), addr)
            except:
                # 可能原因：客户端离线、网络中断等
                pass  # 忽略发送失败的情况

    def update_user_list(self):
        """动态更新在线用户列表
        实现步骤：
        1. 清空当前列表
        2. 遍历客户端字典构建新列表
        3. 按注册顺序显示用户信息
        """
        self.user_list.delete(0, END)  # 清空现有列表项
        for addr, nickname in self.clients.items():
            # 显示格式：昵称 (IP:PORT)
            self.user_list.insert(END, f"{nickname} ({addr[0]}:{addr[1]})")

    def log_system(self, message):
        """记录系统级日志信息
        特点：
        - 使用蓝色字体标识系统消息
        - 自动添加时间戳和地址信息
        - 保持日志的完整性和可追溯性
        """
        self.chat_display.config(state='normal')
        # 插入带样式的系统消息
        self.chat_display.insert(END, f"[系统] {message}\n")
        self.chat_display.see(END)
        self.chat_display.config(state='disabled')

    def log_chat(self, message):
        """记录普通聊天消息
        功能：
        - 保存完整的聊天记录
        - 包含时间戳和客户端地址信息
        - 消息格式标准化
        """
        self.chat_display.config(state='normal')
        # 插入带时间戳的聊天记录
        self.chat_display.insert(END, f"{message}\n")
        self.chat_display.see(END)
        self.chat_display.config(state='disabled')

if __name__ == "__main__":
    ChatServerGUI()  # 启动服务器应用程序