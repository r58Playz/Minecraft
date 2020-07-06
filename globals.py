import blocks
import pyglet
import os

APP_NAME = "Minecraft: Python Edition"
SETTINGS_PATH = pyglet.resource.get_settings_path(APP_NAME)
path_to_create = os.path.join(SETTINGS_PATH, 'resource-packs', 'default')
os.makedirs(path_to_create, exist_ok=True)

from zipfile import ZipFile
from urllib.request import urlopen

from io import BytesIO

zip_url = 'https://www.dropbox.com/s/vymkmzr1fsemo53/resource%2Bpack%2Btemplate%2B%28sound%291.15.x%2Bv1.0.zip?dl=1'
if os.listdir(path_to_create) == []:
    with urlopen(zip_url) as f:
        with BytesIO(f.read()) as b, ZipFile(b) as zipfle:
            zipfle.extractall(path=os.path.join(SETTINGS_PATH, 'resource-packs', 'default'))


VISIBLE_SECTORS_RADIUS = 2

RESOURCE_LOADER = pyglet.resource.Loader(path=[os.path.join(SETTINGS_PATH, 'resource-packs', 'default','assets', 'minecraft'), os.path.join(SETTINGS_PATH, 'resource-packs', 'default', 'assets', 'minecraft', 'textures', 'block')])

FACES = ((-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1))
SECTOR_SIDE = 15
GRASS = blocks.GrassBlock()
DIRT  = blocks.DirtBlock() 
STONE = blocks.StoneBlock()
BEDROCK = blocks.Bedrock()
COBBLESTONE = blocks.CobblestoneBlock()
IRONORE = blocks.IronOre()
COALORE = blocks.CoalOre()
REDSTONEORE = blocks.RedstoneOre()
DIAMONDORE = blocks.DiamondOre()
