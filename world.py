from collections import defaultdict, deque
import pyglet
from terrain import *
import globals as G
from utils import *
import noise


class Model:
    world, shown, _shown, sectors = defaultdict(),defaultdict(), defaultdict(), defaultdict(list)
    batch = pyglet.graphics.Batch()
    #the well-known repeating seed in minecraft
    seed = 107038380838084
    perlin = Perlin(seed)
    caves = Caves3D(seed)
    showhide_queue,playeractions_queue, genqueue = deque(), deque(), deque()
    def __init__(self):
        self.gen_sector((0, 0))
    
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
        y = int(self.perlin(x, z)*40+32)
        yn = self.caves(x, y, z)
        if yn >0.4:
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
    
    def show_all_queued_blocks(self):
        max_blocks = len(self.genqueue)
        i = 0
        lastpercent = 0
        print('Processing generation queue')
        print('0 % ')
        for i in range(max_blocks):
            if self.genqueue:
                func, args = self.dequeue(self.genqueue)
                func(*args)
                i+= 1
                percent = int((i/max_blocks)*100)
                if lastpercent != percent:
                    delete_last_line()
                    print(percent, '%')
                lastpercent = percent
        max_blocks = len(self.showhide_queue)
        i = 0
        print('Processing show and hide queue')
        print('0 %')
        lastpercent = 0
        while self.showhide_queue:
            func, args = self.dequeue(self.showhide_queue)
            func(*args)
            i+= 1
            percent = int((i/max_blocks)*100)
            if percent != lastpercent:
                delete_last_line()
                print(percent, '%')
            lastpercent = percent
    
    def add_block(self, pos, block, player=False):
        if pos in self.world:
            return
        self.show_block(pos, player)
        self.sectors[sectorize(pos)].append(pos)
        self.world[pos] = block
        
    
    def remove_block(self, pos, player=False):
        if not pos in self.world:
            return
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
    
    
    def update(self, dt):
        if self.genqueue:
            for _ in range(40):
                if self.genqueue:
                    func, args = self.dequeue(self.genqueue)
                    func(*args)
        if self.showhide_queue:
            for _ in range(175):
                if self.showhide_queue:
                    func, args = self.dequeue(self.showhide_queue)
                    func(*args)
        if self.playeractions_queue:
            for _ in range(10):
                if self.playeractions_queue:
                    func, args = self.dequeue(self.playeractions_queue)
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
    
    
