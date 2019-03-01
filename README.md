# Python Chess programs
This is my repo for python chess programs. I am using the chess python libraries and python 3.7.
## Chess Library
I am using the chess library that is supported from here [Chess](https://github.com/niklasf/python-chess).
## newchess.py
The newchess.py uses random selection over legal moves. Because of this it gets "smarter"
as the number of pieces shrink. It handles check well as the legal moves limits its choices.
It plays a very odd game with it seemly resisting you but seldom taking your pieces.
## betterchess.py
The betterchess.py measures the value of moves by various factors and creates a value for a move. It picks the 
"best" move it in the list. The code looks forward about one move to check its settings. It also tries to cost not
moving a piece. There is no exchange tree logic. Just looking at the board and playing various moves one step ahead.
The first move is always random. This simulates an opening book, poorly but still better than always playing the same.
