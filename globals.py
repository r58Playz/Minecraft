import blocks
import pyglet
import os

APP_NAME = "Minecraft: Python Edition"
SETTINGS_PATH = pyglet.resource.get_settings_path(APP_NAME)
path_to_create = os.path.join(SETTINGS_PATH, 'resource-packs', 'default')
os.makedirs(path_to_create, exist_ok=True)

from zipfile import ZipFile

# Download zip from https://www.curseforge.com/minecraft/texture-packs/minecraft-resource-pack-template/download/2846023/file and rename to Resources.zip and place in directory
if os.listdir(path_to_create) == []:
    zipfle = ZipFile('Resources.zip')
    zipfle.extractall(path=os.path.join(SETTINGS_PATH, 'resource-packs', 'default'))

RESOURCE_LOADER = pyglet.resource.Loader(path=[os.path.join(SETTINGS_PATH, 'resource-packs', 'default','assets', 'minecraft'), os.path.join(SETTINGS_PATH, 'resource-packs', 'default', 'assets', 'minecraft', 'textures', 'block')])

GRASS = blocks.GrassBlock()
DIRT  = blocks.DirtBlock() 
STONE = blocks.StoneBlock()
BEDROCK = blocks.Bedrock()
COBBLESTONE = blocks.CobblestoneBlock()
