import pyglet
from pyglet.gl import *
import globals as G


def colorize_grass():
    return ('c4B/stream',((92, 200, 66, 0)*4))

def cube_vertices(pos,n=0.5):
    x,y,z = pos; v = tuple((x+X,y+Y,z+Z) for X in (-n,n) for Y in (-n,n) for Z in (-n,n))
    return tuple(tuple(k for j in i for k in v[j]) for i in ((0,1,3,2),(5,4,6,7),(0,4,5,1),(3,7,6,2),(4,0,2,6),(1,5,7,3)))

class Block:
    #'top', 'bottom', 'side'
    files = []
    collidable = True
    
    def get_tex(self,file):
        tex = G.RESOURCE_LOADER.texture(file)
        glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
        return pyglet.graphics.TextureGroup(tex)
    
    def __init__(self):
        #'left','right','bottom','top','back','front'
        self.tex = [self.get_tex(self.files[2]), self.get_tex(self.files[2]), self.get_tex(self.files[1]), self.get_tex(self.files[0]), self.get_tex(self.files[2]), self.get_tex(self.files[2])]
    
    def cuboid(self, pos, batch):
        tex_coords = ('t2f/stream',(0,0, 1,0, 1,1, 0,1))

        x,y,z = pos
        X,Y,Z = x+1,y+1,z+1
        cube = []
        verts = cube_vertices(pos)
        for i in (0, 1, 2, 3, 4, 5):
            cube.append(batch.add(4,GL_QUADS,self.tex[i],('v3f/stream',verts[i]), tex_coords, ('c3B', ((127, 127, 127)*4))))
        return tuple(cube)
    
    
    def draw(self, pos, batch):
        return self.cuboid(pos, batch)

class GrassBlock(Block):
    files = ['grass_block_top.png','dirt.png','grass_block_side.png']
    
    def cuboid(self, pos, batch):
        tex_coords = ('t2f/stream',(0,0, 1,0, 1,1, 0,1, ))
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

class DirtBlock(Block):
    files = ['dirt.png','dirt.png','dirt.png'] 
