from pyglet.gl import *
from pyglet.window import key, mouse
import math
from collections import defaultdict
import random
import globals as G
import noise

def normalize(pos): 
    x,y,z = pos
    return round(x),round(y),round(z)
def flatten(lst): 
    return sum(map(list,lst),[])
def cube_vertices(pos,n=0.5):
    x,y,z = pos
    v = tuple((x+X,y+Y,z+Z) for X in (-n,n) for Y in (-n,n) for Z in (-n,n))
    return tuple(tuple(k for j in i for k in v[j]) for i in ((0,1,3,2),(5,4,6,7),(0,4,5,1),(3,7,6,2),(4,0,2,6),(1,5,7,3)))

class Perlin:
    def __call__(self,x,y): return (self.noise(x*self.f,y*self.f)+1)/2
    def __init__(self,seed=None):
        self.f = 15/512; self.m = 65535; p = list(range(self.m))
        if seed: random.seed(seed)
        random.shuffle(p); self.p = p+p

    def fade(self,t): return t*t*t*(t*(t*6-15)+10)
    def lerp(self,t,a,b): return a+t*(b-a)
    def grad(self,hash,x,y,z):
        h = hash&15; u = y if h&8 else x
        v = (x if h==12 or h==14 else z) if h&12 else y
        return (u if h&1 else -u)+(v if h&2 else -v)

    def noise(self,x,y,z=0):
        p,fade,lerp,grad = self.p,self.fade,self.lerp,self.grad
        xf,yf,zf = math.floor(x),math.floor(y),math.floor(z)
        X,Y,Z = xf%self.m,yf%self.m,zf%self.m
        x-=xf; y-=yf; z-=zf
        u,v,w = fade(x),fade(y),fade(z)
        A = p[X  ]+Y; AA = p[A]+Z; AB = p[A+1]+Z
        B = p[X+1]+Y; BA = p[B]+Z; BB = p[B+1]+Z
        return lerp(w,lerp(v,lerp(u,grad(p[AA],x,y,z),grad(p[BA],x-1,y,z)),lerp(u,grad(p[AB],x,y-1,z),grad(p[BB],x-1,y-1,z))),
                      lerp(v,lerp(u,grad(p[AA+1],x,y,z-1),grad(p[BA+1],x-1,y,z-1)),lerp(u,grad(p[AB+1],x,y-1,z-1),grad(p[BB+1],x-1,y-1,z-1))))

