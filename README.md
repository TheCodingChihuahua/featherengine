# Feather Engine!
Feather is a small Pygame utility module for beginner-friendly 2D games. Created by TheCodingChihuahua.

## Example
```python
import feather

player = None

def init():
    global player
    player = feather.Sprite("assets/player.png")

def update():
    if feather.key_pressed("ENTER"):
        player.image = "assets/playerdance.png"
    if feather.key_pressed("BACKSPACE"):
        player.image = "assets/playercry.png"
    if feather.key_pressed("ESCAPE"):
        feather.end()

feather.run(init, update)
```

`update` runs once per frame at up to 60 frames per second. Image paths are resolved relative to the game's current working directory.

## Installation
```powershell
python -m pip install feather-engine
```

Then import it in your game with:
```python
import feather
```
Special thanks to Hack Club! They didn't support this project, but they're awesome anyhow. [Visit the Hack Club website](www.hackclub.com)
