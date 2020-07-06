from collections import defaultdict, deque
import pyglet
from terrain import *
import globals as G
from utils import *
import noise


class Model:
    world, collidable, shown, _shown, sectors_shown, sectors = defaultdict(),defaultdict(),defaultdict(), defaultdict(), dict(), defaultdict(list)
    batch = pyglet.graphics.Batch()
    seed = 3295784719208478
    perlin = Perlin(seed)
    caves = Caves3D(seed)
    showhide_queue,playeractions_queue, genqueue = deque(), deque(), deque()
    def __init__(self):
        self.gen_terrain()
    
    def enqueue(self, queue, func, *args):
        queue.append((func, args))
    
    def dequeue(self, queue):
        return queue.popleft()
    
    def gen_terrain(self):
        for x in range(0, 3):
            for z in range(0, 3):
                self.gen_sector((x, z))
                
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
        y = int(self.perlin(x, z)*64+64)
        self.add_block((x, y, z), G.GRASS)
        for yy in range(y-10, y):
            yn = self.caves(x, yy, z)
            if yn >0.5:
                self.add_block((x, yy, z), G.DIRT)
        for yy in range(1, y-10):
            yn = self.caves(x, yy, z)
            if yn >0.5:
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
        self.sectors[sectorize(pos)].append(pos)
        self.show_block(pos, player)
        self.world[pos] = block
        
    
    def remove_block(self, pos, player=False):
        if not pos in self.world:
            return
        self.sectors[sectorize(pos)].remove(pos)
        self.hide_block(pos, player)
        del self.world[pos]
    
    def show_block(self, pos, player=False):
        if not player:
            self.enqueue(self.showhide_queue, self._show_block, pos)
        else:
            self.enqueue(self.playeractions_queue, self._show_block, pos)
            
    def hide_block(self, pos, player=False):
        if not player:
            self.enqueue(self.showhide_queue, self._hide_block,pos)
        else:
            self.enqueue(self.playeractions_queue, self._hide_block, pos)
    
    def _show_block(self, pos):
        if pos in self.shown:
            return
        if not pos in self.world:
            return
        
        self.shown[pos] = block = self.world[pos]
        self._shown[pos] = block.draw(pos, self.batch)
    
    def _hide_block(self, pos):
        if not pos in self.shown:
            return
        for lst in self._shown[pos]:
            lst.delete()
        del self._shown[pos]
        del self.shown[pos]
    
    def update(self):
        if self.showhide_queue:
            for _ in range(300):
                if self.showhide_queue:
                    func, args = self.dequeue(self.showhide_queue)
                    func(*args)
        if self.playeractions_queue:
            func, args = self.dequeue(self.playeractions_queue)
            func(*args)
        if self.genqueue:
            for _ in range(50):
                if self.genqueue:
                    func, args = self.dequeue(self.genqueue)
                    func(*args)
    
    def process_whole_queue(self):
        for _ in range(0, G.SECTOR_SIDE**2):
            func, args = self.dequeue(self.genqueue)
            func(*args)
        print('Finished generation queue')
        
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
    
    def change_sectors(self, after):
        new_sectors_shown = dict()
        pad = G.VISIBLE_SECTORS_RADIUS
        x, y, z = after
        for distance in range(0, pad + 1):
            for dx in range(-distance, distance + 1):
                for dz in range(-distance, distance + 1):
                    if abs(dx) != distance and abs(dz) != distance:
                        continue
                    for dy in range(-4, 4):
                        if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                            continue
                        new_sectors_shown[(x + dx, y + dy, z + dz)] = True
        #Queue the sectors to be shown, instead of rendering them in real time
        for sector in new_sectors_shown.keys():
            if sector not in self.sectors_shown:
                if sector not in self.sectors:
                    self.gen_sector(sector)
                self.show_sector(sector)
        self.sectors_shown = new_sectors_shown
    
    def hide_sectors(self, dt, player):
        #TODO: This is pretty laggy, I feel an FPS drop once a second while sector changing because of this
        deload = G.DELOAD_SECTORS_RADIUS
        plysector = sectorize(player.position)
        if player.last_sector != plysector:
            px, py, pz = plysector
            for sector in self.sectors:
                x,y,z = sector
                if abs(px-x) > deload or abs(py-y) > deload or abs(pz-z) > deload:
                    self.hide_sector(sector)
    
    
