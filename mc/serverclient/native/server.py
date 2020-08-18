import socket
import socketserver
from mc.serverclient.native.world_server import WorldServer
from mc.serverclient.native.utils import *
import threading
from warnings import warn

class ServerPlayer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.username = str(self.client_address)
        print("Client connecting...", self.client_address)
        self.server.players[self.client_address] = self
        self.server.player_ids.append(self)
        self.id = len(self.server.player_ids) - 1
        try:
            self.loop()
        except socket.error as e:
            if self.server._stop.isSet():
                return  # Socket error while shutting down doesn't matter
            if e[0] in (10053, 10054):
                #TODO F-strings
                print("Client %s %s crashed." % (self.username, self.client_address))
            else:
                raise e
    def loop(self):
        world, players = self.server.world, self.server.players
        while 1:
            byte = self.request.recv(1)
            if not byte: return  # The client has disconnected intentionally

            packettype = decode_packettype(byte) # Client Packet Type
            if   packettype == 1:    # Sector   request
                print('Sector Request initiated')
            elif packettype == 3:    # Movement packet
                print('Movement Packet recieved')
            elif packettype == 4:    # Jump     packet
                print('Jump packet recieved')
            elif packettype == 5:    # Add      block
                print('Add block request recieved')
            elif packettype == 6:    # Remove   block
                print('Remove block request recieved')
            elif packettype == 255: # Initial  Login
                print('Client login')
                txtlen = int.from_bytes(self.request.recv(2), 'big')
                print(decode_username(self.request.recv(txtlen)))
                self.request.send(encode_packettype(255))

class Server(socketserver.ThreadingTCPServer):
    def __init__(self, *args, **kwargs):
        socketserver.ThreadingTCPServer.__init__(self, *args, **kwargs)
        self._stop = threading.Event()

        self.world = WorldServer(self)
        self.players = {}  # Dict of all players connected. {ipaddress: requesthandler,}
        self.player_ids = []  # List of all players this session, indexes are their ID's [0: first requesthandler,]

def start_server():
    server = Server(('localhost',1486), ServerPlayer)
    server.serve_forever()
if __name__ == '__main__':
    start_server()
