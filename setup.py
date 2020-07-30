from setuptools import setup
from Cython.Build import cythonize

setup(
    name='Minecraft in Python',
    ext_modules=cythonize("mc/terrain.py", compiler_directives={'language_level' : "3"}),
    zip_safe=False,
) 
