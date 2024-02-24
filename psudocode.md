# How to solve Minesweeper:

We need to think of an algorithm that will flag spaces that it knows are bombs, and middle click spaces that have no un-flagged bomb neighbors. I developed the algoritm well be using for this project, but I acknowledge that others might've come up with the same idea independantly.

## Step 1: Flagging
We need to flag any square that we know is a bomb. Well if we look at just one square at a time, we know that *all* of its neighbors are bombs if it has the exact number of neighbers as the value of its number. Lets look at an example:

🟩🟩🟩
🟩4️⃣⬜
⬜⬜⬜
Here we can see that 4 is surrounded by exactly 4 green squares. since it must be touching 4 bombs, and its only touching 4 squares, we know that all 4 of its neighbors are bombs.

🟩🟥🟩
🟩4️⃣⬜
⬜⬜⬜
its important to note that one of its neighbors might already be flagged, so we need to check if the sum of the green neighbors *and* flagged neighbors equals the value of the number.

🟥🟥🟥
🟥4️⃣⬜
⬜⬜⬜
in either case, we can flag all of its neighbors like so. Its important to only right-click the green neighbors though to make sure we dont un-flag any already flagged neighbors.

lets look at a bigger example:

🟩🟩🟩🟩🟩🟩🟩🟩🟩
🟩🟩🟩🟩🟩🟩🟩🟩🟩
🟩⬜⬜⬜⬜1️⃣🟩🟩🟩
🟩1️⃣1️⃣⬜⬜1️⃣1️⃣1️⃣🟩
🟩🟩3️⃣1️⃣⬜⬜1️⃣1️⃣🟩
🟩🟩🟩2️⃣1️⃣1️⃣1️⃣🟩🟩
🟩2️⃣2️⃣2️⃣🟩1️⃣1️⃣🟩🟩
🟩⬜⬜1️⃣1️⃣1️⃣⬜⬜🟩
🟩🟩🟩🟩🟩🟩🟩🟩🟩

Run this algorithm for each space on this board and you will get this:
🟩🟩🟩🟩🟩🟩🟩🟩🟩
🟩🟩🟩🟩🟩🟩🟩🟩🟩
🟩⬜⬜⬜⬜1️⃣🟥🟩🟩
🟩1️⃣1️⃣⬜⬜1️⃣1️⃣1️⃣🟩
🟩🟥3️⃣1️⃣⬜⬜1️⃣1️⃣🟩
🟩🟥🟥2️⃣1️⃣1️⃣1️⃣🟥🟩
🟩2️⃣2️⃣2️⃣🟥1️⃣1️⃣🟩🟩
🟩⬜⬜1️⃣1️⃣1️⃣⬜⬜🟩
🟩🟩🟩🟩🟩🟩🟩🟩🟩

## Step 2: Clearing
Now we need to clear as much as possible to reveal more numbers and get more information. To avoid losing, we can only remove squares that we are certain are safe. Luckily, most versions of minesweeper have a built-in algorithm that will remove all safe squares. If you middle click on a number, and the number of neighboring flags is the same as the value of that number, it will clear all neighboring green squares. TL;DR if you flagged correctly, you can just middle click all the squares to clear as much as possible. To save time and not waste clicks, our code only middle clicks spaces that already meet the conditions to clear neighbors. Lets look at a quick example:

🟩🟩🟩
🟩1️⃣🟥
🟩🟩🟩

If you middle click the one, since its already touching its one bomb, it will clear every neighboring green:

⬜1️⃣1️⃣
⬜1️⃣🟥
⬜1️⃣1️⃣

## Step 3: Repeat
If we repeat these steps forever, we will always either win or get stuck (Yes it gets stuck very very often). Now we just have to make it click in the middle at the beginning and repeat these steps over and over again until we hopefully win.

## Implementation in Psudocode:
```
Until Win:
    Scan the board and record its contents to a list

    For every square on the board:
        If the square has the same number of filled neighbors as its number:
            For each of its green neighbors:
                right click

    For every square on the board:
        If the square has the same number of flagged neighbors as its number AND it has at least one green neighbor:
            middle click

    TODO: if there are no leads, guess. (I havent done this yet so its prone to getting stuck.)
```