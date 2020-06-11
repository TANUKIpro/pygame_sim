from socket import socket, AF_INET, SOCK_STREAM

HOST        = 'localhost'
PORT        = 51000

CHR_CAN     = '\18'
CHR_EOT     = '\04'

def com_send(mess):
    while True:
        try:
            # 通信の確立
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect((HOST, PORT))

            # メッセージ送信
            sock.send(mess.encode('utf-8'))

            # 通信の終了
            sock.close()
            break

        except:
            print ('retry: ' + mess)


def proc():
    com_send('message test')

def exit():
    com_send(CHR_EOT)

def cancel():
    com_send(CHR_CAN)

import time
while True:
    proc()
    time.sleep(1)
