import threading
import argparse
import signal
import socket

Realpass = "BOOYFgbEIYVFBOIBFOgehpiUFHIPG9FY9H974YRH932HR087G8G-87GT0872R9G083GpG08G3R8PGF08FG038FGP7W3G#@)(&*^a"
ip = "90.194.66.47"


class Tunnel(object):

    def __init__(self, clientsock, proxaddr=None, proxport=None):

        self.clientsock = clientsock

        self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if Client:
            self.proxaddr = proxaddr
            self.proxport = proxport

            self.targaddr = raw_input('Target Ip\n:> ')
            self.targport = raw_input('Target Port\n:> ')

            try:
                socket.inet_aton(self.targaddr)
            except Exception:
                try:
                    socket.inet_aton(socket.gethostbyname(self.targaddr))
                    self.targaddr = socket.gethostbyname(self.targaddr)
                except:
                    print('[*] Target address is not a valid IP address. Valid IP addresses are in the format: (0-255).(0-255).(0-255).(0-255).')
                    self.clientsock.close()
                    return

            if self.targport.isdigit() is False:
                print('[*] Target port is not an integer.')
                return

            if int(self.targport) not in range(1, 65535):
                print('[*] Target port is not a valid port number. A valid port number lies within the range 1-65535.')
                self.clientsock.close()
                return

        else:

            try:
                self.targaddr, self.targport = self.clientsock.recv(21).split(':')
                #print('[*] Recieving target server information from client.')

                try:
                    socket.inet_aton(self.targaddr)
                except Exception:
                    print('Target address is not valid.')
                    self.clientsock.send('FAILED')
                    self.clientsock.close()
                    return

                if int(self.targport) not in range(1, 65535):
                    print('Target port is not valid.')
                    self.clientsock.send('FAILED')
                    self.clientsock.close()
                    return

                self.clientsock.send('OK')

            except Exception:

                print('[*] Failed to successfully create tunnel, reason: Client incorrectly entered target server details.')
                self.clientsock.close()
                return

        try:

            if Client:
                self.serversock.connect((self.proxaddr, self.proxport))
                print('[*] Sending authentication and continuing.')

                self.serversock.send(Realpass)

                if self.serversock.recv(6) == 'FAILED':
                    print('[*] Auth failed')
                    return

                self.serversock.send('%s:%s' % (self.targaddr, self.targport))

                if self.serversock.recv(6) == 'FAILED':
                    print('Target server details malformed.')
                    return

                print('[*] Initiating tunnel.')
            else:
                self.serversock.connect((self.targaddr, int(self.targport)))
                #print('[*] Connecting to target server.')

        except Exception:
            print('[*] Failed to successfully create tunnel.')

            self.clientsock.close()
            return

    class ToServer(threading.Thread):
        def __init__(self, clientsock, serversock):
            threading.Thread.__init__(self)

            self.clientsock = clientsock
            self.serversock = serversock

        @staticmethod
        def cleanup():
            exit()

        def run(self):
            while True:

                try:
                    data = self.clientsock.recv(10000)
                    self.serversock.send(data)
                except Exception:
                    print('[*]<%s> Connection closed.' % self.name)
                    self.clientsock.close()
                    self.serversock.close()
                    return

    class ToClient(threading.Thread):
        def __init__(self, clientsock, serversock):
            threading.Thread.__init__(self)

            self.clientsock = clientsock
            self.serversock = serversock

        @staticmethod
        def cleanup():
            exit()

        def run(self):
            while True:

                try:
                    data = self.serversock.recv(10000)
                    self.clientsock.send(data)
                except Exception:
                    print('[*]<%s> Connection closed.' % self.name)
                    self.clientsock.close()
                    self.serversock.close()
                    return

    def start(self):
        if Client:
            print('[*] Initialized peer to peer tunnel.')

        toserver = self.ToServer(self.clientsock, self.serversock)
        toclient = self.ToClient(self.clientsock, self.serversock)

        toserver.start()
        toclient.start()


def parseargs():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    clientparser = subparsers.add_parser('client', help='Flags for client instances.')

    clientparser.add_argument('-a', '--bind-address', dest='Bindaddr', action='store', required=True, type=str, help='Address which you wish to bind this client to')
    clientparser.add_argument('-b', '--bind-port', dest='Bindport', action='store', default=9999, type=int, help='Port which you wish this client to bind to')
    clientparser.add_argument('-s', '--proxy-server', dest='Proxaddr', action='store', required=True, type=str, help='Ip address of the proxy server')
    clientparser.add_argument('-p', '--proxy-port', dest='Proxport', action='store', default=80, type=int, help='Port of the proxy server')

    serverparser = subparsers.add_parser('server', help='Flags for server instances.')

    serverparser.add_argument('-a', '--bind-address', dest='Bindaddr', action='store', required=True, type=str, help='Address which you wish to bind this server to')
    serverparser.add_argument('-b', '--bind-port', dest='Bindport', action='store', default=9999, type=int, help='Port which you wish this server to bind to')

    args = parser.parse_args()

    return vars(args)


def sighand(*args):
    for thread in threading.enumerate():
        if str(thread).find('Main') == -1:
            thread.cleanup()

    exit()


def main():
    signal.signal(signal.SIGINT, sighand)

    global Client
    Client = False

    args = parseargs()

    bindaddr = args['Bindaddr']
    bindport = args['Bindport']

    try:
        socket.inet_aton(bindaddr)
    except socket.error:
        print('Bind address is not a valid IP address. Valid IP addresses are in the format: (0-255).(0-255).(0-255).(0-255).')
        return

    if bindport not in range(1, 65535):
        print('Bind port is not a validport number. A valid port number lies within the range 1-65535.')
        return

    if len(args) != 2:
        Client = True
        proxaddr = args['Proxaddr']
        proxport = args['Proxport']

        try:
            socket.inet_aton(proxaddr)
        except socket.error:
            print('Proxy address is not a valid IP address. Valid IP addresses are in the format: (0-255).(0-255).(0-255).(0-255).')
            return

        if proxport not in range(1, 65535):
            print('Proxy port is not a validport number. A valid port number lies within the range 1-65535.')
            return

    mainsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        mainsock.bind((bindaddr, bindport))
    except socket.error:
        print('[*] Could not bind to port. Maybe the specified address is incorrect.')
        mainsock.close()
        return

    mainsock.listen(5)

    while True:
        clientsock, clientdetails = mainsock.accept()
        print('[*] Recieved new connection from %s:%d' % (clientdetails[0], clientdetails[1]))

        if Client:
            newtunnel = Tunnel(clientsock, proxaddr=proxaddr, proxport=proxport)
        else:
            #print('[*] Waiting for authentication before continuing.')

            try:
                targpass = clientsock.recv(100)
            except Exception:
                print('[*] Connection closed by peer.')
                continue

            if targpass != Realpass:
                print('[*] Authentication failed, closing connection.')
                clientsock.send('FAILED')
                clientsock.close()
                continue
            else:
                clientsock.send('OK')
                newtunnel = Tunnel(clientsock)

        newtunnel.start()


if __name__ == '__main__':
    main()
