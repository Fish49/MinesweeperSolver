#head
'''
Minesweeper Solver v4.2
-PaiShoFish49
1/11/24

OUTDATED CODE
'''

#imports
from PIL import ImageGrab #to get access to the contents of the screen. this is how it gets the board data
import pynput #used to control the mouse
import threading #used for the event listener.
import keyboard #keyboard is used to set up an event listener for ESC in the event that the user wishes to stop the bot
import math #math is used primarily for rounding values to the nearest block space
import json #to access the settings profiles.
import time #to control timing

#variables
board=[] #this is a list of the state of every space on the minesweeper board. it can be any number 1-8, 'b' for blank, 'g' for green, or 'f' for flag
mouse = pynput.mouse.Controller() #setting up the mouse controller.
exitProgram=False #the main loop has exitProgram as an escape condition. when the ESC event listener is activated, it sets this variable to True.

#set this to the difficulty profile you want. by default their are only 3, GoogleEasy, GoogleMedium, and GoogleHard.
#you can manually add new profiles for different difficulties or versions of the game. in theory, it should work for any version of minesweeper with very few exeptions.
difficulty='GoogleHard' 
restartPosition = [1000, 700]

with open('Settings.json', 'r') as Settings: #boilerplate to retrieve the settings profile from the json file
    try:
        properties=json.load(Settings)[difficulty]
    except KeyError:
        exit('No difficulty level matches the inputed value')

clicks=[ #these are the areas that the bot will click if you enable it later in the code. If you do, the bot is more likely to lose immediately, but if it doesnt than it has a headstart.
    [round(0.5*properties['boardWidth']), round(0.5*properties['boardHeight'])],
    [round(0.15*properties['boardWidth']), round(0.15*properties['boardHeight'])],
    [round(0.85*properties['boardWidth']), round(0.15*properties['boardHeight'])],
    [round(0.15*properties['boardWidth']), round(0.85*properties['boardHeight'])],
    [round(0.85*properties['boardWidth']), round(0.85*properties['boardHeight'])]
]

#functions
#input a board cordinate as a tuple or list, and it will return the bottom-left pixel coordinate of that square.
#for example, i would accessGridSpace([3, 0]) and if each square is 10 pixels long and the board is perfectly aligned, it would return [30, 10]
def accessGridSpace(cordinate, offsetX=0, offsetY=0): 
    return [(properties['originPoint'][0]+math.ceil(properties['squareSize']*cordinate[0]))+offsetX, (properties['originPoint'][1]+math.ceil(properties['squareSize']*cordinate[1]))+offsetY]

#input an index, and it will use the boardWidth and boardHeight properties to return a list with the board cordinate.
#the board cordinate it returns corresponds to the index in the variable "board"
#you will often see accessGridSpace(getCordFromI(i)), this just takes an index and returns the pixel cordinate that matches that index.
def getCordFromI(Index): 
    return [Index%properties['boardWidth'], int((Index-(Index%properties['boardWidth']))/properties['boardWidth'])]

#This takes a color; "pixel" and a target color, and if they're similar enough it will return True. 
#for similarity it can be any number between 0 and 255, 0 being the most strict and 255 being that it will always return True. I typically go with 10.
def getPixelMatch(pixel, targetColor, similarity):
    minColor=[targetColor[0]-similarity, targetColor[1]-similarity, targetColor[2]-similarity] #sets the low end for the darkest that the color can be.
    maxColor=[targetColor[0]+similarity, targetColor[1]+similarity, targetColor[2]+similarity] #sets the high end for how light the color can be.
    pixelHigh=pixel[0] > minColor[0] and pixel[1] > minColor[1] and pixel[2] > minColor[2] #checks if the color is light enough for each rgb channel
    pixelLow=pixel[0] < maxColor[0] and pixel[1] < maxColor[1] and pixel[2] < maxColor[2] #checks if the color is dark enough for each rgb channel

    if pixelHigh and pixelLow: #if its not too light and not too dark, goldylocks eats the porridge
        return True
    return False

#uses getPixelMatch to determine what state a square is in based on the color of a specific pixel in the square.
#the pixel it should check is in the defaultOffset property, and the color that matches each state is in their respective properties.
#if it doesnt match any of the specified colors, it assumes the square is blank.
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

