#head
'''
Minesweeper Solver v4.3
Yet another python file.
-PaiShoFish49
2/29/24
'''

#imports
from PIL import ImageGrab #to get access to the contents of the screen. this is how it gets the board data
import pynput #used to control the mouse
import threading #used for the event listener.
import keyboard #keyboard is used to set up an event listener for ESC in the event that the user wishes to stop the bot
import math #math is used primarily for rounding values to the nearest block space
import json #to access the settings profiles.
import time #to control timing
import tkinter as tk #for window stuff.

class Board():
    def __init__(self, properties) -> None:
        self.properties = properties
        self.clicks = [ #these are the areas that the bot will click if you enable it later in the code. If you do, the bot is more likely to lose immediately, but if it doesnt than it has a headstart.
            [round(0.5*properties['boardWidth']), round(0.5*properties['boardHeight'])],
            [round(0.15*properties['boardWidth']), round(0.15*properties['boardHeight'])],
            [round(0.85*properties['boardWidth']), round(0.15*properties['boardHeight'])],
            [round(0.15*properties['boardWidth']), round(0.85*properties['boardHeight'])],
            [round(0.85*properties['boardWidth']), round(0.85*properties['boardHeight'])]
        ]
        self.restartPosition = [1000, 700]
        self.board = []
        self.exitProgram = False

    #input a board cordinate as a tuple or list, and it will return the bottom-left pixel coordinate of that square.
    #for example, i would accessGridSpace([3, 0]) and if each square is 10 pixels long and the board is perfectly aligned, it would return [30, 10]
    def accessGridSpace(self, cordinate, offsetX=0, offsetY=0): 
        return [(self.properties['originPoint'][0]+math.ceil(self.properties['squareSize']*cordinate[0]))+offsetX, (self.properties['originPoint'][1]+math.ceil(self.properties['squareSize']*cordinate[1]))+offsetY]

    #input an index, and it will use the boardWidth and boardHeight properties to return a list with the board cordinate.
    #the board cordinate it returns corresponds to the index in the variable "board"
    #you will often see accessGridSpace(getCordFromI(i)), this just takes an index and returns the pixel cordinate that matches that index.
    def getCordFromI(self, Index): 
        return [Index%self.properties['boardWidth'], int((Index-(Index%self.properties['boardWidth']))/self.properties['boardWidth'])]

    #This takes a color; "pixel" and a target color, and if they're similar enough it will return True. 
    #for similarity it can be any number between 0 and 255, 0 being the most strict and 255 being that it will always return True. I typically go with 10.
    def getPixelMatch(self, pixel, targetColor, similarity):
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
    def getState(self, Index, screen):
        tempPixel=screen.getpixel(self.accessGridSpace(self.getCordFromI(Index),self.properties['defaultOffset'][0],self.properties['defaultOffset'][1]))

        if self.getPixelMatch(tempPixel, self.properties['cGreen'], self.properties['minSimilarity']):
            return 'g'
        elif self.getPixelMatch(tempPixel, self.properties['cFlag'], self.properties['minSimilarity']):
            return 'f'
        elif self.getPixelMatch(tempPixel, self.properties['cOne'], self.properties['minSimilarity']):
            return 1
        elif self.getPixelMatch(tempPixel, self.properties['cTwo'], self.properties['minSimilarity']):
            return 2
        elif self.getPixelMatch(tempPixel, self.properties['cThree'], self.properties['minSimilarity']):
            return 3
        elif self.getPixelMatch(tempPixel, self.properties['cFour'], self.properties['minSimilarity']):
            return 4
        elif self.getPixelMatch(tempPixel, self.properties['cFive'], self.properties['minSimilarity']):
            return 5
        elif self.getPixelMatch(tempPixel, self.properties['cSix'], self.properties['minSimilarity']):
            return 6
        elif self.getPixelMatch(tempPixel, self.properties['cSeven'], self.properties['minSimilarity']):
            return 7
        return 'b'
    
    #this returns a list of all the tiles surrounding a specific tile (index) that matches the state (look)
    #for example, if i have a square surrounded by flags, and I wrote getSurrounding(4, 'f'), it would return a list of 8 indecies, one for each surrounding tile
    def getSurrounding(self, index, look):
        surroundList=[[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
        baseCord=self.getCordFromI(index)
        returnList=[]
        for i in surroundList:
            searchCord=[baseCord[0]+i[0], baseCord[1]+i[1]]
            if 0 <= searchCord[0] < self.properties['boardWidth'] and 0 <= searchCord[1] < self.properties['boardHeight']:
                searchIndex=(searchCord[1]*self.properties['boardWidth'])+searchCord[0]
                if self.board[searchIndex] == look:
                    returnList.append(searchIndex)
        return returnList
    
    #just like getSurrounding but it returns the number of tiles instead of a list of their indicies, and it only counts green and flagged squares.
    def countSurroundingFilled(self, index):
        return len(self.getSurrounding(index, 'f'))+len(self.getSurrounding(index, 'g'))

mouse = pynput.mouse.Controller() #setting up the mouse controller.


with open('Settings.json', 'r') as SettingsFile:
    propertyProfiles = json.load(SettingsFile)

def on_key_event(e):
    global exitProgram
    if e.name == 'esc':
        exitProgram=True

def onStart():
    global exitProgram
    exitProgram=False
    mainBoard = Board(propertyProfiles[difficulty_var.get()])
    playRisky = risky_play_var.get()

    keyboard_thread = threading.Thread(target=keyboard.hook, args=(on_key_event,))
    keyboard_thread.start()

    #main function
    while not exitProgram:
        if playRisky: #option to enable playing risky at the beginning. if you do, its more likely to lose immediately but if it doesnt then it has a headstart.
            for i in mainBoard.clicks:
                mouse.position = mainBoard.accessGridSpace(i)
                mouse.click(pynput.mouse.Button.left)
        else:
            mouse.position = mainBoard.accessGridSpace(mainBoard.clicks[0])
            mouse.click(pynput.mouse.Button.left)
        
        mainBoard.board = []
        screen = ImageGrab.grab() #takes a screenshot and filles in the board with its current state
        for i in range(mainBoard.properties['boardWidth']*mainBoard.properties['boardHeight']):
            mainBoard.board.append(mainBoard.getState(i, screen))

        timeOfLastMove = time.time() + 3

        while not (mainBoard.getPixelMatch(screen.getpixel(mainBoard.properties['blueSpace']), [77, 193, 249], 10) or exitProgram):
            
            mouse.position = mainBoard.accessGridSpace((math.floor(0.5*mainBoard.properties['boardWidth']), math.floor(0.5*mainBoard.properties['boardHeight'])))
            mouse.click(pynput.mouse.Button.left)

            screen = ImageGrab.grab() #takes a screenshot and fills in the board with its current state
            for i in range(len(mainBoard.board)):
                if mainBoard.board[i] != 'f': #due to the particles that are released when you click a tile, and the speed of my bot, it can mistake flags for green squares, this if is just to make sure it doesnt unflag anything
                    mainBoard.board[i] = mainBoard.getState(i, screen)

            for i in range(len(mainBoard.board)): #goes through the board and checks if each tile has the same number of neighbors as its number. if so, it knows that it can flag all surrounding green squares.
                if mainBoard.board[i] in [1, 2, 3, 4, 5, 6, 7]: #making sure the square is a number.
                    if mainBoard.countSurroundingFilled(i) == mainBoard.board[i]: #checking if it meets the conditions to flag all neghibors
                        surroundingSpaces=mainBoard.getSurrounding(i, 'g') #recording the positions of all green neighbors
                        for j in surroundingSpaces: #process of flagging that which needs to be flagged.
                            mainBoard.board[j]='f' #marks the space as a flag
                            mouse.position = mainBoard.accessGridSpace(mainBoard.getCordFromI(j))
                            mouse.click(pynput.mouse.Button.right)
                            timeOfLastMove = time.time()
                            
            for i in range(len(mainBoard.board)): #goes through the board and checks if each tile has the same number of neighbor flags as its number, if so, it can clear all surrounding greens by middle clicking.
                if mainBoard.board[i] in [1, 2, 3, 4, 5, 6, 7]:
                    if len(mainBoard.getSurrounding(i, 'g'))>0 and len(mainBoard.getSurrounding(i, 'f'))==mainBoard.board[i]: #makes sure that there are the correct amount of surrounding flags and at least one green to clear (to not waste time)
                        mouse.position = mainBoard.accessGridSpace(mainBoard.getCordFromI(i))
                        mouse.click(pynput.mouse.Button.middle)
                        timeOfLastMove = time.time()
            
            if time.time() - timeOfLastMove > 1: #if nothing is happening, make a guess.
                tileOfHighestPriority=[0, 0] #the tile with the most number of safe neighbor guesses, first is the tile index, second is its priority.
                for i in range(len(mainBoard.board)):
                    if mainBoard.board[i] in [1, 2, 3, 4, 5, 6, 7]:
                        tilePriority = len(mainBoard.getSurrounding(i, 'g')) - mainBoard.board[i] #calculating the probablilty of any of the surrounding greens being bombs. higher number means less likely per neighboring green.
                        if  tilePriority > tileOfHighestPriority[1]: #if the current tile has a higher priority than any others on the board, its the new highest.
                            tileOfHighestPriority = [i, tilePriority] #assigning the value
                try:
                    mouse.position = mainBoard.accessGridSpace(mainBoard.getCordFromI(mainBoard.getSurrounding(tileOfHighestPriority[0], 'g')[0]))
                except:
                    for i in range(len(mainBoard.board)):
                        if mainBoard.board[i] == 'g':
                            mouse.position = mainBoard.accessGridSpace(mainBoard.getCordFromI(i))
                            break
                mouse.click(pynput.mouse.Button.left)
                timeOfLastMove = time.time() - 0.5

        mouse.position = mainBoard.restartPosition
        time.sleep(0.2)
        mouse.click(pynput.mouse.Button.left)

    keyboard.unhook_all() #threading boilerplate
    keyboard_thread.join() #"

    time.sleep(0.3)
    window.deiconify()

def calibrate():
    newPropertyProfile={
        'Custom':{
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
    }

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

    newPropertyProfile['Custom']['originPoint']=mousePos

    propertyProfiles.update(newPropertyProfile)

    mouse.position=newPropertyProfile['Custom']['originPoint']

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
            mousePos = newPropertyProfile['Custom']['originPoint']
        mouse.position = mousePos

    squareSize = mousePos[0]-newPropertyProfile['Custom']['originPoint']
    newPropertyProfile['Custom']['squareSize'] = squareSize

    mouse.position=newPropertyProfile['Custom']['originPoint']

    boardWidth=1

    while True:
        event = keyboard.read_event()
        mousePos = list(mouse.position)

        if event.event_type == 'up':
            continue
        if event.name == 'enter':
            break

        if event.name == 'd':
            mousePos[0] += newPropertyProfile['Custom']['squareSize']
            boardWidth += 1
        if event.name == 'r':
            mousePos = newPropertyProfile['Custom']['originPoint']
            boardWidth = 1

        mouse.position = mousePos

    newPropertyProfile['Custom']['boardWidth'] = boardWidth

    mouse.position = newPropertyProfile['Custom']['originPoint']

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
            mousePos[1]+=newPropertyProfile['Custom']['squareSize']
            boardHeight+=1
        if event.name == 'r':
            mousePos=newPropertyProfile['Custom']['originPoint']
            boardHeight=1

        mouse.position = mousePos

    newPropertyProfile['Custom']['boardHeight'] = boardHeight

window = tk.Tk()
window.title('Minesweeper Solver!')

# Difficulty dropdown
difficulty_var = tk.StringVar()
difficulty_label = tk.Label(window, text="Select Difficulty:")
difficulty_label.pack()
difficulty_dropdown = tk.OptionMenu(window, difficulty_var, *propertyProfiles.keys())
difficulty_dropdown.pack()

# Toggle for risky play
risky_play_var = tk.BooleanVar()
risky_play_var.set(False)  # Default risky play disabled
risky_play_checkbox = tk.Checkbutton(window, text="Enable Risky Play", variable=risky_play_var)
risky_play_checkbox.pack()

# Button to start solver
start_button = tk.Button(window, text="Start Solver", command=onStart)
start_button.pack()

calibrateButton = tk.Button(window, text='Calibrate', command=calibrate)
calibrateButton.pack

window.mainloop()