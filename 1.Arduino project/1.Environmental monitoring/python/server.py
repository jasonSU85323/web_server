#coding=utf-8
import socket
import sys

sys.path.insert(0, '/usr/lib/python2.7/bridge/')
from bridgeclient import BridgeClient as bridgeclient

def accept_aonn(conn):

        data = conn.recv(1024)
        print(data)
        if data == "one":
                value = bridgeclient()
                number = value.get('one')
                conn.send(str(number))
                # jsonData = { 'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5 }
                # jason = json.dumps(jsonData)
                # conn.sendall(jason)
                return 1

        elif data == "Humidity":
                value = bridgeclient()
                number = value.get('Humidity')
                conn.send(str(number))
                return 1

        elif data == "TemperC":
                value = bridgeclient()
                number = value.get('TemperC')
                conn.send(str(number))
                return 1
                
        elif data == "TemperF":
                value = bridgeclient()
                number = value.get('TemperF')
                conn.send(str(number))
                return 1
                
        elif data == "sensor":
                value = bridgeclient()
                number = value.get('sensor')
                conn.send(str(number))
                return 1
                
        elif data == "Air":
                value = bridgeclient()
                number = value.get('Air')
                conn.send(str(number))
                return 1
                
        elif data == "Dust":
                value = bridgeclient()
                number = value.get('Dust')
                conn.send(str(number))
                return 1
                
        elif data == "ampere":
                value = bridgeclient()
                number = value.get('ampere')
                conn.send(str(number))
                return 1

        elif data == "4":
                print "client:close server socker!!!"
                return 0

        else:
                print "client:All"
                return 1

if __name__ == '__main__':
        HOST = ''
        PORT = 8888

        try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
                print("Create socket FALL!!")
        else:
                print("Socket created")

        try:
                s.bind((HOST, PORT))
        except socket.error as msg:
                print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
                sys.exit()
        else:
                print("Binding the address OK!")

        s.listen(5)
        print('Socket is listenin')

        print("\ntry to accept the connect:")
        switch = 1
        while switch:
                conn, addr = s.accept()
                print '\nConnected with ' + addr[0] + ':' + str(addr[1])
                switch = accept_aonn(conn)

        conn.close()
        s.close()
        sys.exit()