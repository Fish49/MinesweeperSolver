import pynput
from PIL import Image, ImageGrab
import keyboard

profile={
    "originPoint":[0, 0],
    "boardWidth":0,
    "boardHeight":0,
    "squareSize":0,
    "cOne":[25, 118, 210],
    "cTwo":[56, 142, 60],
    "cThree":[211, 47, 47],
    "cFour":[123, 31, 162],
    "cFive":[255, 143, 0],
    "cSix":[0, 151, 167],
    "cSeven":[109, 100, 91],
    "cGreen":[170, 215, 81],
    "cFlag":[242, 54, 7],
    "defaultOffset":[16, -21],
    "blueSpace":[850, 500],
    "minSimilarity":10
}

def whenKeyboardPress(KEY):
    print(KEY)

mouse=pynput.mouse.Controller()
keyboard.on_press()