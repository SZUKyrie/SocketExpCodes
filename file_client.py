from socket import *  # 网络通信库

# 配置服务器地址和端口
SERVER_IP = 'localhost'   
SERVER_PORT = 12000

# 创建TCP套接字并连接服务器
client_socket = socket(AF_INET, SOCK_STREAM)  # AF_INET: IPv4, SOCK_STREAM: TCP
client_socket.connect((SERVER_IP, SERVER_PORT))
print("[CLIENT] 已连接到服务器")

# 输入请求的文件名并发送
filename = input("请输入要下载的文件名: ").strip()  # 去除输入两端的空格
client_socket.send(filename.encode())          # 编码为字节流后发送
print(f"[CLIENT] 已发送文件请求: {filename}")

# 初始化接收参数
received_data = b''         # 存储接收到的二进制数据
total_received = 0          # 已接收总字节数
chunk_count = 0             # 分块计数器
print(f"[CLIENT] 开始接收文件...")

try:
    # 分块接收数据
    while True:
        chunk = client_socket.recv(4096)  # 接收最多4096字节（与服务器分块大小一致）
        if not chunk:  # 接收空数据表示传输结束
            break
        received_data += chunk
        chunk_size = len(chunk)
        total_received += chunk_size
        chunk_count += 1
        # 打印实时接收信息
        print(f"[CLIENT] 分块 #{chunk_count}: 接收 {chunk_size} 字节 | 累计: {total_received} 字节")

except Exception as e:
    print(f"[CLIENT] 接收异常: {e}")

# 处理接收结果
if received_data == b'FileNotFound':
    print(f"[CLIENT] 错误: 服务器未找到文件 '{filename}'")
else:
    # 保存文件
    new_filename = f"received_by_client.txt"
    with open(new_filename, 'wb') as f:  # 二进制写模式保存
        f.write(received_data)
    print(f"[CLIENT] 文件已保存为 '{new_filename}'")
    print(f"[CLIENT] 总计接收分块数: {chunk_count}, 总字节数: {total_received}")

# 关闭连接
client_socket.close()
print("[CLIENT] 连接已关闭")