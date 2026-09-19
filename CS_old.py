import socket as s
import glob
from itertools import islice
import sys
import time

PORT = 39871
BUFFER = 1024
EOF_Flag = b'---EOF---EOF---FCSFLAG---...---EOF---EOF---FCSFLAG---'
CONT_Flag = b'CONTINUE---...000--...FCGFLAG'

def Wait(Socket):
    return Socket.recv(BUFFER)

def Continue(Socket):
    Socket.send(b'wait')


def Find():
    #Pattern = 'C:/**/*.txt'
    Pattern = './*.jpg'
    #return list(islice(glob.iglob(Pattern, recursive=True), 3))
    return list(glob.iglob(Pattern, recursive=True))


def GetFilename(Msg):
    new = Msg.split('/')
    return new[-1]

def TryToDecode(msg):
    try:
        out = msg.decode()
        return out
    except:
        return -1



def Receiver():
    Socket = s.socket(s.AF_INET, s.SOCK_STREAM)

    Socket.bind(("", PORT))

    Socket.listen(3)

    ClientSocket, Info = Socket.accept()
    print("acc")
    print(Info)

    msg = ""
    while True:
        msg = ClientSocket.recv(256).decode() # filename
        if msg == '':
            break
        Continue(ClientSocket)
        print("file--- " + msg)
        f = open(msg, 'wb+')
        while True:
            flag = Wait(ClientSocket)
            if flag == CONT_Flag:
                Continue(ClientSocket)
                f.write(ClientSocket.recv(BUFFER))
            else:
                f.close()
                break
        print("Downloaded...")
        Continue(ClientSocket)


def Sender():
    Socket = s.socket(s.AF_INET, s.SOCK_STREAM)
    while True:
        try:
            Socket.connect(("127.0.0.1", PORT))
        except:
            continue
        break
    list = Find()
    ll = len(list)-1
    print(ll)
    while ll != -1:
        print(list)
        name = GetFilename(list[ll])
        Socket.send(name.encode())
        Wait(Socket)
        f = open(list[ll], 'rb')
        while True:
            datas = f.read(BUFFER)
            if datas == b'':
                Socket.send(EOF_Flag)
                break
            else:
                Socket.send(CONT_Flag)
                Wait(Socket)
                Socket.send(datas)
        list.remove(name)
        print(list)
        print("file done")
        Wait(Socket)
        print("\n\n"+str(ll))
        ll-=1

    
    


if __name__ == "__main__":

    cs = int(sys.argv[1])

    print(cs)

    if cs==1:
        Sender()

    else:
        Receiver()
