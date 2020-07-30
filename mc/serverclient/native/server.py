import socket
import socketserver


class ServerPlayer:
    

class Server(socketserver.ThreadingTCPServer):
    players = {} #id to player
    ids = {}     #player to id
