from collections import defaultdict, deque
import pyglet
from terrain import *
import globals as G
from utils import *
import noise


class Model:
    world, collidable, shown, _shown = defaultdict(),defaultdict(),defaultdict(),defaultdict()
    batch = pyglet.graphics.Batch()
    perlin = Perlin()
    caves =Caves3D()
    showhide_queue = deque()
    playeractions_queue = deque()
    genqueue = deque()

    def __init__(self):
        self.gen_terrain()
    
    def enqueue(self, queue, func, *args):
        queue.append((func, args))
    
    def dequeue(self, queue):
        return queue.popleft()
    
    def gen_terrain(self):
        for x in range(-3, 3):
            for z in range(-3, 3):
                self.gen_sector((x, z))
                
    def gen_sector(self, pos):
        for x in range(pos[0]*G.SECTOR_SIDE, (pos[0]*G.SECTOR_SIDE)+G.SECTOR_SIDE+1):
            for z in range(pos[1]*G.SECTOR_SIDE, (pos[1]*G.SECTOR_SIDE)+G.SECTOR_SIDE+1):
                self.enqueue(self.genqueue, self.gen_block, (pos[0]+x, pos[1]+z))
    
    def gen_block(self, pos):
        x, z = pos
        y = int(self.perlin(x, z)*64+64)
        self.add_block((x, y, z), G.GRASS)
        for yy in range(y-10, y):
            yn = self.caves(x, yy, z)
            if yn >0.4:
                self.add_block((x, yy, z), G.DIRT)
        for yy in range(1, y-10):
            yn = self.caves(x, yy, z)
            if yn >0.4:
                self.add_block((x, yy, z), G.STONE)
        self.add_block((x, 0, z), G.BEDROCK)
        
    def gen_caveblock(self, pos, invert=True):
        '''Debug function to visualize caves
        '''
        x, z = pos
        y = 60
        for yy in range(1, y):
            yn = self.caves(x, yy, z)
            if invert:
                if yn <0.4:
                    self.add_block((x, yy, z), G.STONE)
            else:
                if yn >0.4:
                    self.add_block((x, yy, z), G.STONE)
        self.add_block((x, 0, z), G.BEDROCK)
    
    
    def add_block(self, pos, block, player=False):
        if pos in self.world:
            return
        self.world[pos] = block
        if not player:
            self.enqueue(self.showhide_queue, self.show_block, pos)
        else:
            self.enqueue(self.playeractions_queue, self.show_block, pos)
    
    def remove_block(self, pos, player=False):
        if not pos in self.world:
            return
        if not player:
            self.enqueue(self.showhide_queue, self.hide_block,pos)
        else:
            self.enqueue(self.playeractions_queue, self.hide_block, pos)
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
    
    def update(self):
        if self.showhide_queue:
            for _ in range(100):
                if self.showhide_queue:
                    func, args = self.dequeue(self.showhide_queue)
                    func(*args)
        if self.playeractions_queue:
            for _ in range(5):
                if self.playeractions_queue:
                    func, args = self.dequeue(self.playeractions_queue)
                    func(*args)
        if self.genqueue:
            for _ in range(3):
                if self.genqueue:
                    func, args = self.dequeue(self.genqueue)
                    func(*args)
    
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
    
    
