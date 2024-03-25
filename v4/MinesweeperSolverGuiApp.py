#head
'''
Minesweeper Solver v4.6.4
Yet another python file.
-PaiShoFish49
2/29/24
'''

#imports
from PIL import ImageGrab, Image, ImageTk, ImageDraw #to get access to the contents of the screen. this is how it gets the board data
import pynput #used to control the mouse
import threading #used for the event listener.
import keyboard #keyboard is used to set up an event listener for ESC in the event that the user wishes to stop the bot
import math #math is used primarily for rounding values to the nearest block space
import json #to access the settings profiles.
import time #to control timing
import tkinter as tk #for window stuff.
from tkinter import ttk
from ttkthemes import ThemedTk

class Board():
    def __init__(self, properties, clickSpace) -> None:
        self.properties = properties
        self.clicks = [ #these are the areas that the bot will click if you enable it later in the code. If you do, the bot is more likely to lose immediately, but if it doesnt than it has a headstart.
            [round(0.5*properties['boardWidth']), round(0.5*properties['boardHeight'])],
            [round(0.15*properties['boardWidth']), round(0.15*properties['boardHeight'])],
            [round(0.85*properties['boardWidth']), round(0.15*properties['boardHeight'])],
            [round(0.15*properties['boardWidth']), round(0.85*properties['boardHeight'])],
            [round(0.85*properties['boardWidth']), round(0.85*properties['boardHeight'])]
        ]
        self.clickSpace = clickSpace
        self.board = []
        self.exitProgram = False

    #input a board cordinate as a tuple or list, and it will return the bottom-left pixel coordinate of that square.
    #for example, i would accessGridSpace([3, 0]) and if each square is 10 pixels long and the board is perfectly aligned, it would return [30, 10]
    def accessGridSpace(self, cordinate, offsetX=0, offsetY=0, considerOrigin=True):
        startingPoint = self.properties['originPoint'] if considerOrigin else (0, self.properties['squareSize']-1)
        pixelCordinate = (self.properties['squareSize']*cordinate[0], self.properties['squareSize']*cordinate[1])
        alignedPixelCordinate = (pixelCordinate[0]+startingPoint[0]+offsetX, pixelCordinate[1]+startingPoint[1]+offsetY)
        return alignedPixelCordinate

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
        tempPixel=screen.getpixel(self.accessGridSpace(self.getCordFromI(Index), self.properties['defaultOffset'][0], self.properties['defaultOffset'][1], False))

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
    
    def getScreen(self, blueSpace = False):
        if blueSpace:
            screen = ImageGrab.grab((*self.properties['blueSpace'], self.properties['blueSpace'][0]+1, self.properties['blueSpace'][0]+1), all_screens=True)
        else:
            TL = (self.properties['originPoint'][0], self.properties['originPoint'][1]-self.properties['squareSize']+1)
            BR = (TL[0]+(self.properties['squareSize']*(self.properties['boardWidth'])), TL[1]+(self.properties['squareSize']*self.properties['boardHeight']))
            screen = ImageGrab.grab((*TL, *BR), all_screens=True)
        return screen

mouse = pynput.mouse.Controller() #setting up the mouse controller.
mouseOrigin = (0, 0)
mousePosition = (0, 0)
clickSpace = (1000, 700)

with open('Settings.json', 'r') as SettingsFile:
    propertyProfiles = json.load(SettingsFile)

