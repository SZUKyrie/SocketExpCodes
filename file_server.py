# 导入必要的库
from socket import *  # 网络通信库
import os             # 文件路径和操作系统相关功能

# 定义服务器端口和块大小
SERVER_PORT = 12000   # 服务器监听端口
CHUNK_SIZE = 4096     # 分块大小（4KB）

# 创建TCP套接字
server_socket = socket(AF_INET, SOCK_STREAM)  # AF_INET: IPv4地址族，SOCK_STREAM: TCP协议
server_socket.bind(('', SERVER_PORT))         # 绑定所有可用网络接口（IP为空字符串）和指定端口
server_socket.listen(5)                       # 开始监听，允许最多5个等待连接的客户端
print(f"[SERVER] 文件服务器已启动，监听端口 {SERVER_PORT}")

# 主循环：持续接受客户端连接
while True:
    # 接受新客户端连接
    conn_socket, client_addr = server_socket.accept()  # 阻塞等待客户端连接，返回新套接字和客户端地址
    print(f"[SERVER] 已连接到客户端: {client_addr}")

    try:
        # 接收客户端请求的文件名（最大1024字节）
        filename = conn_socket.recv(1024).decode().strip()  # 解码为字符串并去除两端空格
        print(f"[SERVER] 收到文件请求: {filename}")

        # 检查文件是否存在
        if not os.path.exists(filename):
            conn_socket.sendall(b'FileNotFound')  # 发送错误标识（字节流）
            print(f"[SERVER] 文件 '{filename}' 不存在")
            continue  # 跳过后续代码，继续等待下一个请求

        # 获取文件总大小
        file_size = os.path.getsize(filename)
        print(f"[SERVER] 开始发送文件 '{filename}' (大小: {file_size} 字节)")

        # 分块读取并发送文件
        total_sent = 0    # 已发送总字节数
        chunk_count = 0    # 分块计数器
        with open(filename, 'rb') as f:  # 以二进制读模式打开文件
            while True:
                chunk = f.read(CHUNK_SIZE)  # 读取一个块（最多CHUNK_SIZE字节）
                if not chunk:  # 文件读取完毕（chunk为空）
                    break
                # 发送当前块数据
                conn_socket.sendall(chunk)  # sendall确保所有数据被发送
                sent_bytes = len(chunk)
                total_sent += sent_bytes
                chunk_count += 1
                # 打印实时传输信息
                print(f"[SERVER] 分块 #{chunk_count}: 发送 {sent_bytes} 字节 | 累计: {total_sent}/{file_size} 字节")

        # 文件发送完成
        print(f"[SERVER] 文件发送成功! 总分块数: {chunk_count}, 总字节数: {total_sent}")

    except Exception as e:
        print(f"[SERVER] 传输异常: {e}")
    finally:
        # 关闭当前连接（无论是否出错）
        conn_socket.close()
        print(f"[SERVER] 连接已关闭: {client_addr}\n")