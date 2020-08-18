from mc.serverclient.native.client import PacketReciever as pr
import socket

def test_pr():
    sock = socket.socket()
    sock.connect(('localhost', 1486))

    packetreciever = pr(None, None, sock)
    packetreciever.start()
    packetreciever.login(input('Enter username:'))
    while True:
        if packetreciever.sector_packets:
            packetreciever.dequeue_packet()
