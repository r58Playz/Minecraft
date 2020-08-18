import socket
from threading import Thread, Lock, Event
from collections import deque
from mc.serverclient.native.utils import *
class PacketReciever(Thread):
    def __init__(self, world, window, sock):
        Thread.__init__(self)
        self.world = world
        self.window = window
        self.sock = sock
        self.lock = Lock()
        self.sector_packets = deque()
        self._stop = Event()
        self.append_to_sector_packets   = self.sector_packets.append
        self.remove_from_sector_packets = self.sector_packets.pop
        
    
    def run(self):
        try:
            self.loop()
        except socket.error as e:
            if e[0] in (10053, 10054):
                #TODO: GUI tell the client they were disconnected
                print("Disconnected from server.")
            else:
                raise e
    
    def loop(self):
        packetcache, packetsize = b"", 0

        append_to_sector_packets = self.append_to_sector_packets
        while 1:
            resp = self.sock.recv(16384)
            print(resp)
            if self._stop.isSet() or not resp:
                print("Client PacketReceiver:",self._stop.isSet() and "Shutting down" or "We've been disconnected by the server")
                self.sock.shutdown(SHUT_RDWR)
                return

            # Sometimes data is sent in multiple pieces, just because sock.recv returned data doesn't mean its complete
            # So we write the datalength in the beginning of all messages, and don't look at the packet until we have enough data
            packetcache += resp
            if not packetsize and len(packetcache) >= 1:
                packetsize = struct.unpack("i", packetcache[:4])[0]

            # Sometimes we get multiple packets in a single burst, so loop through packetcache until we lack the data
            while packetsize and len(packetcache) >= packetsize:
                #Once we've obtained the whole packet
                packetid = decode_packettype(packetcache[:1])  # Server Packet Type
                packet = packetcache[2:packetsize]

                with self.lock:
                    append_to_sector_packets((packetid, packet))

                packetcache = packetcache[packetsize:]  # Cut off the part we just read
                packetsize = struct.unpack("i", packetcache[:4])[0] if len(packetcache) >= 4 else 0  # Get the next packet's size
    
    def dequeue_packet(self):
        with self.lock:
            packettype, packet = self.remove_from_sector_packets()
        if packettype == 1: # Entire Sector
            print('Complete sector recieved')
        elif packettype == 3:    # Movement packet
            print('Movement Packet recieved')
        elif packettype == 4:    # Jump     packet
            print('Jump packet recieved')
        elif packettype == 5:    # Add      block
            print('Add block request recieved')
        elif packettype == 6:    # Remove   block
            print('Remove block request recieved')
        elif packettype == 255:
            print('Recieved login confirmation')
    
    def login(self, username):
        packet = b''
        packet += encode_packettype(255)
        packet += encode_username(username)
        self.sock.send(packet)