propertyProfiles.update({
    'Custom':{
    "originPoint":[0, 0],
    "boardWidth":1,
    "boardHeight":1,
    "squareSize":1,
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
})

def on_key_event(e):
    global exitProgram
    if e.name == 'esc':
        exitProgram=True

def onStart():
    global propertyProfiles
    global exitProgram
        
    exitProgram=False
    mainBoard = Board(propertyProfiles[difficulty_var.get()], clickSpace)
    playRisky = risky_play_var.get()
    repeat = repeatToggleVar.get()

    keyboard_thread = threading.Thread(target=keyboard.hook, args=(on_key_event,))
    keyboard_thread.start()

    #main function
    while not exitProgram:
        time.sleep(0.2)
        if playRisky: #option to enable playing risky at the beginning. if you do, its more likely to lose immediately but if it doesnt then it has a headstart.
            for i in mainBoard.clicks:
                mouse.position = mainBoard.accessGridSpace(i)
                mouse.click(pynput.mouse.Button.left)
        else:
            mouse.position = mainBoard.accessGridSpace(mainBoard.clicks[0])
            mouse.click(pynput.mouse.Button.left)
        
        mainBoard.board = []
        screen = mainBoard.getScreen() #takes a screenshot and filles in the board with its current state
        for i in range(mainBoard.properties['boardWidth']*mainBoard.properties['boardHeight']):
            mainBoard.board.append(mainBoard.getState(i, screen))

        timeOfLastMove = time.time() + 3

        while not (mainBoard.getPixelMatch(mainBoard.getScreen(True).getpixel((0, 0)), [77, 193, 249], 10) or exitProgram):
            
            mouse.position = mainBoard.accessGridSpace((math.floor(0.5*mainBoard.properties['boardWidth']), math.floor(0.5*mainBoard.properties['boardHeight'])))
            mouse.click(pynput.mouse.Button.left)

            screen = mainBoard.getScreen() #takes a screenshot and fills in the board with its current state
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

        if not repeat:
            break

        mouse.position = mainBoard.clickSpace
        time.sleep(0.2)
        mouse.click(pynput.mouse.Button.left)

    keyboard.unhook_all() #threading boilerplate
    keyboard_thread.join() #"

    time.sleep(0.3)
    window.deiconify()

def editCustom():
    def calibrate():
        calibrationLabel.config(text='use WASD to locate the bottom-left pixel of the top-left square on the board. when youre done hit ENTER', wraplength=calibrateFrame.winfo_width())
        calibrationLabel.update()

        while True:
            event = keyboard.read_event()
            mousePos = list(mouse.position)

            if event.event_type == 'up':
                continue
            if event.name == 'esc':
                calibrationLabel.config(text='')
                return
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

        propertyProfiles['Custom']['originPoint']=mousePos

        mouse.position=propertyProfiles['Custom']['originPoint']

        calibrationLabel.config(text='use D key to locate the bottom-left pixel of the tile to the right, hit the r key to reset. when youre done hit ENTER')
        calibrationLabel.update()

        while True:
            event = keyboard.read_event()
            mousePos = list(mouse.position)

            if event.event_type == 'up':
                continue
            if event.name == 'esc':
                calibrationLabel.config(text='')
                return
            if event.name == 'enter':
                break

            if event.name == 'd':
                mousePos[0]+=1
            if event.name == 'r':
                mousePos = propertyProfiles['Custom']['originPoint']
            mouse.position = mousePos

        squareSize = mousePos[0]-propertyProfiles['Custom']['originPoint'][0]
        propertyProfiles['Custom']['squareSize'] = squareSize

        mouse.position=propertyProfiles['Custom']['originPoint']

        calibrationLabel.config(text='use D key to locate the bottom-left pixel of the rightmost tile, hit the r key to reset. when youre done hit ENTER')
        calibrationLabel.update()

        boardWidth = 1
        boardHeight = 1

        while True:
            event = keyboard.read_event()
            mousePos = list(mouse.position)

            if event.event_type == 'up':
                continue
            if event.name == 'esc':
                calibrationLabel.config(text='')
                return
            if event.name == 'enter':
                break

            if event.name == 'd':
                mousePos[0] += propertyProfiles['Custom']['squareSize']
                boardWidth += 1
            if event.name == 'r':
                mousePos = propertyProfiles['Custom']['originPoint']
                boardWidth = 1

            mouse.position = mousePos

        propertyProfiles['Custom']['boardWidth'] = boardWidth

        mouse.position = propertyProfiles['Custom']['originPoint']

        calibrationLabel.config(text='use S key to locate the bottom-left pixel of the lowest tile, hit the r key to reset. when youre done hit ENTER')
        calibrationLabel.update()

        while True:
            event = keyboard.read_event()
            mousePos = list(mouse.position)

            if event.event_type == 'up':
                continue
            if event.name == 'esc':
                calibrationLabel.config(text='')
                return
            if event.name == 'enter':
                break

            if event.name == 's':
                mousePos[1]+=propertyProfiles['Custom']['squareSize']
                boardHeight+=1
            if event.name == 'r':
                mousePos=propertyProfiles['Custom']['originPoint']
                boardHeight=1

            mouse.position = mousePos

        propertyProfiles['Custom']['boardHeight'] = boardHeight

        propertyProfiles.update(propertyProfiles)

        calibrationLabel.config(text='')
        calibrationLabel.update()

    def goToPixel():
        global mousePosition
        mouse.position = [int(XmouseEntry.get()), int(YmouseEntry.get())]
        mousePosition = mouse.position
        useWASDLabel.config(text = 'Mouse Position:' + str((mousePosition[0]-mouseOrigin[0], mousePosition[1]-mouseOrigin[1])))

    def useWASD():
        global mousePosition
        event = keyboard.read_event()
        mousePos = list(mouse.position)

        if event.event_type == 'up':
            window.after(10, useWASD)
            return
        if event.name == 'esc':
            return
        if event.name == 'enter':
            return

        if event.name == 'w':
            mousePos[1]-=1
        elif event.name == 's':
            mousePos[1]+=1
        elif event.name == 'a':
            mousePos[0]-=1
        elif event.name == 'd':
            mousePos[0]+=1

        mouse.position = mousePos
        mousePosition = mouse.position
        useWASDLabel.config(text = 'Mouse Position:' + str((mousePosition[0]-mouseOrigin[0], mousePosition[1]-mouseOrigin[1])))
        window.after(10, useWASD)

    def setOrigin():
        global mouseOrigin
        mouseOrigin = mousePosition
        originLabel.config(text='Origin:' + str(mouseOrigin))
        useWASDLabel.config(text = 'Mouse Position:' + str((mousePosition[0]-mouseOrigin[0], mousePosition[1]-mouseOrigin[1])))

    def resetOrigin():
        global mouseOrigin
        mouseOrigin = (0, 0)
        originLabel.config(text='Origin:' + str(mouseOrigin))
        useWASDLabel.config(text = 'Mouse Position:' + str((mousePosition[0]-mouseOrigin[0], mousePosition[1]-mouseOrigin[1])))

    def setCustomEntryFields():
        global clickSpace
        global propertyProfiles
        if blueSpaceEntry.get() != '':
            blueSpace = blueSpaceEntry.get().split(',')
            propertyProfiles['Custom']['blueSpace'] = [int(blueSpace[0]), int(blueSpace[1])]
        if defaultOffsetEntry.get() != '':
            defaultOffset = defaultOffsetEntry.get().split(',')
            propertyProfiles['Custom']['defaultOffset'] = [int(defaultOffset[0]), int(defaultOffset[1])]
        if minSimilarityEntry.get() != '':
            minSimilarity = minSimilarityEntry.get()
            propertyProfiles['Custom']['minSimilarity'] = int(minSimilarity)
        if clickSpaceEntry.get() != '' and difficulty_var.get() == 'Custom':
            clickSpace = clickSpaceEntry.get().split(',')
        else:
            clickSpace = (1000, 700)

    def solveForColors():
        def addNewBlank():
            global mouse
            nonlocal blankColorsTkImage
            while True:
                event = keyboard.read_event()

                if event.event_type == 'up':
                    continue
                if event.name == 'esc':
                    return
                if event.name == 'enter':
                    break

            mousePosition = mouse.position
            mouse.position = (0, 0)
            blankColors.append(ImageGrab.grab((*mousePosition, mousePosition[0]+1, mousePosition[1]+1), all_screens=True).getpixel((0, 0)))

            blankColorsImage = Image.new('RGB', (32*len(blankColors), 32), (0, 0, 0))

            blankColorsDraw = ImageDraw.Draw(blankColorsImage)
            for i in range(len(blankColors)):
                blankColorsDraw.rectangle((i*32, 0, (i*32)+32, 32), fill=blankColors[i])

            blankColorsTkImage = ImageTk.PhotoImage(blankColorsImage)
            blanksLabel.config(image=blankColorsTkImage)
            blanksLabel.update()

        def clearAllBlanks():
            nonlocal blankColorsTkImage
            blankColors.clear()
            blankColorsImage = Image.new('RGB', (32, 32), (255, 255, 255))

            blankColorsTkImage = ImageTk.PhotoImage(blankColorsImage)
            blanksLabel.config(image=blankColorsTkImage)
            blanksLabel.update()
        
        def getPixelMatch(pixel, targetColor, similarity):
            minColor=[targetColor[0]-similarity, targetColor[1]-similarity, targetColor[2]-similarity] #sets the low end for the darkest that the color can be.
            maxColor=[targetColor[0]+similarity, targetColor[1]+similarity, targetColor[2]+similarity] #sets the high end for how light the color can be.
            pixelHigh=pixel[0] > minColor[0] and pixel[1] > minColor[1] and pixel[2] > minColor[2] #checks if the color is light enough for each rgb channel
            pixelLow=pixel[0] < maxColor[0] and pixel[1] < maxColor[1] and pixel[2] < maxColor[2] #checks if the color is dark enough for each rgb channel

            if pixelHigh and pixelLow: #if its not too light and not too dark, goldylocks eats the porridge
                return True
            return False
        
        def addNewNum():
            global mouse
            nonlocal bigNumberImage
            nonlocal numberTkImage

            while True:
                event = keyboard.read_event()

                if event.event_type == 'up':
                    continue
                if event.name == 'esc':
                    return
                if event.name == 'enter':
                    break
            
            pixelOnBoard = (mouse.position[0] - propertyProfiles['Custom']['originPoint'][0], mouse.position[1] - propertyProfiles['Custom']['originPoint'][1])
            alignedPixelOnBoard = ((pixelOnBoard[0] // propertyProfiles['Custom']['squareSize'])*propertyProfiles['Custom']['squareSize'], (pixelOnBoard[1] // propertyProfiles['Custom']['squareSize'])*propertyProfiles['Custom']['squareSize'])
            TLPixelOnScreen = (alignedPixelOnBoard[0] + propertyProfiles['Custom']['originPoint'][0], alignedPixelOnBoard[1] + propertyProfiles['Custom']['originPoint'][1])
            BRPixelOnScreen = (TLPixelOnScreen[0] + propertyProfiles['Custom']['squareSize'], TLPixelOnScreen[1] + propertyProfiles['Custom']['squareSize'])
            
            mouse.position = (0, 0)
            time.sleep(0.2)
            squareImage = ImageGrab.grab((*TLPixelOnScreen, *BRPixelOnScreen), all_screens=True)

            for i in range(propertyProfiles['Custom']['squareSize']):
                for j in range(propertyProfiles['Custom']['squareSize']):
                    for k in blankColors:
                        if getPixelMatch(squareImage.getpixel((j, i)), k, 30):
                            numberImage.putpixel((j, i), (0, 0, 0))

            for i in range(propertyProfiles['Custom']['squareSize']):
                for j in range(propertyProfiles['Custom']['squareSize']):
                    if ((i%2 == 0) ^ (j%2 == 0)) and numberImage.getpixel((j, i)) == (0, 0, 0):
                        numberImage.putpixel((j, i), (100, 100, 100))
            
            bigNumberImage = numberImage.resize((propertyProfiles['Custom']['squareSize']*4, propertyProfiles['Custom']['squareSize']*4), Image.Resampling.NEAREST)
            numberTkImage = ImageTk.PhotoImage(bigNumberImage)
            numberLabel.config(image=numberTkImage)
            numberLabel.update()

        def clearNumbers():
            nonlocal numberImage
            nonlocal bigNumberImage
            nonlocal numberTkImage

            numberImage = Image.new('RGB', (propertyProfiles['Custom']['squareSize'], propertyProfiles['Custom']['squareSize']), (255, 255, 255))
            bigNumberImage = numberImage.resize((propertyProfiles['Custom']['squareSize']*4, propertyProfiles['Custom']['squareSize']*4), Image.Resampling.NEAREST)
            numberTkImage = ImageTk.PhotoImage(bigNumberImage)
            numberLabel.config(image=numberTkImage)
            numberLabel.update()
        
        def highlightPixel():
            nonlocal bigNumberImage
            nonlocal numberTkImage

            markedNumberImage = numberImage.copy()
            markedNumberImage.putpixel((abs(int(XpixelEntry.get())), propertyProfiles['Custom']['squareSize']-(abs(int(YpixelEntry.get()))+1)), (255, 0, 0))
            bigNumberImage = markedNumberImage.resize((propertyProfiles['Custom']['squareSize']*4, propertyProfiles['Custom']['squareSize']*4), Image.Resampling.NEAREST)
            numberTkImage = ImageTk.PhotoImage(bigNumberImage)
            numberLabel.config(image=numberTkImage)
            numberLabel.update()
        
        def colorFinder():
            global propertyProfiles
            colorOrder = colorOrderInputEntry.get()
            colorDictionary = {'1':'cOne', '2':'cTwo', '3':'cThree', '4':'cFour', '5':'cFive', '6':'cSix', '7':'cSeven', 'g':'cGreen', 'f':'cFlag'}

            propertyProfiles['Custom']['defaultOffset'] = (abs(int(XpixelEntry.get())), -abs(int(YpixelEntry.get())))
            i = 0

            while True:
                event = keyboard.read_event()

                if event.event_type == 'up':
                    continue
                if event.name == 'esc':
                    return
                if event.name == 'enter':
                    pixelOnBoard = (mouse.position[0] - propertyProfiles['Custom']['originPoint'][0], mouse.position[1] - propertyProfiles['Custom']['originPoint'][1])
                    alignedPixelOnBoard = ((pixelOnBoard[0] // propertyProfiles['Custom']['squareSize'])*propertyProfiles['Custom']['squareSize'], (pixelOnBoard[1] // propertyProfiles['Custom']['squareSize'])*propertyProfiles['Custom']['squareSize'])
                    TLPixelOnScreen = (alignedPixelOnBoard[0] + propertyProfiles['Custom']['originPoint'][0], alignedPixelOnBoard[1] + propertyProfiles['Custom']['originPoint'][1])
                    BRPixelOnScreen = (TLPixelOnScreen[0] + propertyProfiles['Custom']['squareSize'], TLPixelOnScreen[1] + propertyProfiles['Custom']['squareSize'])

                    mouse.position = (0, 0)
                    time.sleep(0.2)
                    squareImage = ImageGrab.grab((*TLPixelOnScreen, *BRPixelOnScreen), all_screens=True)

                    color = squareImage.getpixel((abs(int(XpixelEntry.get())), propertyProfiles['Custom']['squareSize']-(abs(int(YpixelEntry.get()))+1)))
                    propertyProfiles['Custom'][colorDictionary[colorOrder[i]]] = color

                    if i >= len(colorOrder)-1:
                        colorOrderInputLabel.config(text='Order To Enter Numbers (ex. 1234fg)')
                        break
                    else:
                        i += 1
                        colorOrderInputLabel.config(text=colorOrder[i])
                        colorOrderInputLabel.update()

        def closeColorsWindow():
            colorsWindow.destroy()

        colorsWindow = tk.Toplevel(editCustomWindow)
        colorsWindow.title('Solve For Colors')

        blankColors = []
        blankColorsImage = Image.new('RGB', (32, 32), (255, 255, 255))
        blankColorsTkImage = ImageTk.PhotoImage(blankColorsImage)
        blanksLabel = ttk.Label(colorsWindow, image=blankColorsTkImage)
        blanksLabel.pack()

        addNewBlankButton = ttk.Button(colorsWindow, text='Add New Blank Color', command=addNewBlank)
        addNewBlankButton.pack(padx=80)
        clearBlanksButton = ttk.Button(colorsWindow, text='Clear All Blanks', command=clearAllBlanks)
        clearBlanksButton.pack()

        numberImage = Image.new('RGB', (propertyProfiles['Custom']['squareSize'], propertyProfiles['Custom']['squareSize']), (255, 255, 255))
        bigNumberImage = numberImage.resize((propertyProfiles['Custom']['squareSize']*4, propertyProfiles['Custom']['squareSize']*4), Image.Resampling.NEAREST)
        numberTkImage = ImageTk.PhotoImage(bigNumberImage)

        numberLabel = ttk.Label(colorsWindow, image=numberTkImage)
        numberLabel.pack()

        addNewNumButton = ttk.Button(colorsWindow, text='Add New Number', command=addNewNum)
        addNewNumButton.pack()
        clearNumButton = ttk.Button(colorsWindow, text='Clear Numbers', command=clearNumbers)
        clearNumButton.pack()

        XpixelLabel = ttk.Label(colorsWindow, text='X:')
        XpixelEntry = ttk.Entry(colorsWindow)
        YpixelLabel = ttk.Label(colorsWindow, text='Y:')
        YpixelEntry = ttk.Entry(colorsWindow)
        XpixelLabel.pack()
        XpixelEntry.pack()
        YpixelLabel.pack()
        YpixelEntry.pack()

        goToPixelButton = ttk.Button(colorsWindow, text='Highlight XY', command=highlightPixel)
        goToPixelButton.pack()

        colorOrderInputLabel = ttk.Label(colorsWindow, text='Order To Enter Numbers (ex. 1234fg)')
        colorOrderInputEntry = ttk.Entry(colorsWindow)
        colorFinderButton = ttk.Button(colorsWindow, text='Number Color Magic', command=colorFinder)
        colorOrderInputLabel.pack()
        colorOrderInputEntry.pack()
        colorFinderButton.pack()

        closeColorsWindowButton = ttk.Button(colorsWindow, text='Close', command=closeColorsWindow)
        closeColorsWindowButton.pack()

    def setCustomToMatch():
        global propertyProfiles
        propertyProfiles['Custom'] = propertyProfiles[setCustomDifficultyVar.get()]
    
    def closeEditCustomWindow():
        editCustomWindow.destroy()

    editCustomWindow = tk.Toplevel(window)
    editCustomWindow.title('Edit Custom Profile')

    # Entry for X and Y
    goToPixelFrame = tk.Frame(editCustomWindow, padx=20, pady=20)
    XmouseLabel = ttk.Label(goToPixelFrame, text='X:')
    XmouseEntry = ttk.Entry(goToPixelFrame)
    YmouseLabel = ttk.Label(goToPixelFrame, text='Y:')
    YmouseEntry = ttk.Entry(goToPixelFrame)
    goToPixelButton = ttk.Button(goToPixelFrame, text='Go To XY', command=goToPixel)
    XmouseLabel.pack()
    XmouseEntry.pack()
    YmouseLabel.pack()
    YmouseEntry.pack()
    goToPixelButton.pack()
    goToPixelFrame.grid(column=0, row=0)

    #Use wsad button
    useWASDFrame = tk.Frame(editCustomWindow, padx=20, pady=20)
    useWASDLabel = ttk.Label(useWASDFrame, text='Mouse Position:(0, 0)')
    useWASDButton = ttk.Button(useWASDFrame, text='Use WASD', command=useWASD)
    originLabel = ttk.Label(useWASDFrame, text='Origin:' + str(mouseOrigin))
    setOriginButton = ttk.Button(useWASDFrame, text='Set Origin', command=setOrigin)
    resetOriginButton = ttk.Button(useWASDFrame, text='Reset Origin', command=resetOrigin)
    useWASDLabel.pack()
    useWASDButton.pack()
    originLabel.pack()
    setOriginButton.pack()
    resetOriginButton.pack()
    useWASDFrame.grid(column=1, row=0)

    #blueSpace, defaultOffset, and minSimilarity fields
    customEntryFieldsFrame = tk.Frame(editCustomWindow, padx=20, pady=20)
    blueSpaceLabel = ttk.Label(customEntryFieldsFrame, text='Blue Space (850,500)')
    blueSpaceEntry = ttk.Entry(customEntryFieldsFrame)
    clickSpaceLabel = ttk.Label(customEntryFieldsFrame, text='Click Space (1000,700)')
    clickSpaceEntry = ttk.Entry(customEntryFieldsFrame)
    defaultOffsetLabel = ttk.Label(customEntryFieldsFrame, text='Default Offset (16,-21)')
    defaultOffsetEntry = ttk.Entry(customEntryFieldsFrame)
    minSimilarityLabel = ttk.Label(customEntryFieldsFrame, text='Minimum Similarity (10)')
    minSimilarityEntry = ttk.Entry(customEntryFieldsFrame)
    setCustomEntryFieldsButton = ttk.Button(customEntryFieldsFrame, text='Set To Custom', command=setCustomEntryFields)
    blueSpaceLabel.pack()
    blueSpaceEntry.pack()
    clickSpaceLabel.pack()
    clickSpaceEntry.pack()
    defaultOffsetLabel.pack()
    defaultOffsetEntry.pack()
    minSimilarityLabel.pack()
    minSimilarityEntry.pack()
    setCustomEntryFieldsButton.pack()
    customEntryFieldsFrame.grid(column=0, row=1)

    #Calibrate Button
    calibrateFrame = tk.Frame(editCustomWindow, padx=20, pady=20)
    calibrateButton = ttk.Button(calibrateFrame, text='Calibrate', command=calibrate)
    calibrateButton.pack()
    calibrationLabel = ttk.Label(calibrateFrame, text='', wraplength=calibrateFrame.winfo_width(), anchor='w', justify='left')
    calibrationLabel.pack(fill='x', expand=False)

    solveForColorsButton = ttk.Button(calibrateFrame, text='Solve For Colors', command=solveForColors)
    solveForColorsButton.pack()

    setCustomToMatchButton = ttk.Button(calibrateFrame, text='Set Custom To Match', command=setCustomToMatch)
    setCustomDifficultyVar = tk.StringVar()
    setCustomDifficultyLabel = ttk.Label(calibrateFrame, text="")
    setCustomDifficultyDropdown = ttk.OptionMenu(calibrateFrame, setCustomDifficultyVar, str(list(propertyProfiles.keys())[0]), *propertyProfiles.keys())

    setCustomDifficultyLabel.pack()
    setCustomDifficultyDropdown.pack()
    setCustomToMatchButton.pack()
    calibrateFrame.grid(column=1, row=1)

    closeEditCustomWindowButton = ttk.Button(editCustomWindow, text='Close', command=closeEditCustomWindow)
    closeEditCustomWindowButton.grid(column=0, row=2, columnspan=2, padx=20, pady=20)

def viewProfile():
    def fetchBoard():
        zoomed = False
        properties = propertyProfiles[difficulty_var.get()]
        ajustedDefaultOffset = (properties['defaultOffset'][0], properties['squareSize']+properties['defaultOffset'][1]-1)

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
        def getState(cord, screen):
            properties = propertyProfiles[difficulty_var.get()]
            ajustedDefaultOffset = (properties['defaultOffset'][0], properties['squareSize']+properties['defaultOffset'][1]-1)
            tempPixel=screen.getpixel((cord[0]*properties['squareSize']+ajustedDefaultOffset[0], cord[1]*properties['squareSize']+ajustedDefaultOffset[1]))

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

        def boardRetrieval():
            nonlocal boardTkImage
            nonlocal boardImage
            TL = (properties['originPoint'][0], properties['originPoint'][1]-properties['squareSize']+1)
            BR = (TL[0]+(properties['squareSize']*(properties['boardWidth'])), TL[1]+(properties['squareSize']*properties['boardHeight']))
            boardScreenshot = ImageGrab.grab((*TL, *BR), all_screens=True)
            boardImage = boardScreenshot.copy()

            editedBoardImage = ImageDraw.Draw(boardImage)

            for i in range(properties['boardHeight']):
                for j in range(properties['boardWidth']):
                    TL = (j*properties['squareSize'], i*properties['squareSize'])
                    BR = (TL[0]+properties['squareSize']-1, TL[1]+properties['squareSize']-1)
                    editedBoardImage.rectangle((*TL, *BR), outline=(255, 0, 0) if (i+j)%2==0 else (255, 255, 0))

                    editedBoardImage.text((TL[0]+(properties['squareSize']//2), TL[1]+(properties['squareSize']//2)), str(getState((j, i), boardScreenshot)), (0, 0, 0))

                    editedBoardImage.point((j*properties['squareSize']+ajustedDefaultOffset[0], i*properties['squareSize']+ajustedDefaultOffset[1]), (0, 0, 0))

            boardTkImage = ImageTk.PhotoImage(boardImage)
            boardImageLabel.config(image=boardTkImage)
            boardImageLabel.update()

        def zoom():
            nonlocal boardTkImage
            if zoomed:
                boardTkImage = ImageTk.PhotoImage(boardImage)
            else:
                boardTkImage = ImageTk.PhotoImage(boardImage.resize((boardImage.width*2, boardImage.height*2), Image.Resampling.NEAREST))
            boardImageLabel.config(image=boardTkImage)
            boardImageLabel.update()

        def closeShowBoardWindow():
            showBoardWindow.destroy()

        showBoardWindow = tk.Toplevel(profileViewerWindow)
        showBoardWindow.title('Show Board')

        boardImage = Image.new('RGB', (5, 5), (255, 255, 255))
        boardTkImage = ImageTk.PhotoImage(boardImage)
        boardImageLabel = ttk.Label(showBoardWindow, image=boardTkImage)
        boardImageLabel.pack()

        boardRetrieval()

        refreshBoardButton = ttk.Button(showBoardWindow, text='Refresh', command=boardRetrieval)
        refreshBoardButton.pack()

        zoomButton = ttk.Button(showBoardWindow, text='Zoom', command=zoom)
        zoomButton.pack()

        closeShowBoardWindowButton = ttk.Button(showBoardWindow, text='Close', command=closeShowBoardWindow)
        closeShowBoardWindowButton.pack(padx=80)

    def showProfile():
        properties = propertyProfiles[difficulty_var.get()]
        showProfileWindow = tk.Toplevel(profileViewerWindow)
        showProfileWindow.title('View Profile')
        originPointLabel = ttk.Label(showProfileWindow)
        boardWidthLabel = ttk.Label(showProfileWindow)
        boardHeightLabel = ttk.Label(showProfileWindow)
        squareSizeLabel = ttk.Label(showProfileWindow)
        defatultOffsetLabel = ttk.Label(showProfileWindow)
        blueSpaceLabel = ttk.Label(showProfileWindow)
        minSimilarityLabel = ttk.Label(showProfileWindow)
        originPointLabel.pack()
        boardWidthLabel.pack()
        boardHeightLabel.pack()
        squareSizeLabel.pack()
        defatultOffsetLabel.pack()
        blueSpaceLabel.pack()
        minSimilarityLabel.pack()

    def closeProfileViewerWindow():
        profileViewerWindow.destroy()

    profileViewerWindow = tk.Toplevel(window)
    profileViewerWindow.title('Show Profile')

    fetchBoardButton = ttk.Button(profileViewerWindow, text='View Board', command=fetchBoard)
    fetchBoardButton.pack()

    showProfileButton = ttk.Button(profileViewerWindow, text='Show Profile', command=showProfile)
    showProfileButton.pack()

    closeProfileViewerButton = ttk.Button(profileViewerWindow, text='Close', command=closeProfileViewerWindow)
    closeProfileViewerButton.pack(padx=80)

window = ThemedTk(theme='breeze')
window.title('Minesweeper Solver!')
window.iconphoto(True, tk.PhotoImage(file='logo.png'))

# Difficulty dropdown
difficultyFrame = ttk.Frame()
difficulty_var = tk.StringVar()
difficulty_label = ttk.Label(difficultyFrame, text="Select Difficulty:")
difficulty_dropdown = ttk.OptionMenu(difficultyFrame, difficulty_var, str(list(propertyProfiles.keys())[0]), *propertyProfiles.keys())
difficulty_label.pack()
difficulty_dropdown.pack()
editCustomButton = ttk.Button(difficultyFrame, text='Edit Custom', command=editCustom)
editCustomButton.pack()

showBoardButton = ttk.Button(difficultyFrame, text='View Profile', command=viewProfile)
showBoardButton.pack()
difficultyFrame.grid(column=0, row=0, padx=20, pady=20)

# Toggle for risky play
riskyPlayFrame = ttk.Frame(window)
risky_play_var = tk.BooleanVar()
repeatToggleVar = tk.BooleanVar()
repeatToggleCheckbox = ttk.Checkbutton(riskyPlayFrame, text='Repeat', variable=repeatToggleVar)
risky_play_checkbox = ttk.Checkbutton(riskyPlayFrame, text="Enable Risky Play", variable=risky_play_var)
risky_play_var.set(False)  # Default risky play disabled
repeatToggleVar.set(True)
risky_play_checkbox.pack()
repeatToggleCheckbox.pack()
riskyPlayFrame.grid(column=1, row=0, padx=20, pady=20)

startSolverFrame = ttk.Frame(window)
# Button to start solver
start_button = ttk.Button(startSolverFrame, text="Start Solver", command=onStart)
start_button.pack()

quitButton = ttk.Button(startSolverFrame, text='Quit', command=window.destroy)
quitButton.pack()
startSolverFrame.grid(row=1, column=0, columnspan=2, padx=20, pady=20)

window.mainloop()