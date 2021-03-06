#-*- encoding: utf-8 -*-

from flask import Flask, render_template
from flask_socketio import SocketIO
import socketserver
import threading
import time

############# socket io parameter #############

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

############# socket with zynq run #############

class MyTcpHandler(socketserver.BaseRequestHandler):
    # def __init__(self, request, client_address, server):
    #     super(MyTcpHandler, self).__init__(request, client_address, server)
    #     self.data = ''

    def handle(self):
        print('...connected from:', self.client_address)
        while True:
            try:
                data = self.request.recv(16).strip().decode()
                self.server.data = data
                
                if data == '###':
                    print(self.client_address, 'exit')
                    break
                
                # print(self.data_obj.data)
                # time.sleep(1)     # 不能sleep，否则说不定缓冲区被阻塞住导致一次性收到了多次发送的数据
                
            except Exception as e:
                print("[+] Error", e)
                break
            
            except KeyboardInterrupt:
                print('[+] Connection close')
                break
            
############# socket io run #############

@app.route('/')
def hello_world():
    return render_template('index.html')

@socketio.on('connect', namespace='/message')
def send_message():
    socketio.start_background_task(target=background_func)

def background_func():
    while True:
        socketio.emit('server_response', {'data': tcpSerSock.data}, namespace='/message')
        # socketio.sleep(1)



if __name__ == '__main__':
    app_thread = threading.Thread(target=socketio.run, args=(app,))
    # socketio.run(app)
    app_thread.daemon = True    # daemon attribute causes the thread to terminate when the main process ends.
    app_thread.start()

    # HOST, PORT = "localhost", 6887     # 这里localhost务必换成本机ip地址，否则一般外部无法访问！！！！
    # HOST, PORT = "192.168.2.117", 6887     # 这里localhost务必换成本机ip地址，否则一般外部无法访问！！！！
    # HOST, PORT = "172.20.165.210", 6887     # 这里localhost务必换成本机ip地址，否则一般外部无法访问！！！！
    HOST, PORT = "192.168.177.105", 6887     # 这里localhost务必换成本机ip地址，否则一般外部无法访问！！！！
    tcpSerSock = socketserver.ThreadingTCPServer((HOST, PORT), MyTcpHandler)
    tcpSerSock.data = '###'
    print('waiting for connection...')

    try:
        tcpSerSock.serve_forever()
    except:
        pass
    finally:
        tcpSerSock.server_close()
        print('Server close')