#this returns a list of all the tiles surrounding a specific tile (index) that matches the state (look)
#for example, if i have a square surrounded by flags, and I wrote getSurrounding(4, 'f'), it would return a list of 8 indecies, one for each surrounding tile
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

#just like getSurrounding but it returns the number of tiles instead of a list of their indicies, and it only counts green and flagged squares.
def countSurroundingFilled(index):
    return len(getSurrounding(index, 'f'))+len(getSurrounding(index, 'g'))

#threding boilerplate
def on_key_event(e):
    global exitProgram
    if e.name == 'esc':
        exitProgram=True

#starts the keyboard listener in a separate thread
keyboard_thread = threading.Thread(target=keyboard.hook, args=(on_key_event,))
keyboard_thread.start()


#main function
while not exitProgram:
    if False: #option to enable playing risky at the beginning. if you do, its more likely to lose immediately but if it doesnt then it has a headstart.
        for i in clicks:
            mouse.position = accessGridSpace(i)
            mouse.click(pynput.mouse.Button.left)
    else:
        mouse.position = accessGridSpace(clicks[0])
        mouse.click(pynput.mouse.Button.left)
    
    board = []
    screen = ImageGrab.grab() #takes a screenshot and filles in the board with its current state
    for i in range(properties['boardWidth']*properties['boardHeight']):
        board.append(getState(i))

    timeOfLastMove = time.time() + 3

    while not (getPixelMatch(screen.getpixel(properties['blueSpace']), [77, 193, 249], 10) or exitProgram):
        
        mouse.position = accessGridSpace((math.floor(0.5*properties['boardWidth']), math.floor(0.5*properties['boardHeight'])))
        mouse.click(pynput.mouse.Button.left)

        screen = ImageGrab.grab() #takes a screenshot and fills in the board with its current state
        for i in range(len(board)):
            if board[i] != 'f': #due to the particles that are released when you click a tile, and the speed of my bot, it can mistake flags for green squares, this if is just to make sure it doesnt unflag anything
                board[i] = getState(i)

        for i in range(len(board)): #goes through the board and checks if each tile has the same number of neighbors as its number. if so, it knows that it can flag all surrounding green squares.
            if board[i] in [1, 2, 3, 4, 5, 6, 7]: #making sure the square is a number.
                if countSurroundingFilled(i) == board[i]: #checking if it meets the conditions to flag all neghibors
                    surroundingSpaces=getSurrounding(i, 'g') #recording the positions of all green neighbors
                    for j in surroundingSpaces: #process of flagging that which needs to be flagged.
                        board[j]='f' #marks the space as a flag
                        mouse.position = accessGridSpace(getCordFromI(j))
                        mouse.click(pynput.mouse.Button.right)
                        timeOfLastMove = time.time()
                        
        for i in range(len(board)): #goes through the board and checks if each tile has the same number of neighbor flags as its number, if so, it can clear all surrounding greens by middle clicking.
            if board[i] in [1, 2, 3, 4, 5, 6, 7]:
                if len(getSurrounding(i, 'g'))>0 and len(getSurrounding(i, 'f'))==board[i]: #makes sure that there are the correct amount of surrounding flags and at least one green to clear (to not waste time)
                    mouse.position = accessGridSpace(getCordFromI(i))
                    mouse.click(pynput.mouse.Button.middle)
                    timeOfLastMove = time.time()
        
        if time.time() - timeOfLastMove > 1: #if nothing is happening, make a guess.
            tileOfHighestPriority=[0, 0] #the tile with the most number of safe neighbor guesses, first is the tile index, second is its priority.
            for i in range(len(board)):
                if board[i] in [1, 2, 3, 4, 5, 6, 7]:
                    tilePriority = len(getSurrounding(i, 'g')) - board[i] #calculating the probablilty of any of the surrounding greens being bombs. higher number means less likely per neighboring green.
                    if  tilePriority > tileOfHighestPriority[1]: #if the current tile has a higher priority than any others on the board, its the new highest.
                        tileOfHighestPriority = [i, tilePriority] #assigning the value
            mouse.position = accessGridSpace(getCordFromI(getSurrounding(tileOfHighestPriority[0], 'g')[0]))
            mouse.click(pynput.mouse.Button.left)
            timeOfLastMove = time.time() - 0.5

    mouse.position = restartPosition
    mouse.click(pynput.mouse.Button.left)

keyboard.unhook_all() #threading boilerplate
keyboard_thread.join() #"