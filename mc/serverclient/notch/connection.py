
class ConnectionContext:
    '''simple class to house the protocol version'''
    __slots__ = ('protocol_version')
    protocol_version = None
    def __init__(self, protocol_version):
        self.protocol_version = protocol_version
