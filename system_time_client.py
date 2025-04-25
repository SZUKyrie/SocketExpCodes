from socket import *

# 1. 配置服务器地址
server_name = 'localhost'  # 若服务器在远程，需改为服务器IP
server_port = 12000

# 2. 创建TCP套接字并连接
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_name, server_port))
print("[CLIENT] Connected to server. Enter 'Time' or 'Exit'.")

# 3. 交互循环
while True:
    command = input("> ").strip()
    client_socket.send(command.encode())  # 发送命令

    if command == "Exit":
        response = client_socket.recv(1024).decode()
        print(f"[CLIENT] Server says: {response}")
        break

    response = client_socket.recv(1024).decode()
    print(f"[CLIENT] Server time: {response}")

# 4. 关闭连接
client_socket.close()
print("[CLIENT] Connection closed.")