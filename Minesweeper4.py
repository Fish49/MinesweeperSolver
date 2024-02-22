#head
'''
Minesweeper Solver v4.0
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
import pygetwindow as gw

#variables
GameRegion=(716,361,487,432)
board=[]
mouse = pynput.mouse.Controller()
exitProgram=False
vscode = gw.getActiveWindow()

difficulty=3

if difficulty==1:
    originPoint=(0, 225)
    boardWidth=10
    boardHeight=8
    squareSize=45
    cOne=[25, 118, 210]
    cTwo=[56, 142, 60]
    cThree=[211, 47, 47]
    cFour=[137, 52, 162]
    cFive=[255, 143, 0]
    cSix=[0, 151, 167]
    cSeven=[109, 100, 91]
    cGreen=[162, 209, 73]
    cFlag=[242, 54, 7]
    defaultOffset=(22, -32)
    blueSpace=(850, 500)
    minSimilarity=10
elif difficulty==2:
    originPoint=(0, 210)
    boardWidth=18
    boardHeight=14
    squareSize=30
    cOne=[25, 118, 210]
    cTwo=[56, 142, 60]
    cThree=[211, 47, 47]
    cFour=[123, 31, 162]
    cFive=[255, 143, 0]
    cSix=[0, 151, 167]
    cSeven=[109, 100, 91]
    cGreen=[170, 215, 81]
    cFlag=[242, 54, 7]
    defaultOffset=(16, -21)
    blueSpace=(850, 500)
    minSimilarity=10
elif difficulty==3:
    originPoint=(0, 205)
    boardWidth=24
    boardHeight=20
    squareSize=25
    cOne=[25, 118, 210]
    cTwo=[111, 156, 92]
    cThree=[218, 105, 91]
    cFour=[136, 52, 161]
    cFive=[249, 150, 24]
    cSix=[0, 151, 167]
    cSeven=[109, 100, 91]
    cGreen=[170, 215, 81]
    cFlag=[242, 54, 7]
    defaultOffset=(12, -17)
    blueSpace=(850, 500)
    minSimilarity=10

clicks=[
    [round(0.5*boardWidth), round(0.5*boardHeight)],
    [round(0.15*boardWidth), round(0.15*boardHeight)],
    [round(0.85*boardWidth), round(0.15*boardHeight)],
    [round(0.15*boardWidth), round(0.85*boardHeight)],
    [round(0.85*boardWidth), round(0.85*boardHeight)]
]

#functions
def accessGridSpace(cordinate, offsetX=0, offsetY=0):
    return [(originPoint[0]+math.ceil(squareSize*cordinate[0]))+offsetX, (originPoint[1]+math.ceil(squareSize*cordinate[1]))+offsetY]

def getCordFromI(Index):
    return [Index%boardWidth, int((Index-(Index%boardWidth))/boardWidth)]

def getPixelMatch(pixel, targetColor, similarity):
    minColor=[targetColor[0]-similarity, targetColor[1]-similarity, targetColor[2]-similarity]
    maxColor=[targetColor[0]+similarity, targetColor[1]+similarity, targetColor[2]+similarity]
    pixelHigh=pixel[0] > minColor[0] and pixel[1] > minColor[1] and pixel[2] > minColor[2]
    pixelLow=pixel[0] < maxColor[0] and pixel[1] < maxColor[1] and pixel[2] < maxColor[2]

    if pixelHigh and pixelLow:
        return True
    return False

def getState(Index):
    tempPixel=screen.getpixel(accessGridSpace(getCordFromI(Index), defaultOffset[0], defaultOffset[1]))

    if getPixelMatch(tempPixel, cGreen, minSimilarity):
        return 'g'
    elif getPixelMatch(tempPixel, cFlag, minSimilarity):
        return 'f'
    elif getPixelMatch(tempPixel, cOne, minSimilarity):
        return 1
    elif getPixelMatch(tempPixel, cTwo, minSimilarity):
        return 2
    elif getPixelMatch(tempPixel, cThree, minSimilarity):
        return 3
    elif getPixelMatch(tempPixel, cFour, minSimilarity):
        return 4
    elif getPixelMatch(tempPixel, cFive, minSimilarity):
        return 5
    elif getPixelMatch(tempPixel, cSix, minSimilarity):
        return 6
    elif getPixelMatch(tempPixel, cSeven, minSimilarity):
        return 7
    return 'b'

def getSurrounding(index, look):
    surroundList=[[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
    baseCord=getCordFromI(index)
    returnList=[]
    for i in surroundList:
        searchCord=[baseCord[0]+i[0], baseCord[1]+i[1]]
        if 0 <= searchCord[0] < boardWidth and 0 <= searchCord[1] < boardHeight:
            searchIndex=(searchCord[1]*boardWidth)+searchCord[0]
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
for i in range(boardWidth*boardHeight):
        board.append(getState(i))

while not (getPixelMatch(screen.getpixel(blueSpace), [77, 193, 249], 10) or exitProgram):
    
    mouse.position = accessGridSpace((math.floor(0.5*boardWidth), math.floor(0.5*boardHeight)))
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

#if not exitProgram:
    #time.sleep(1)
    #mouse.position = (850, 700)
    #mouse.click(pynput.mouse.Button.left)
    #time.sleep(0.3)
    #vscode.activate()

keyboard.unhook_all()
keyboard_thread.join()