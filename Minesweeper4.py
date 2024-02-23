#head
'''
Minesweeper Solver v4.1
-PaiShoFish49
1/11/24
'''

#imports
from PIL import ImageGrab
import pynput
import time
import threading
import keyboard
import math
import json

#variables
board=[]
mouse = pynput.mouse.Controller()
exitProgram=False

difficulty='GoogleHard'

with open('Settings.json', 'r') as Settings:
    try:
        properties=json.load(Settings)[difficulty]
    except KeyError:
        exit('No difficulty level matches the inputed value')

clicks=[
    [round(0.5*properties['boardWidth']), round(0.5*properties['boardHeight'])],
    [round(0.15*properties['boardWidth']), round(0.15*properties['boardHeight'])],
    [round(0.85*properties['boardWidth']), round(0.15*properties['boardHeight'])],
    [round(0.15*properties['boardWidth']), round(0.85*properties['boardHeight'])],
    [round(0.85*properties['boardWidth']), round(0.85*properties['boardHeight'])]
]

#functions
def accessGridSpace(cordinate, offsetX=0, offsetY=0):
    return [(properties['originPoint'][0]+math.ceil(properties['squareSize']*cordinate[0]))+offsetX, (properties['originPoint'][1]+math.ceil(properties['squareSize']*cordinate[1]))+offsetY]

def getCordFromI(Index):
    return [Index%properties['boardWidth'], int((Index-(Index%properties['boardWidth']))/properties['boardWidth'])]

def getPixelMatch(pixel, targetColor, similarity):
    minColor=[targetColor[0]-similarity, targetColor[1]-similarity, targetColor[2]-similarity]
    maxColor=[targetColor[0]+similarity, targetColor[1]+similarity, targetColor[2]+similarity]
    pixelHigh=pixel[0] > minColor[0] and pixel[1] > minColor[1] and pixel[2] > minColor[2]
    pixelLow=pixel[0] < maxColor[0] and pixel[1] < maxColor[1] and pixel[2] < maxColor[2]

    if pixelHigh and pixelLow:
        return True
    return False

def getState(Index):
    tempPixel=screen.getpixel(accessGridSpace(getCordFromI(Index),properties['defaultOffset'][0],properties['defaultOffset'][1]))

    if getPixelMatch(tempPixel, properties['cGreen'], properties['minSimilarity']):
        return 'g'
    elif getPixelMatch(tempPixel, properties['cFlag'], properties['minSimilarity']):
        return 'f'
    elif getPixelMatch(tempPixel, properties['cOne'], properties['minSimilarity']):
        return 1
    elif getPixelMatch(tempPixel, properties['cTwo'], properties['minSimilarity']):
        return 2
    elif getPixelMatch(tempPixel, properties['cThree'], properties['minSimilarity']):
        return 3
    elif getPixelMatch(tempPixel, properties['cFour'], properties['minSimilarity']):
        return 4
    elif getPixelMatch(tempPixel, properties['cFive'], properties['minSimilarity']):
        return 5
    elif getPixelMatch(tempPixel, properties['cSix'], properties['minSimilarity']):
        return 6
    elif getPixelMatch(tempPixel, properties['cSeven'], properties['minSimilarity']):
        return 7
    return 'b'

def getSurrounding(index, look):
    surroundList=[[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
    baseCord=getCordFromI(index)
    returnList=[]
    for i in surroundList:
        searchCord=[baseCord[0]+i[0], baseCord[1]+i[1]]
        if 0 <= searchCord[0] < properties['boardWidth'] and 0 <= searchCord[1] < properties['boardHeight']:
            searchIndex=(searchCord[1]*properties['boardWidth'])+searchCord[0]
            if board[searchIndex] == look:
                returnList.append(searchIndex)
    return returnList

def countSurroundingFilled(index):
    return len(getSurrounding(index, 'f'))+len(getSurrounding(index, 'g'))

def on_key_event(e):
    global exitProgram
    if e.name == 'esc':
        exitProgram=True

# Start the keyboard listener in a separate thread
keyboard_thread = threading.Thread(target=keyboard.hook, args=(on_key_event,))
keyboard_thread.start()


#main function
start = time.time()

if False:
    for i in clicks:
        mouse.position = accessGridSpace(i)
        mouse.click(pynput.mouse.Button.left)
    end=time.time()
else:
    mouse.position = accessGridSpace(clicks[0])
    mouse.click(pynput.mouse.Button.left)
    end=time.time()

screen = ImageGrab.grab()
for i in range(properties['boardWidth']*properties['boardHeight']):
        board.append(getState(i))

while not (getPixelMatch(screen.getpixel(properties['blueSpace']), [77, 193, 249], 10) or exitProgram):
    
    mouse.position = accessGridSpace((math.floor(0.5*properties['boardWidth']), math.floor(0.5*properties['boardHeight'])))
    mouse.click(pynput.mouse.Button.left)

    screen = ImageGrab.grab()
    for i in range(len(board)):
        if board[i] != 'f':
            board[i] = getState(i)

    for i in range(len(board)):
        if board[i] in [1, 2, 3, 4, 5, 6, 7]:
            if countSurroundingFilled(i) == board[i]:
                surroundingSpaces=getSurrounding(i, 'g')
                for j in surroundingSpaces:
                    board[j]='f'
                    mouse.position = accessGridSpace(getCordFromI(j))
                    mouse.click(pynput.mouse.Button.right)
                    
    for i in range(len(board)):
        if board[i] in [1, 2, 3, 4, 5, 6, 7]:
            if len(getSurrounding(i, 'g'))>0 and len(getSurrounding(i, 'f'))==board[i]:
                end=time.time()
                mouse.position = accessGridSpace(getCordFromI(i))
                mouse.click(pynput.mouse.Button.middle)

print(f'Time: {end-start}')

keyboard.unhook_all()
keyboard_thread.join()