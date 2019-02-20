#!/usr/bin/env python
"""
    Copyright 2018 by Michael Wild (alohawild)
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
        http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
==============================================================================

"""
__author__ = 'michaelwild'
__copyright__ = "Copyright (C) 2018 Michael Wild"
__license__ = "Apache License, Version 2.0"
__version__ = "0.0.3"
__credits__ = ["Michael Wild"]
__maintainer__ = "Michael Wild"
__email__ = "alohawild@mac.com"
__status__ = "Initial"


import chess.pgn
import chess.svg
from secrets import randbelow
import sys

# ######################## shared ##############################


def random_move(my_board):

    """
    Generate a random move from the available legal moves.
    There is no iterator nor means to directly reference legal moves so
    we do it this that I have found--this works.
    Returns null move if no legal move
    Generates an exception if no moves are legal

    :param my_board: the current instance of the board game
    :return: one random move from possible legal moves in uci
    """
    my_move = chess.Move.null()

    # Get legal moves and select a random value
    my_number = my_board.legal_moves.count()
    if my_number < 1:
        raise Exception('No valid move for random move')

    my_random_move = randbelow(my_number)

    # Now as we have no cool Pythonic means just loop until values match
    move_number = 0
    my_move = chess.Move.null()
    for a_move in my_board.legal_moves:
        if my_random_move == move_number:
            my_move = a_move
            break
        move_number = move_number + 1

    return my_move

def uci_legal(my_board):
    """
    Creates a list of legal moves.
    Returns null list if no moves.
    :param my_board: the current instance of the board game
    :return: list of UCI legal moves.
    """

    my_uci = []
    for a_move in board.legal_moves:
        my_uci.append(board.uci(a_move))

    return my_uci

# =============================================================
# Main program begins here

if __name__ == "__main__":

    print("Program: newchess")
    print("Version ", __version__, " ", __copyright__, " ", __license__)
    print("Running on ", sys.version)
    print("Chess version: ", chess.__version__)

    chess.STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    board = chess.Board()
    print("Starting Board")
    print(board)

    while True:
        if board.is_game_over():
            print("Game Over!")
            break
        if board.is_check():
            print("Check!")

        random_legal = chess.Move.null()
        random_legal = random_move(board)
        print("My move is ", random_legal)
        board.push(random_legal)
        print("Board is now...")
        print(board)

        if board.is_game_over():
            print("Game over")
            break
        else:
            while True:
                if board.is_check():
                    print("Check!")
                legal_moves = uci_legal(board)
                print(legal_moves)
                your_move = chess.Move.null()
                print("Enter your move:")
                print(" ")
                your_move = input("? (quit to end)")

                if your_move == "quit":
                    sys.exit(0)
                if len(your_move) <4:
                    print("Invalid entry")
                    continue

                try:
                    move = chess.Move.from_uci(your_move)
                except:
                    print("Entry not valid: ", your_move)
                    continue

                if move in board.legal_moves:
                    board.push(move)
                    print("Board is now...")
                    print(board)
                    break
                else:
                    print("Move not valid: ", your_move)

    print(board)
    print(" ")
    print(" ... End of Line.")