# Minecraft 
This is a minecraft-clone


~~NOTE: I have stopped development on this project. I will be working with c++~~

## Running
### This requires Python 3.
Install pipenv from pip or your Linux distribution's package manager:
```
pip install pipenv
```
Arch Linux:
```
pacman -S python-pipenv
```

Then run pipenv in the source directory(be sure to insert your Python version):
```
pipenv --python <insert python version here>
pipenv update
pipenv shell
```

Finally, run Python:
```
python main.py
```

The next time you want to start the game, run:
```
pipenv shell
python main.py
```
or:
```
pipenv run python main.py
```
