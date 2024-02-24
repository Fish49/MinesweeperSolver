# MinesweeperSolver
MinesweeperSover is a clever python bot that can quickly solve Minesweeper!

!IMPORTANT! This code interacts with your mouse and captures the entire content of your screen multiple times a second. If you havent set your computer up corectly for the bot to run, and even sometimes if you have, it will click all over your computer and probably ruin something.

!IMPORTANT! At any point, hit ESC to stop the program. If you arent fast enough, it could mess with your computer and click all over the place. use this bot at your own risk.

So far ive only tested this bot on a 1920x1080 screen on Windows 11. chances are it wont work on any other screen size or OS, since it uses precise pixel coordinates to check the state of the screen and do the clicking.

To use it, you must go to https://www.google.com/fbx?fbx=minesweeper and set googles zoom size to 100%. you have to edit the code to reflect what difficulty you're using, at the top of Minesweeper4.py, there should be a variable called "difficulty" set this to the appropriate difficulty that you wish it to solve, 1=easy, 2=medium, 3=hard. If you dont give it the correct value, it wont work, and could even go berserk.

To run the code, you will need to install its dependancies, PIL, pynput, and keyboard. to do this, go to your python console and run each of the following commands:  
`pip install pillow`  
`pip install pynput`  
`pip install keyboard`  
This is not a guide on how to use pip, install python, or intall dependencies, if you need any extra help just check out https://packaging.python.org/en/latest/tutorials/installing-packages/

(Yes I know ive made the bot sound really scary but in theory, it shouldnt mess anything up. if it doesnt detect a minesweeper board, chances are it wont do any clicking. Just remember, in the event of an emergency, click ESC)
