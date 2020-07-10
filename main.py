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
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.set_minimum_size(500, 500)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule(self.update)
        self.reticle = None
        self.model = Model()
        self.player = Player(self.model, (0,int(self.model.perlin(0, 0)*40+32)+2,0),(-30,0))
        pyglet.clock.schedule(self.model.update)
        self.hotbar = inventory.Hotbar(self.width, self.height)
        self.inv = inventory.Inventory(self.width, self.height)
        self.ininv = False
        self.last_ininv = False
        self.invindex = 0
        self.block = self.inventory[self.invindex]
        self.inventorylabel = pyglet.text.Label('Dirt',
                  font_name='Arial',
                  font_size=18,
                  x=self.width, y=self.height,
                  anchor_x='right', anchor_y='top')
    
    @property
    def current_index(self):
        return int(self.invindex)

    @current_index.setter
    def current_index(self, value):
        self.invindex = value % len(self.inventory)
    
    
    def on_mouse_motion(self,x,y,dx,dy):
        if self.mouse_lock: self.player.mouse_motion(dx,dy)

    def on_key_press(self,KEY,MOD):
        if KEY == key.ESCAPE: 
            self.mouse_lock = False
            if self.ininv:
                self.ininv = False; self.mouse_lock = True
        elif KEY == key.F: self.player.flying = not self.player.flying; self.player.dy = 0
        elif KEY == key.C: self.player.noclip = not self.player.noclip
        elif KEY == key.E:
            self.ininv = not self.ininv
            if self.last_ininv:
                self.mouse_lock = True
            self.last_ininv = not self.last_ininv
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.current_index -= -scroll_y
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
            if not self.ininv:
                self.mouse_lock = True
    def updatesector(self, dt):
        sector = sectorize(self.player.pos)
        if sector != self.player.sector:
            self.model.change_sectors(self.player.sector, sector)
            if self.player.sector == None:
                self.model.show_all_queued_blocks()
            self.player.sector = sector
    
    def update(self,dt):
        if not self.ininv:
            self.player.update(dt,self.keys)
        self.updatesector(dt)
        if self.ininv: self.mouse_lock = False
        self.block = self.inventory[self.invindex]
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
        if self.ininv:
            self.inv.batch.draw()
    
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
        if self.inv.vlist:
            self.inv.remove()
        self.inv.x, self.inv.y = (self.width//2)-130, (self.height//2)-110
        self.inv.add()
        super(Window, self).on_resize(width, height)
        
def vec(*args):
    return (GLfloat * len(args))(*args)
def setup_fog():
    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    glHint(GL_FOG_HINT, GL_FASTEST)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_START, 20.0)
    glFogf(GL_FOG_END, 60.0)

if __name__ == '__main__':
    window = Window(width=854,height=480,caption='Minecraft',resizable=True)
    glClearColor(0.5,0.7,1,1)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL); glAlphaFunc(GL_GEQUAL,1)
    #glEnable(GL_CULL_FACE)
    glEnable(GL_BLEND)
    glEnable(GL_FOG)
    glHint(GL_FOG_HINT,GL_DONT_CARE)
    glFogi(GL_FOG_MODE,GL_EXP)
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(1.0, 1.0, 1.0, 0.01))
    glFogfv(GL_FOG_DENSITY, (GLfloat)(0.003))
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_COMBINE)
    glTexEnvf(GL_TEXTURE_ENV, GL_COMBINE_RGB, GL_ADD_SIGNED)
    setup_fog()
    pyglet.app.run()