class Model:
    world, collidable, shown, _shown = defaultdict(),defaultdict(),defaultdict(),defaultdict()

    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.perlin = Perlin()
        self.gen_terrain()
        
    def gen_terrain(self):
        for x in range(-10, 10):
            for z in range(-10, 10):
                y = int(self.perlin(x, z)*40+50)
                self.add_block((x, y, z), G.GRASS)
                for yy in range(1, y):
                    self.add_block((x, yy, z), G.DIRT)
                    self.show_block((x, yy, z))
                self.show_block((x, y, z))
    def add_block(self, pos, block):
        if pos in self.world:
            return
        self.world[pos] = block
    
    def remove_block(self, pos):
        if not pos in self.world:
            return
        self.hide_block(pos)
        del self.world[pos]
    
    def show_block(self, pos):
        if pos in self.shown:
            return
        if not pos in self.world:
            return
        
        self.shown[pos] = block = self.world[pos]
        if block.collidable:
            self.collidable[pos] = block
        self._shown[pos] = block.draw(pos, self.batch)
    
    def hide_block(self, pos):
        if not pos in self.shown:
            return
        if self.shown[pos].collidable:
            del self.collidable[pos]
        for lst in self._shown[pos]:
            lst.delete()
        del self._shown[pos]
        del self.shown[pos]

    def draw(self):
        self.batch.draw()
    def hit_test(self,position,vector,max_distance=8):
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in range(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and key in self.shown:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None



class Player:
    WALKING_SPEED = 5
    FLYING_SPEED = 15

    GRAVITY = 20
    JUMP_SPEED = (2*GRAVITY)**.5
    TERMINAL_VELOCITY = 50
    flying, noclip = False, False
    dy = 0
    
    def __init__(self,model, pos=(0,0,0),rot=(0,0)):
        self.pos = list(pos)
        self.rot = list(rot)
        self.model = model

    def mouse_motion(self,dx,dy):
        dx/=8; dy/=8; self.rot[0]+=dy; self.rot[1]-=dx
        if self.rot[0]>90: self.rot[0] = 90
        elif self.rot[0]<-90: self.rot[0] = -90
    
    def jump(self):
        if not self.dy: self.dy = self.JUMP_SPEED
    
    def get_sight_vector(self):
        rotX,rotY = self.rot[0]/180*math.pi,-self.rot[1]/180*math.pi
        dx,dz = math.sin(rotY),-math.cos(rotY)
        dy,m = math.sin(rotX),math.cos(rotX)
        return dx*m,dy,dz*m

    def update(self,dt,keys):
        DX,DY,DZ = 0,0,0; s = dt*self.FLYING_SPEED if self.flying else dt*self.WALKING_SPEED
        rotY = self.rot[1]/180*math.pi
        dx,dz = s*-math.sin(rotY),s*math.cos(rotY)
        if self.flying:
            if keys[key.LSHIFT]: DY-=s
            if keys[key.SPACE]: DY+=s
        elif keys[key.SPACE]: self.jump()
        if keys[key.W]: DX+=dx; DZ-=dz
        if keys[key.S]: DX-=dx; DZ+=dz
        if keys[key.A]: DX-=dz; DZ-=dx
        if keys[key.D]: DX+=dz; DZ+=dx

        if dt<0.2:
            dt/=10; DX/=10; DY/=10; DZ/=10
            for i in range(10): self.move(dt,DX,DY,DZ)

    def move(self,dt,dx,dy,dz):
        if not self.flying:
            self.dy -= dt*self.GRAVITY
            self.dy = max(self.dy,-self.TERMINAL_VELOCITY)
            dy += self.dy*dt

        x,y,z = self.pos
        self.pos = self.collide((x+dx,y+dy,z+dz))

    def collide(self,pos):
        if self.noclip and self.flying: return pos
        pad = 0.25; p = list(pos); np = normalize(pos)
        for face in ((-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)):
            for i in (0,1,2):
                if not face[i]: continue
                d = (p[i]-np[i])*face[i]
                if d<pad: continue
                for dy in (0,1):
                    op = list(np); op[1]-=dy; op[i]+=face[i]
                    if tuple(op) in self.model.collidable:
                        p[i]-=(d-pad)*face[i]
                        if face[1]: self.dy = 0
                        break
        return p

class Window(pyglet.window.Window):

    def push(self,pos,rot): glPushMatrix(); glRotatef(-rot[0],1,0,0); glRotatef(-rot[1],0,1,0); glTranslatef(-pos[0],-pos[1],-pos[2],)
    def Projection(self): glMatrixMode(GL_PROJECTION); glLoadIdentity()
    def Model(self): glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    def set2d(self): self.Projection(); gluOrtho2D(0,self.width,0,self.height); self.Model()
    def set3d(self): self.Projection(); gluPerspective(70,self.width/self.height,0.05,1000); self.Model()

    def setLock(self,state): self.lock = state; self.set_exclusive_mouse(state)
    lock = False; mouse_lock = property(lambda self:self.lock,setLock)

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.set_minimum_size(300,200)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule(self.update)
        self.reticle = None
        self.model = Model()
        self.player = Player(self.model, (0,100,0),(-30,0))

    def on_mouse_motion(self,x,y,dx,dy):
        if self.mouse_lock: self.player.mouse_motion(dx,dy)

    def on_key_press(self,KEY,MOD):
        if KEY == key.ESCAPE: self.close()
        elif KEY == key.E: self.mouse_lock = not self.mouse_lock
        elif KEY == key.F: self.player.flying = not self.player.flying; self.player.dy = 0
        elif KEY == key.C: self.player.noclip = not self.player.noclip
    
    def on_mouse_press(self,x,y,button,MOD):
        if button == mouse.LEFT:
            block = self.model.hit_test(self.player.pos,self.player.get_sight_vector())[0]
            if block:
                if self.keys[key.LSHIFT]:
                    self.model.hide_block(block)
                else:
                    self.model.remove_block(block)
        elif button == mouse.RIGHT:
            block = self.model.hit_test(self.player.pos,self.player.get_sight_vector())[1]
            if block: self.model.add_block(block,G.DIRT), self.model.show_block(block)
    
    def update(self,dt):
        self.player.update(dt,self.keys)

    def on_draw(self):
        self.clear()
        self.set3d()
        self.push(self.player.pos,self.player.rot)
        block = self.model.hit_test(self.player.pos,self.player.get_sight_vector())[0]
        if block:
            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE); glColor3d(0,0,0)
            pyglet.graphics.draw(24,GL_QUADS,('v3f/static',flatten(cube_vertices(block,0.52))))
            glPolygonMode(GL_FRONT_AND_BACK,GL_FILL); glColor3d(1,1,1)
        self.model.draw()
        glPopMatrix()
        self.set2d()
        self.reticle.draw(GL_LINES)
        
    
    def on_resize(self, width, height):
        if self.reticle:
            self.reticle.delete()
        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n)), ('c3B', ((255, 255, 255)*4))
        )
        


if __name__ == '__main__':
    window = Window(width=854,height=480,caption='Minecraft',resizable=True)
    glClearColor(0.5,0.7,1,1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_COMBINE)
    glTexEnvf(GL_TEXTURE_ENV, GL_COMBINE_RGB, GL_ADD_SIGNED)
    pyglet.app.run()



