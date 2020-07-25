import pyglet
from pyglet.gl import *
import mc.globals as G
from mc.utils_py import *

def colorize_grass():
    return ('c4B/stream',((92, 200, 66, 255)*4))

class BlockID:
    main, sub = None, None
    def __init__(self, main, sub=0): self.main=main; self.sub=sub
    def __eq__(self, other): return self.main == other.main and self.sub == other.sub

class Block:
    #'top', 'bottom', 'side'
    files = []
    collidable = True
    name = ''
    id = BlockID(0)
    
    def get_tex(self,file):
        tex = G.RESOURCE_LOADER.texture(file)
        glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
        return pyglet.graphics.TextureGroup(tex)
    
    def __init__(self):
        #'left','right','bottom','top','back','front'
        G.BLOCKS_DIR[(self.id.main, self.id.sub)] = self
        if self.files == []:
            self.tex = None
            return
        self.tex = [self.get_tex(self.files[2]), self.get_tex(self.files[2]), self.get_tex(self.files[1]), self.get_tex(self.files[0]), self.get_tex(self.files[2]), self.get_tex(self.files[2])]
    
    def cuboid(self, pos, batch):
        tex_coords = ('t2f/stream',(0,0, 1,0, 1,1, 0,1))

        x,y,z = pos
        X,Y,Z = x+1,y+1,z+1
        cube = []
        verts = cube_vertices(pos)
        for i in (0, 1, 2, 3, 4, 5):
            cube.append(batch.add(4,GL_QUADS,self.tex[i],('v3f/stream',verts[i]), tex_coords, ('c4B', ((127, 127, 127, 255)*4))))
        return tuple(cube)
    
    
    def draw(self, pos, batch):
        if self.tex:
            return self.cuboid(pos, batch)

class Grass(Block):
    files = ['grass_block_top.png','dirt.png','grass_block_side.png']
    name = 'Grass'
    id = BlockID(2)
    
    def cuboid(self, pos, batch):
        tex_coords = ('t2f/stream',(0,0, 1,0, 1,1, 0,1))
        f = 'left','right','bottom','top','back','front'
        x,y,z = pos
        X,Y,Z = x+1,y+1,z+1
        cube = []
        verts = cube_vertices(pos)
        for i in (0, 1, 2, 3, 4, 5):
            if f[i] != 'top':
                cube.append(batch.add(4,GL_QUADS,self.tex[i],('v3f/stream',verts[i]), tex_coords, ('c3B', ((127,127, 127)*4))))
            else:
                cube.append(batch.add(4,GL_QUADS,self.tex[i],('v3f/stream',verts[i]), tex_coords, colorize_grass()))

        return tuple(cube)

class Dirt(Block):
    name = 'Dirt'
    files = ['dirt.png','dirt.png','dirt.png']
    id = BlockID(3)

class Stone(Block):
    name = 'Stone'
    files = ['stone.png', 'stone.png', 'stone.png']
    id = BlockID(1)
    
class Cobblestone(Block):
    name = 'Cobblestone'
    files = ['cobblestone.png','cobblestone.png','cobblestone.png']
    id = BlockID(4)

class Bedrock(Block):
    name = 'Bedrock'
    files = ['bedrock.png','bedrock.png','bedrock.png']
    id = BlockID(7)

class IronOre(Block):
    name = 'Iron Ore'
    files = ['iron_ore.png','iron_ore.png','iron_ore.png']
    id = BlockID(15)

class CoalOre(Block):
    name = 'Coal Ore'
    files = ['coal_ore.png','coal_ore.png','coal_ore.png']
    id = BlockID(16)

class RedstoneOre(Block):
    name = 'Redstone Ore'
    files = ['redstone_ore.png','redstone_ore.png','redstone_ore.png']
    id = BlockID(73)
class DiamondOre(Block):
    name = 'Diamond Ore'
    files = ['diamond_ore.png','diamond_ore.png','diamond_ore.png']
    id = BlockID(56)
class Air(Block):
    name = 'Air'
    id = BlockID(0)
