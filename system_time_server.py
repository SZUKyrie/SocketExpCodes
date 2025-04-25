from socket import *
import time
import datetime

# 1. 创建TCP套接字
server_port = 12000
server_socket = socket(AF_INET, SOCK_STREAM)  # AF_INET: IPv4, SOCK_STREAM: TCP
server_socket.bind(('', server_port))         # 绑定所有可用IP和端口12000
server_socket.listen(5)                       # 允许最多5个排队连接
print(f"[SERVER] Time server is running on port {server_port}")

# 2. 持续监听客户端连接
while True:
    # 接受新连接
    conn_socket, client_addr = server_socket.accept()
    print(f"[SERVER] Connected to client: {client_addr}")

    try:
        # 3. 处理客户端请求
        while True:
            request = conn_socket.recv(1024).decode().strip()  # 接收客户端数据
            if not request:  # 客户端关闭连接时收到空数据
                break

            print(f"[SERVER] Received from {client_addr}: '{request}'")

            # 4. 根据请求类型响应
            if request == "Time":
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn_socket.send(current_time.encode())
                print(f"[SERVER] Sent time: {current_time}")
            elif request == "Exit":
                conn_socket.send(b"Bye")
                break
            else:
                conn_socket.send(b"Invalid command")
    finally:
        # 5. 关闭当前连接
        conn_socket.close()
        print(f"[SERVER] Connection closed: {client_addr}\n")