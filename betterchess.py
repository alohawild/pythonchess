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
__version__ = "0.0.5"
__credits__ = ["Michael Wild"]
__maintainer__ = "Michael Wild"
__email__ = "alohawild@mac.com"
__status__ = "Initial"


import chess.svg
import random
import sys
import xml.etree.cElementTree as ET
from xml.dom import minidom

# ######################## shared ##############################

# Put shared functions here

# ######################## Classes ##############################


class MoveList:
    """
    This is a helper class for working with chess items.
    """
    chess_list = [  'P',
                    'N',
                    'B',
                    'R',
                    'Q'
                    'K']

    #  These below are adjustable values for calculating value of moves
    CHESS_BOARD_VALUE = [0, 0, 1, 1, 1, 1, 0, 0,
                         0, 2, 2, 2, 2, 2, 2, 0,
                         1, 2, 3, 3, 3, 3, 2, 1,
                         1, 2, 3, 4, 4, 3, 2, 1,
                         1, 2, 3, 4, 4, 3, 2, 1,
                         1, 2, 3, 3, 3, 3, 2, 1,
                         0, 2, 2, 2, 2, 2, 2, 0,
                         0, 0, 1, 1, 1, 1, 0, 0,
                         ]

    CHESS_BOARD_KING = [4, 4, 3, 3, 3, 3, 4, 4,
                        4, 2, 2, 2, 2, 2, 2, 4,
                        3, 2, 1, 1, 1, 1, 2, 3,
                        3, 2, 1, 0, 0, 1, 2, 3,
                        3, 2, 1, 0, 0, 1, 2, 3,
                        3, 2, 1, 1, 1, 1, 2, 3,
                        4, 2, 2, 2, 2, 2, 2, 4,
                        4, 4, 3, 3, 3, 3, 4, 4,
                        ]

    CHESS_POINTS = [0, 1, 3, 3, 5, 9, 100]  # None, "p", "n", "b", "r", "q", "k"

    RISK_FACTOR = -1.0  # Loss of piece value
    BOARD_FACTOR = 1.0  # Place on board value
    PIECE_FACTOR = 1.0  # Value of pieces for exchange
    BOARD_KING = 1.0  # Place on board value for King move
    SUPPORT_FACTOR = 1.0  # Value of interlocking support
    HOLD_FACTOR = 0.5  # Value of hold attack loss

    def __init__(self, my_file_name="goodvalues.xml"):
        """
        Start up and try to load starting values
        :param my_file_name: xml file that contains value
        """

        xml_doc = minidom.parse(my_file_name)

        self.RISK_FACTOR = int(xml_doc.getElementsByTagName('RISK_FACTOR')[0].attributes['name'].value) / 10000.0
        self.BOARD_FACTOR = int(xml_doc.getElementsByTagName('BOARD_FACTOR')[0].attributes['name'].value) / 10000.0
        self.BOARD_KING = int(xml_doc.getElementsByTagName('BOARD_KING')[0].attributes['name'].value) / 10000.0
        self.PIECE_FACTOR = int(xml_doc.getElementsByTagName('PIECE_FACTOR')[0].attributes['name'].value) / 10000.0
        self.SUPPORT_FACTOR = int(xml_doc.getElementsByTagName('SUPPORT_FACTOR')[0].attributes['name'].value) / 10000.0
        self.HOLD_FACTOR = int(xml_doc.getElementsByTagName('HOLD_FACTOR')[0].attributes['name'].value) / 10000.0

        return

    @staticmethod
    def print_board(my_board):
        """
        Just print board with a bit more display
        :param my_board:
        :return: None
        """

        print(" ")
        print("a b c d e f g h")
        print("---------------")
        print(board)
        print("---------------")
        print("a b c d e f g h")
        print(" ")

        return

    @staticmethod
    def list_legal(my_board):
        """
        Get a list of legal moves and UCI descriptions
        :param my_board:
        :return: list of legal moves and list of UCI of same
        """

        my_list = list(my_board.legal_moves)
        my_uci = [my_board.uci(a_move) for a_move in my_list]

        return my_list, my_uci

    def list_piece_move(self, my_board):
        """
        Break out all of the valid moves values
        :param my_board: Current board
        :return: list of moves with values broken into a list:
                    move [piece, color, from_square, to_square, is_attack, uci]
        """
        my_list = []
        for a_move in list(my_board.legal_moves):
            my_list.append([a_move, self.eval_move(a_move, my_board)])

        return my_list

    def eval_move(self, my_move, my_board):
        """
        This routine breaks apart a move and then evaluates it.
        It looks one move ahead to determine positive and negative
        actions. It does not do a min-max just a few checks.
        :param my_move: the legal move to be evaluated
        :param my_board: the board that the move is for
        :return: a list of all the values calculated or extracted
        """
        assert my_move in my_board.legal_moves

        from_square = my_move.from_square
        to_square = my_move.to_square
        our_piece = my_board.piece_at(from_square)
        to_piece = my_board.piece_at(to_square)
        the_uci = my_board.uci(my_move)
        attack = True
        if to_piece is None:
            attack = False
        game_over, our_risk = self.check_risk(my_board, my_move)

        our_hold, our_support = self.check_hold(my_board, my_move)

        # Calculate value of move
        our_move_calc = our_hold + our_support
        # Force movement to favor the center, unless the King
        if our_piece.symbol == "k":
            our_move_calc = (self.CHESS_BOARD_KING[to_square] * self.BOARD_FACTOR) + our_move_calc
        else:
            our_move_calc = (self.CHESS_BOARD_VALUE[to_square] * self.BOARD_FACTOR) + our_move_calc
        if attack:
            our_move_calc = (self.CHESS_POINTS[to_piece.piece_type] * self.PIECE_FACTOR) + our_move_calc
            if our_risk:
                our_move_calc = our_move_calc - (self.CHESS_POINTS[our_piece.piece_type] * self.PIECE_FACTOR)
        else:
            if our_risk:
                our_move_calc = (self.CHESS_POINTS[our_piece.piece_type] * self.RISK_FACTOR) + our_move_calc

        if game_over:
            our_move_calc = 1000.0

        #  send back a list
        return [our_piece, our_piece.color, from_square, to_square, to_piece, attack,
                the_uci, game_over, our_risk, our_move_calc, our_hold, our_support]


    @staticmethod
    def best_from_list(my_list):
        """
        Get the best move using calculation value.
        On tie supply last pawn move.
        :param my_list: List of moves fully evaluated from above
        :return:
        """
        my_move = None
        score = -999999.99
        for row in my_list:
            a_move = row[0]
            the_break_down = row[1]
            piece = the_break_down[0]
            calc = the_break_down[9]
            if calc > score:
                score = calc
                my_move = a_move
            elif calc == score and piece.symbol == "p":  # On a tie select pawns
                score = calc
                my_move = a_move

        # This should never happen
        assert (my_move is not None)

        return my_move, score


    @staticmethod
    def check_risk(my_board, my_move, verbose=False):
        """
        Take a move, create a new board, apply it, check what happens
        :param my_board: board to use
        :param my_move: move to appy
        :param verbose: trace or not
        :return: gameover and if attacked boolean values
        """
        try_board = my_board.copy(stack=False)
        try_board.push(my_move)

        if verbose:
            print("Move: ", my_move)
            print(try_board)

        our_risk = False
        for a_move in list(try_board.legal_moves):
            #  if there are any moves to the square we are moving to
            #  then it is at risk move
            if a_move.to_square == my_move.to_square:
                our_risk = True
                break

        if verbose:
            print("Game over: ", try_board.is_game_over())
            print("Risk: ", our_risk)

        return try_board.is_game_over(), our_risk

    def check_hold(self, my_board, my_move, verbose=False):
        """
        Calculate the number of supporting pieces after move.
        and calculate if no move and if piece can be lost
        :param my_board: the current board
        :param my_move: proposed move
        :param verbose: tracing value
        :return: hold value and support value
        """
        calc_hold = 0.0
        calc_support = 0.0

        # Remove anything that was where the piece is going and
        # Count how many can move there
        try_board = my_board.copy(stack=False)
        try_board.remove_piece_at(my_move.to_square)
        my_support = -1
        for a_move in list(try_board.legal_moves):
            if my_move.to_square == a_move.to_square:
                my_support = my_support + 1

        # Now put a enemy pawn there and see if the count is better
        # Pawns will now attack the pawn
        # This could create a crazy problem and have no moves...
        # But that is unlikely and would have no move so it should be OK
        if try_board.turn == chess.WHITE:
            try_piece = chess.Piece(chess.PAWN, chess.BLACK)
        else:
            try_piece = chess.Piece(chess.PAWN, chess.WHITE)
        try_board.set_piece_at(my_move.to_square, try_piece)
        my_support_better = -1
        for a_move in list(try_board.legal_moves):
            if my_move.to_square == a_move.to_square:
                my_support_better = my_support_better + 1

        if my_support > my_support_better:
            calc_support = my_support
        else:
            calc_support = my_support_better

        # Now move and then put the pieces back so
        # that the count of attacks can be measured
        # ignore the piece that was taken, if any, as it is not part of the calc
        try_board = my_board.copy(stack=False)
        try_board.push(my_move)
        try_piece = try_board.piece_at(my_move.to_square)
        try_board.remove_piece_at(my_move.to_square)
        try_board.set_piece_at(my_move.from_square, try_piece)

        my_hold = False
        for a_move in list(try_board.legal_moves):
            if my_move.from_square == a_move.to_square:
                my_hold = True
                break
        if my_hold:
            calc_hold = (self.CHESS_POINTS[try_piece.piece_type] * self.PIECE_FACTOR)

        calc_support = calc_support * self.SUPPORT_FACTOR
        calc_hold = calc_hold * self.HOLD_FACTOR

        if verbose:
            print("Move: ", my_move)
            print("Hold:", calc_hold)
            print("Support:", calc_support)

        return calc_hold, calc_support

    @staticmethod
    def print_legal(my_board, my_moves):
        """
        Print out evaluated move list
        :param my_board: board in play
        :param my_moves: moves fully evaluated from above
        :return: None.
        """

        for the_move in my_moves:
            the_break_down = the_move[1]
            uci = the_break_down[6]
            risk = the_break_down[8]
            attack = the_break_down[5]
            piece = the_break_down[0]
            win = the_break_down[7]
            attacked = the_break_down[4]
            calc = the_break_down[9]
            print(piece, uci, "Calc:", calc)
            if win:
                print("----->End of Game Move")
            if attack:
                print("----->Take Piece: ", attacked)
            if risk:
                print("----->Threatened")
        return

    def save_values(self, my_file_name="goodvalues.xml"):
        """
        Copy truncated to int values for chess calculations to xml file
        :param my_file_name: file name string
        :return: N/A
        """

        root = ET.Element("chess")
        #doc = ET.SubElement(root, "values")
        string_value = str(int(10000 * self.RISK_FACTOR))
        ET.SubElement(root, "RISK_FACTOR", name=string_value).text = "Rick Factor"
        string_value = str(int(10000 * self.BOARD_FACTOR))
        ET.SubElement(root, "BOARD_FACTOR", name=string_value).text = "Board Factor"
        string_value = str(int(10000 * self.BOARD_KING))
        ET.SubElement(root, "BOARD_KING", name=string_value).text = "Board King"
        string_value = str(int(10000 * self.PIECE_FACTOR))
        ET.SubElement(root, "PIECE_FACTOR", name=string_value).text = "Piece Factor"
        string_value = str(int(10000 * self.SUPPORT_FACTOR))
        ET.SubElement(root, "SUPPORT_FACTOR", name=string_value).text = "Support Factor"
        string_value = str(int(10000 * self.HOLD_FACTOR))
        ET.SubElement(root, "HOLD_FACTOR", name=string_value).text = "HOLD Factor"

        tree = ET.ElementTree(root)
        tree.write(my_file_name)

        return

