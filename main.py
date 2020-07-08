from pyglet.gl import *
from pyglet.window import key, mouse
import math
from collections import defaultdict, deque
import random
import globals as G
from world import Model
from utils import *
from player import Player
import inventory


class Window(pyglet.window.Window):

    def push(self,pos,rot): glPushMatrix(); glRotatef(-rot[0],1,0,0); glRotatef(-rot[1],0,1,0); glTranslatef(-pos[0],-pos[1],-pos[2],)
    def Projection(self): glMatrixMode(GL_PROJECTION); glLoadIdentity()
    def Model(self): glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    def set2d(self): self.Projection(); gluOrtho2D(0,self.width,0,self.height); self.Model()
    def set3d(self): self.Projection(); gluPerspective(70,self.width/self.height,0.05,1000); self.Model()

    def setLock(self,state): self.lock = state; self.set_exclusive_mouse(state)
    lock = False; mouse_lock = property(lambda self:self.lock,setLock)
    inventory = [G.DIRT, G.GRASS, G.STONE, G.COBBLESTONE, G.BEDROCK, G.IRONORE, G.COALORE, G.REDSTONEORE, G.DIAMONDORE]
    block = inventory[0]
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.set_minimum_size(500, 500)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule(self.update)
        self.reticle = None
        self.model = Model()
        self.player = Player(self.model, (0,100,0),(-30,0))
        self.inventorylabel = pyglet.text.Label('Dirt',
                          font_name='Arial',
                          font_size=18,
                          x=self.width, y=self.height,
                          anchor_x='right', anchor_y='top')
        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9, key._0]
        pyglet.clock.schedule(self.model.update)
        self.hotbar = inventory.Hotbar(self.width, self.height)
        
    def on_mouse_motion(self,x,y,dx,dy):
        if self.mouse_lock: self.player.mouse_motion(dx,dy)

    def on_key_press(self,KEY,MOD):
        if KEY == key.ESCAPE: self.mouse_lock = False
        elif KEY == key.F: self.player.flying = not self.player.flying; self.player.dy = 0
        elif KEY == key.C: self.player.noclip = not self.player.noclip
        elif KEY in self.num_keys:
            index = (KEY - self.num_keys[0]) % len(self.inventory)
            self.block = self.inventory[index]
        
    
    def on_mouse_press(self,x,y,button,MOD):
        if self.mouse_lock:
            if button == mouse.LEFT:
                block = self.model.hit_test(self.player.pos,self.player.get_sight_vector())[0]
                if block:
                    self.model.remove_block(block, player=True)
            elif button == mouse.RIGHT:
                block = self.model.hit_test(self.player.pos,self.player.get_sight_vector())[1]
                if block: self.model.add_block(block,self.block, player=True)
        else:
            self.mouse_lock = True
    def updatesector(self, dt):
        sector = sectorize(self.player.pos)
        if sector != self.player.sector:
            self.model.change_sectors(self.player.sector, sector)
            self.player.sector = sector
    
    def update(self,dt):
        self.player.update(dt,self.keys)
        self.updatesector(dt)
        self.inventorylabel.text = self.block.name

    def on_draw(self):
        self.clear()
        self.set3d()
        self.push(self.player.pos,self.player.rot)
        block = self.model.hit_test(self.player.pos,self.player.get_sight_vector())[0]
        if block:
            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE); glColor3d(0,0,0)
            pyglet.graphics.draw(24,GL_QUADS,('v3f/static',flatten(cube_vertices(block,0.53))))
            glPolygonMode(GL_FRONT_AND_BACK,GL_FILL); glColor3d(1,1,1)
        self.model.draw()
        glPopMatrix()
        self.set2d()
        self.inventorylabel.draw()
        self.hotbar.batch.draw()
        self.reticle.draw(GL_LINES)
        
    
    def on_resize(self, width, height):
        if self.reticle:
            self.reticle.delete()
        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n)), ('c3B', ((255, 255, 255)*4))
        )
        self.inventorylabel.x = self.width
        self.inventorylabel.y = self.height
        if self.hotbar.vlist:
            self.hotbar.remove()
        self.hotbar.x = (self.width//2)-181
        self.hotbar.add()
        super(Window, self).on_resize(width, height)
        
def vec(*args):
    return (GLfloat * len(args))(*args)

if __name__ == '__main__':
    window = Window(width=854,height=480,caption='Minecraft',resizable=True)
    light0pos = [20.0,   20.0, 20.0, 1.0]
    glClearColor(0.5,0.7,1,1)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL); glAlphaFunc(GL_GEQUAL,1)
    glEnable(GL_CULL_FACE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_COMBINE)
    glTexEnvf(GL_TEXTURE_ENV, GL_COMBINE_RGB, GL_ADD_SIGNED)
    pyglet.app.run()



