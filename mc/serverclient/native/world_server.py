from collections import defaultdict, deque
import pyglet
from mc.terrain import *
import mc.globals as G
from mc.utils_py import *
import noise
def sectorize(position):
    x, y, z = normalize(position)
    x, y, z = x // G.SECTOR_SIZE+1, y // G.SECTOR_SIZE+1, z // G. SECTOR_SIZE+1
    return (x, 0, z)


class WorldServer:
    world, sectors = defaultdict(), defaultdict(list)
    batch = pyglet.graphics.Batch()
    #the well-known repeating seed in minecraft
    seed = 107038380838084
    perlin = Perlin(seed)
    caves = Caves3D(seed)
    genqueue = deque()
    def __init__(self, server):
        self.gen_sector((0, 0))
        self.server = server
    
    def enqueue(self, queue, func, *args):
        queue.append((func, args))
    
    def dequeue(self, queue):
        return queue.popleft()
                
    def gen_sector(self, pos):
        for x in range(pos[0]*G.SECTOR_SIDE, (pos[0]*G.SECTOR_SIDE)+G.SECTOR_SIDE+1):
            for z in range(pos[1]*G.SECTOR_SIDE, (pos[1]*G.SECTOR_SIDE)+G.SECTOR_SIDE+1):
                self.enqueue(self.genqueue, self.gen_block, (pos[0]+x, pos[1]+z))
    
    def show_sector(self, sector):
        if sector not in self.sectors:
            return
        for block in self.sectors[sector]:
            self.show_block(block)
    def hide_sector(self, sector):
        if sector not in self.sectors:
            return
        for block in self.sectors[sector]:
            self.hide_block(block)
            
    def gen_block(self, pos):
        x, z = pos
        y = int(self.perlin(x, z ,0)*40+32)
        yn = self.caves(x, y, z)
        if yn >0.2:
            self.add_block((x, y, z), G.GRASS)
        for yy in range(y-10, y):
            yn = self.caves(x, yy, z)
            if yn >0.2:
                self.add_block((x, yy, z), G.DIRT)
        for yy in range(1, y-10):
            yn = self.caves(x, yy, z)
            if yn >0.2:
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
    def add_block(self, pos, block):
        if pos in self.world:
            return
        self.sectors[sectorize(pos)].append(pos)
        self.world[pos] = block
        
    
    def remove_block(self, pos):
        if not pos in self.world:
            return
        del self.world[pos]
    
    def check_neighbors(self, position):
        x, y, z = position
        for dx, dy, dz in G.FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            if self.exposed(key):
                if key not in self.shown:
                    self.show_block(key)
            else:
                if key in self.shown:
                    self.hide_block(key)

    
    def update(self):
        if self.genqueue:
            for _ in range(400):
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
    
    def change_sectors(self, before, after):
        before_set = set()
        after_set = set()
        pad = G.SECTOR_PAD
        for dx in range(-pad, pad + 1):
            for dy in [0]:  # xrange(-pad, pad + 1):
                for dz in range(-pad, pad + 1):
                    if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                        continue
                    if before:
                        x, y, z = before
                        before_set.add((x + dx, z + dz, y + dy))
                    if after:
                        x, y, z = after
                        after_set.add((x + dx, z + dz, y + dy))
        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            if sector not in self.sectors:
                self.gen_sector(sector)
            self.show_sector(sector)
        for sector in hide:
            if sector not in self.sectors:
                self.gen_sector(sector)
            self.hide_sector(sector)
        self.gen_sector_lazy(after)
    def gen_sector_lazy(self, current_sector):
        pad = G.SECTOR_PAD+1
        x, y, z = current_sector
        for dx in range(-pad, pad+1):
            for dz in range(-pad, pad+1):
                dy = 0
                sector = (dx+x, dy+y, dz+z)
                if sector not in self.sectors:
                    self.gen_sector(sector)
    def exposed(self, pos):
        x, y, z = pos
        for dx, dy, dz in G.FACES:
            if (x+dx, y+dy, z+dz) not in self.world:
                return True
        return False
 
