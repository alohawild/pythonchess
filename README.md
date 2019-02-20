# Python Chess programs
This is my repo for python chess programs. I am using the chess python libraries and python 3.7.
## Chess Library
I am using the chess library that is supported from here [Chess](https://github.com/niklasf/python-chess).
## newchess.py
The newchess.py uses random selection over legal moves. Because of this it gets "smarter"
as the number of pieces shrink. It handles check well as the legal moves limits its choices.
It plays a very odd game with it seemly resisting you but seldom taking your pieces.
### Issues
I was unable to use an iterator or even an array on legal moves so I built some sub routines for that. 
In the next program I will likely use a helper class and start building objects to help.
This is likely the final version of this code as I am moving on with a new file for more interesting changes.
