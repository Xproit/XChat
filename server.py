import socket
import threading

# 配置信息
HOST = '0.0.0.0'  # 监听所有网卡
PORT = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

# 广播消息给所有人
def broadcast(message):
    for client in clients:
        client.send(message)

# 处理客户端连接的核心逻辑
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            # 发生错误或客户端断开，清理数据
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} 离开了聊天室！'.encode('utf-8'))
            nicknames.remove(nickname)
            break

# 接收新连接的主循环
def receive():
    print(f"服务端已启动，正在监听端口 {PORT}...")
    while True:
        client, address = server.accept()
        print(f"已连接来自 {str(address)} 的用户")

        # 获取用户名并存储
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f"该用户的昵称是 {nickname}")
        broadcast(f"{nickname} 加入了聊天！\n".encode('utf-8'))
        client.send('已成功连接到服务器！'.encode('utf-8'))

        # 为每个客户端开启独立线程处理
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

receive()