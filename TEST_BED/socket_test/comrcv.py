from socket import socket, AF_INET, SOCK_STREAM

HOST        = 'localhost'
PORT        = 51000
MAX_MESSAGE = 2048
NUM_THREAD  = 4

CHR_CAN     = '\18'
CHR_EOT     = '\04'

def com_receive():

    # 通信の確立
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind    ((HOST, PORT))
    sock.listen  (NUM_THREAD)
    print ('receiver ready, NUM_THREAD  = ' + str(NUM_THREAD))

    # メッセージ受信ループ
    while True:
        try:
            conn, addr = sock.accept()
            mess       = conn.recv(MAX_MESSAGE).decode('utf-8')
            conn.close()

            # 終了要求？
            if (mess == CHR_EOT):
                break

            # キャンセル？
            if (mess == CHR_CAN):
                print('cancel')
                continue

            # テキスト
            print ('message:' + mess)

        except:
            print ('Error:' + mess)

    # 通信の終了
    sock.close()
    print ('end of receiver')

def proc():
    com_receive()

proc()
