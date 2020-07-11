import mc.blocks as blocks
import pyglet
import os

SECTOR_SIZE = 15
APP_NAME = "Minecraft: Python Edition"
SETTINGS_PATH = pyglet.resource.get_settings_path(APP_NAME)
path_to_create = os.path.join(SETTINGS_PATH, 'resource-packs', 'default')
os.makedirs(path_to_create, exist_ok=True)
os.makedirs(os.path.join(SETTINGS_PATH, 'resource-packs', 'default', 'panorama'), exist_ok=True)

from zipfile import ZipFile
from urllib.request import urlopen

from io import BytesIO

zip_url = 'https://www.dropbox.com/s/vymkmzr1fsemo53/resource%2Bpack%2Btemplate%2B%28sound%291.15.x%2Bv1.0.zip?dl=1'
if 'assets' not in os.listdir(path_to_create):
    with urlopen(zip_url) as f:
        with BytesIO(f.read()) as b, ZipFile(b) as zipfle:
            zipfle.extractall(path=os.path.join(SETTINGS_PATH, 'resource-packs', 'default'))
if 'panorama' not in os.listdir(path_to_create):
    with urlopen('https://www.dropbox.com/s/t8v15627e90bkt9/background.zip?dl=1') as f:
        with BytesIO(f.read()) as b, ZipFile(b) as zipfle:
            zipfle.extractall(path=os.path.join(SETTINGS_PATH, 'resource-packs', 'default', 'panorama'))




RESOURCE_LOADER = pyglet.resource.Loader(path=[os.path.join(SETTINGS_PATH, 'resource-packs', 'default','assets', 'minecraft'), os.path.join(SETTINGS_PATH, 'resource-packs', 'default', 'assets', 'minecraft', 'textures', 'block')])

PANORAMA_LOADER = pyglet.resource.Loader(path=[os.path.join(SETTINGS_PATH, 'resource-packs', 'default', 'panorama')])

FACES = ((-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1))
SECTOR_SIDE = 15
SECTOR_PAD = 2
GRASS = blocks.GrassBlock()
DIRT  = blocks.DirtBlock() 
STONE = blocks.StoneBlock()
BEDROCK = blocks.Bedrock()
COBBLESTONE = blocks.CobblestoneBlock()
IRONORE = blocks.IronOre()
COALORE = blocks.CoalOre()
REDSTONEORE = blocks.RedstoneOre()
DIAMONDORE = blocks.DiamondOre()