# =============================================================
# Main program begins here


if __name__ == "__main__":

    print("Program: betterchess")
    print("Version ", __version__, " ", __copyright__, " ", __license__)
    print("Running on ", sys.version)
    print("Chess version: ", chess.__version__)

    chess.STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    board = chess.Board()
    file_name = "goodvalues.xml"
    moving = MoveList(file_name)
    get_random = True
    quit_game = False

    while True:
        if board.is_game_over():
            print("Game over")
            break
        if quit_game:
            break
        if get_random:
            random_legal = random.choice(list(board.legal_moves))
            print("My random move is ", random_legal)
        else:
            the_moves = moving.list_piece_move(board)
            random_legal, move_value = moving.best_from_list(the_moves)
            print("My calculated move is ", random_legal, " Calc:", move_value)

        board.push(random_legal)
        print("Board is now...")
        moving.print_board(board)

        if board.is_game_over():
            print("Game over")
            break
        else:
            while True:
                if board.is_check():
                    print("Check!")
                the_moves = moving.list_piece_move(board)
                moving.print_legal(board, the_moves)

                print("Enter your move:")
                print(" ")
                your_move = input("? (quit to end)")

                if your_move == "quit":
                    quit_game = True
                    break
                if len(your_move) < 4:
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
                    moving.print_board(board)
                    break
                else:
                    print("Move not valid: ", your_move)
        get_random = False

    # Save values to XML file
    moving.save_values(file_name)

    print(board)
    print(" ")
    print(" ... End of Line.")
