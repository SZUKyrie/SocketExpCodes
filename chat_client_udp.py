import socket  # 用于网络通信
import threading  # 用于实现多线程接收消息
from tkinter import (  # 用于创建图形用户界面
    Tk, Frame, Label, Scrollbar, Entry, Button, Text, END
)

class ChatClientGUI:
    def __init__(self, host='localhost', port=12002):
        """客户端主类初始化方法
        :param host: 服务器地址，默认本地主机
        :param port: 服务器端口，默认12002
        """
        self.host = host  # 存储服务器地址
        self.port = port  # 存储服务器端口
        self.nickname = ""  # 用户昵称初始化为空
        
        # 创建UDP套接字（无连接协议）
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # ===== GUI界面初始化 =====
        self.window = Tk()  # 创建主窗口
        self.window.title("UDP聊天室客户端")  # 设置窗口标题
        self.window.geometry("800x600")  # 设置窗口尺寸
        
        # ===== 昵称输入模块 =====
        self.nick_frame = Frame(self.window)  # 创建昵称输入框架
        self.nick_label = Label(self.nick_frame, text="昵称:", anchor='w')  # 昵称标签
        self.nick_entry = Entry(self.nick_frame, width=15)  # 昵称输入框
        self.nick_button = Button(  # 进入聊天室按钮
            self.nick_frame, 
            text="进入聊天室", 
            command=self.set_nickname  # 绑定点击事件
        )
        
        # 布局设置（左对齐，设置内边距）
        self.nick_label.pack(side='left', padx=(10, 0))
        self.nick_entry.pack(side='left', expand=True, fill='x')
        self.nick_button.pack(side='left', padx=(10, 0))
        self.nick_frame.pack(fill='x', pady=10)  # 填充水平空间
        
        # ===== 聊天记录显示区 =====
        self.chat_display = Text(
            self.window, 
            wrap='word',  # 自动换行
            state='disabled'  # 初始禁用编辑
        )
        self.chat_display.pack(
            expand=True,  # 填充可用空间
            fill='both',  # 填充水平和垂直空间
            padx=10, 
            pady=10
        )
        
        # ===== 滚动条设置 =====
        scrollbar = Scrollbar(self.window, command=self.chat_display.yview)  # 创建垂直滚动条
        scrollbar.pack(side='right', fill='y')  # 右侧垂直填充
        self.chat_display.config(yscrollcommand=scrollbar.set)  # 关联滚动条
        
        # ===== 消息输入模块 =====
        self.msg_frame = Frame(self.window)  # 创建消息输入框架
        self.msg_entry = Entry(self.msg_frame, width=50)  # 消息输入框
        self.send_button = Button(  # 发送按钮
            self.msg_frame, 
            text="发送", 
            command=self.send_message  # 绑定点击事件
        )
        
        # 布局设置（输入框扩展，按钮右对齐）
        self.msg_entry.pack(side='left', expand=True, fill='x')
        self.send_button.pack(side='right', padx=5)
        self.msg_frame.pack(side='bottom', pady=10, padx=10, fill='x')  # 底部固定
        
        # ===== 接收线程初始化 =====
        self.recv_thread = threading.Thread(target=self.receive_messages)  # 创建接收线程
        self.recv_thread.daemon = True  # 设置为守护线程（主程序退出时自动结束）
        
        self.window.mainloop()  # 启动GUI主循环

    def set_nickname(self):
        """设置用户昵称并初始化连接
        1. 获取输入框内容
        2. 验证昵称有效性
        3. 禁用昵称输入组件
        4. 发送初始注册消息
        """
        self.nickname = self.nick_entry.get().strip()  # 获取并去除首尾空格
        if not self.nickname:  # 检查昵称是否为空
            return
        self.nick_entry.config(state='disabled')  # 禁用输入框
        self.nick_button.config(state='disabled')  # 禁用按钮
        self.send_initial_message()  # 发送初始消息

    def send_initial_message(self):
        """发送包含昵称的注册消息到服务器
        消息格式：/nick <昵称>
        作用：通知服务器用户加入
        """
        msg = f"/nick {self.nickname}"  # 构造注册消息
        self.sock.sendto(msg.encode('utf-8'), (self.host, self.port))  # 发送UDP数据包
        self.recv_thread.start()  # 启动消息接收线程

    def send_message(self):
        """处理用户消息发送
        1. 获取消息内容
        2. 处理退出命令
        3. 构造完整消息格式
        4. 发送消息到服务器
        """
        msg = self.msg_entry.get().strip()  # 获取输入内容
        if not msg:  # 检查空消息
            return
        if msg == "/quit":  # 处理退出命令
            self.sock.sendto(msg.encode('utf-8'), (self.host, self.port))  # 发送退出通知
            self.window.quit()  # 退出应用程序
        else:
            # 构造带昵称的消息格式（客户端显示用）
            full_msg = f"[{self.nickname}]: {msg}"
            self.sock.sendto(full_msg.encode('utf-8'), (self.host, self.port))  # 发送消息
            self.msg_entry.delete(0, END)  # 清空输入框

    def receive_messages(self):
        """持续接收服务器消息的线程函数
        1. 循环监听服务器数据
        2. 解析不同类型消息
        3. 调用对应的显示方法
        4. 异常处理（网络中断等）
        """
        while True:
            try:
                # 接收数据（最大1024字节）
                data, _ = self.sock.recvfrom(1024)
                message = data.decode('utf-8')  # 解码为字符串
                
                # 根据消息类型分发处理
                if "加入了聊天室" in message:
                    self.show_system_message(f"{message}")  # 显示加入提示
                elif "退出了聊天室" in message:
                    self.show_system_message(f"{message}")  # 显示退出提示
                else:
                    self.show_chat_message(message)  # 显示普通聊天消息
                    
            except Exception as e:
                # 网络异常处理（如断开连接）
                print(f"接收异常: {str(e)}")
                break  # 终止接收循环

    def show_system_message(self, msg):
        """显示系统提示消息
        特点：不可编辑、自动滚动、特殊样式
        """
        self.chat_display.config(state='normal')  # 临时启用编辑状态
        self.chat_display.insert(END, msg + "\n")  # 插入消息内容
        self.chat_display.see(END)  # 自动滚动到底部
        self.chat_display.config(state='disabled')  # 恢复禁用状态

    def show_chat_message(self, msg):
        """显示普通聊天消息
        与系统消息区别：不添加时间戳和特殊标识
        """
        self.chat_display.config(state='normal')  # 临时启用编辑状态
        self.chat_display.insert(END, msg + "\n")  # 插入消息内容
        self.chat_display.see(END)  # 自动滚动到底部
        self.chat_display.config(state='disabled')  # 恢复禁用状态

if __name__ == "__main__":
    ChatClientGUI()  # 启动客户端应用程序