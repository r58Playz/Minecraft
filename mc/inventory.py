import pyglet
import mc.globals as G
from pyglet.gl import *


class Hotbar:
    file='textures/gui/widgets.png'
    tex = None
    batch = None
    vlist = None
    def __init__(self, winwidth, winheight):
        self.x, self.y = (winwidth//2)-181, 30
        self.tex = pyglet.graphics.TextureGroup(G.RESOURCE_LOADER.texture(self.file))
        self.batch = pyglet.graphics.Batch()
    
    def add(self):
        tex_coords = ('t2f',(0,0.915, 0.75,0.915, 0.75,1, 0,1))
        self.vlist = self.batch.add(4,GL_QUADS, self.tex, tex_coords, ('v2i', (self.x, self.y, self.x+362, self.y, self.x+362, self.y+44, self.x, self.y+44)), ('c3B', ((127, 127, 127)*4)))
    def remove(self):
        self.vlist.delete()
#175, 166
class Inventory:
    file='textures/gui/container/inventory.png'
    tex = None
    batch = None
    vlist = None
    def __init__(self, winwidth, winheight):
        self.x, self.y = (winwidth//2)-130, (winheight//2)-110
        self.tex = pyglet.graphics.TextureGroup(G.RESOURCE_LOADER.texture(self.file))
        self.batch = pyglet.graphics.Batch()
    
    def add(self):
        tex_coords = ('t2f/stream',(0,0.35, 0.69,0.35, 0.69,1, 0,1))
        self.vlist = self.batch.add(4,GL_QUADS, self.tex, tex_coords, ('v2i', (self.x, self.y, self.x+250, self.y, self.x+250, self.y+232, self.x, self.y+232)), ('c3B', ((127, 127, 127)*4)))
    def remove(self):
        self.vlist.delete()
    
