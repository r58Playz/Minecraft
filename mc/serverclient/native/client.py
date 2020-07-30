import socket
from threading import Thread, Lock, Event
from collections import deque

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
        
