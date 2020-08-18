from mc.blocks import BlockID


# =====Limits=====
# Packet type: 255

def encode_blockid(block_id):
    if isinstance(block_id, tuple):
        main, sub = block_id
    elif isinstance(block_id, BlockID):
        main, sub = block_id.main, block_id.sub
    else:
        raise ValueError('encode_blockid: block_id required to be (main, sub) or an instance of BlockID')
    return int.to_bytes(main, 16, 'big') + int.to_bytes(sub, 1, 'big')

def decode_blockid(bytestr):
    main = bytestr[:-1]
    sub  = bytestr[-1:]
    out = BlockID(int.from_bytes(main, 'big'), int.from_bytes(sub, 'big'))

def encode_length(length):
    return int.to_bytes(length, 32, 'big')

def decode_length(blength):
    return int.from_bytes(blength, 'big')

def decode_packettype(ptype):
    return int.from_bytes(ptype, 'big')

def encode_packettype(ptype):
    return int.to_bytes(ptype, 1, 'big')

def encode_string(text):
    out = b''
    out += int.to_bytes(len(text), 2, 'big')
    out += text.encode('utf-8')
    return out

def decode_string(btext):
    return btext.decode('utf-8')

def encode_color(color):
    if not isinstance(color, tuple):
        raise ValueError('encode_color: color required to be (red, green, blue, alpha) ranging from 1-255')
    out = b''
    for component in color:
        out += int.to_bytes(component, 1, 'big')
    return out

def decode_color(bcolor):
    r = bcolor[:-3].from_bytes('big')
    g = bcolor[-3:-2].from_bytes('big')
    b = bcolor[-2:-1].from_bytes('big')
    a = bcolor[-1:].from_bytes('big')
    return (r, g, b, a)

encode_username = encode_string
decode_username = decode_string

def send_packet(sock, payload):
    packet = encode_length(len(payload)) + payload
