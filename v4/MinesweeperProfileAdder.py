import pynput
from PIL import Image, ImageGrab
import keyboard
import json

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

mouse = pynput.mouse.Controller()

def focus():
    print('click on your minesweeper window to bring it into focus. make sure that you are able to see the vscode window the entire time')
    print('when youre minesweeper window is focused, click C to start the process.')
    while True:
        event = keyboard.read_event()
        if event.name == 'c':
            break

def getOriginPoint():
    global profile

    print('\nUse the wasd keys to navigate to the bottom-left corner of the top-left square on youre board. hit enter when youre done')

    while True:
        event = keyboard.read_event()
        mousePos = list(mouse.position)

        if event.event_type == 'up':
            continue
        if event.name == 'enter':
            break

        if event.name == 'w':
            mousePos[1]-=1
        if event.name == 's':
            mousePos[1]+=1
        if event.name == 'a':
            mousePos[0]-=1
        if event.name == 'd':
            mousePos[0]+=1
        mouse.position = mousePos

    profile['originPoint']=mousePos

def getSquareSize():
    global profile
    mouse.position=profile['originPoint']

    print('\nUse the d key to move the mouse cursor to the leftmost pixel of the square to the right. hit enter when youre done')
    print('if you accidentally move your mouse, hit R')

    while True:
        event = keyboard.read_event()
        mousePos = list(mouse.position)

        if event.event_type == 'up':
            continue
        if event.name == 'enter':
            break

        if event.name == 'd':
            mousePos[0]+=1
        if event.name == 'r':
            mousePos = profile['originPoint']
        mouse.position = mousePos

    squareSize = mousePos[0]-profile["originPoint"][0]
    profile['squareSize'] = squareSize

def getBoardWidth():
    global profile
    mouse.position=profile['originPoint']

    print('\nUse the d key to move the mouse cursor to the bottom-left pixel of the rightmost square. hit enter when youre done')
    print('if you accidentally move your mouse, hit R')

    boardWidth=1

    while True:
        event = keyboard.read_event()
        mousePos = list(mouse.position)

        if event.event_type == 'up':
            continue
        if event.name == 'enter':
            break

        if event.name == 'd':
            mousePos[0] += profile['squareSize']
            boardWidth += 1
        if event.name == 'r':
            mousePos = profile['originPoint']
            boardWidth = 1

        mouse.position = mousePos

    profile['boardWidth'] = boardWidth

def getBoardHeight():
    global profile
    mouse.position = profile['originPoint']

    print('\nUse the s key to move the mouse cursor to the bottom-left pixel of the lowest square. hit enter when youre done')
    print('if you accidentally move your mouse, hit R')

    boardHeight=1

    while True:
        event = keyboard.read_event()
        mousePos = list(mouse.position)

        if event.event_type == 'up':
            continue
        if event.name == 'enter':
            break

        if event.name == 's':
            mousePos[1]+=profile['squareSize']
            boardHeight+=1
        if event.name == 'r':
            mousePos=profile['originPoint']
            boardHeight=1

        mouse.position = mousePos

    profile['boardHeight'] = boardHeight

def export():
    fullSettings:dict = {} 
    with open('Settings.json', 'r') as jsonFile:
        fullSettings = json.load(jsonFile)
    fullSettings.update(profile)

focus()
getOriginPoint()
getSquareSize()
getBoardWidth()
getBoardHeight()
export()