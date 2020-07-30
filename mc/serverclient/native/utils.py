from mc.blocks import BlockID
 
def encode_blockid(block_id):
    if isinstance(block_id, tuple):
        main, sub = block_id
    elif isinstance(block_id, BlockID):
        main, sub = block_id.main, block_id.sub
    else:
        raise ValueError('encode_blockid: block_id required to be (main, sub) or an instance of BlockID')
    return main.to_bytes(16, 'big') + sub.to_bytes(1, 'big')

def decode_blockid(bytestr):
    main = bytestr[:-1]
    sub  = bytestr[-1:]
    out = BlockID(int.from_bytes(main, 'big'), int.from_bytes(sub, 'big'))
