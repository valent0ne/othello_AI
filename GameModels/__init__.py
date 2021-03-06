import numpy as np
import copy as cp
import logging

# initial othello board
initial_board = [['-', '-', '-', '-', '-', '-', '-', '-'],
                 ['-', '-', '-', '-', '-', '-', '-', '-'],
                 ['-', '-', '-', '-', '-', '-', '-', '-'],
                 ['-', '-', '-', 'k', 'w', '-', '-', '-'],
                 ['-', '-', '-', 'w', 'k', '-', '-', '-'],
                 ['-', '-', '-', '-', '-', '-', '-', '-'],
                 ['-', '-', '-', '-', '-', '-', '-', '-'],
                 ['-', '-', '-', '-', '-', '-', '-', '-']]


class Game:

    def __init__(self, initial_state=None, heuristic=None):
        self.state = initial_state
        self.heuristic = heuristic

    def neighbors(self, state, turn):
        out = set([])
        return out

    def get_state(self):
        return self.state

    def solution(self, state):
        return True


class OthelloRepresentation:
    def __init__(self):
        self.board = np.array(cp.deepcopy(initial_board))

    # given a position, returns the board in that position
    def get_disc(self, x, y):
        return self.board[x][y]

    # given a position, set the disc in that position
    def set_disc(self, x, y, disc):
        self.board[x][y] = disc

    # check whether a position is empty
    def is_empty(self, x, y):
        return self.board[x][y] == '-'

    @staticmethod
    def get_enemy_color(my_color):
        if my_color == 'k':
            return 'w'
        else:
            return 'k'


class OthelloState:
    # a state contains the representation (board) and the heuristic
    def __init__(self, h):
        self.heuristic = h
        self.representation = OthelloRepresentation()

    # redefine equal for the states obj
    def __eq__(self, other):
        return str(self.representation.board) == str(other.representation.board)

    # redefine not equal for the state obj
    def __ne__(self, other):
        return str(self.representation.board) != str(other.representation.board)

    # redefine hash for state obj
    def __hash__(self):
        return hash(str(self.representation.board))

    # wrapper
    def get_disc(self, x, y):
        return self.representation.get_disc(x, y)

    # wrapper
    def set_disc(self, x, y, disc):
        self.representation.set_disc(x, y, disc)

    # wrapper
    def is_empty(self, x, y):
        return self.representation.is_empty(x, y)

    # check whether the state is final
    def is_final(self):
        num_black_discs = 0
        num_white_discs = 0
        for i in range(8):
            for j in range(8):
                if self.representation.get_disc(i, j) == "-":
                    return None
                elif self.representation.get_disc(i, j) == 'k':
                    num_black_discs += 1
                else:
                    num_white_discs += 1
        if num_black_discs > num_white_discs:
            return "k"
        elif num_black_discs < num_white_discs:
            return "w"
        else:
            return "e"

    # returns a set of affected disc after the new disc of color "my_color" is positioned in position x, y
    def get_affected_discs(self, x, y, my_color):
        total_affected_discs = set([])
        logging.debug("get_affected_discs: coordinates = [{},{}], player = {}".format(x, y, my_color))
        if self.representation.is_empty(x, y):

            set_affected_row = set([])
            set_affected_col = set([])
            set_affected_fdiag = set([])
            set_affected_sdiag = set([])

            row_previous, row_next = self.get_nearest_discs_row(x, y, my_color)
            col_above, col_under = self.get_nearest_discs_col(x, y, my_color)
            fdiag_previous, fdiag_next = self.get_nearest_discs_first_diag(x, y, my_color)
            sdiag_previous, sdiag_next = self.get_nearest_discs_second_diag(x, y, my_color)

            if row_previous is not None:
                set_affected_row |= self.get_affected_row(x, y, row_previous[1], my_color)
            if row_next is not None:
                set_affected_row |= self.get_affected_row(x, y, row_next[1], my_color)
            if col_above is not None:
                set_affected_col |= self.get_affected_col(x, y, col_above[0], my_color)
            if col_under is not None:
                set_affected_col |= self.get_affected_col(x, y, col_under[0], my_color)
            if fdiag_previous is not None:
                set_affected_fdiag |= self.get_affected_first_diag(x, y, fdiag_previous[0], fdiag_previous[1], my_color)
            if fdiag_next is not None:
                set_affected_fdiag |= self.get_affected_first_diag(x, y, fdiag_next[0], fdiag_next[1], my_color)
            if sdiag_previous is not None:
                set_affected_sdiag |= self.get_affected_second_diag(x, y, sdiag_previous[0], sdiag_previous[1], my_color)
            if sdiag_next is not None:
                set_affected_sdiag |= self.get_affected_second_diag(x, y, sdiag_next[0], sdiag_next[1], my_color)

            # logging.debug("get_affected_discs: len of affected discs in row {} = {}".format(x, len(set_affected_row)))
            # logging.debug("get_affected_discs: len of affected discs in col {} = {}".format(y, len(set_affected_col)))
            # logging.debug("get_affected_discs: len of affected discs in first diag. = {}".format(len(set_affected_fdiag)))
            # logging.debug("get_affected_discs: len of affected discs in second diag. = {}".format(len(set_affected_sdiag)))

            total_affected_discs = set_affected_row | set_affected_col | set_affected_fdiag | set_affected_sdiag

        logging.debug("get_affected_discs: total # of affected discs: {}".format(len(total_affected_discs)))
        logging.debug("get_affected_discs: ---------------------------------------------\n")
        return total_affected_discs

    # returns the affected enemy discs (of row x) if the player would place a disc of color = my_color in position x,y
    def get_affected_row(self, x, y, y1, my_color):
        out_previous = set([])
        out_next = set([])
        enemy_color = self.representation.get_enemy_color(my_color)
        if y1 > y:
            j = y
            while j < y1:
                j += 1
                if self.representation.get_disc(x, j) == enemy_color:
                    out_next.add((x, j))
                elif self.representation.get_disc(x, j) == '-':
                    out_next.clear()
                    break
        elif y1 < y:
            j = y
            while j > y1:
                j -= 1
                if self.representation.get_disc(x, j) == enemy_color:
                    out_previous.add((x, j))
                elif self.representation.get_disc(x, j) == '-':
                    out_previous.clear()
                    break
        return out_next | out_previous

    # returns the affected enemy discs (column y) if the player would place a disc of color = my_color in position x, y
    def get_affected_col(self, x, y, x1, my_color):
        out_above = set([])
        out_under = set([])
        enemy_color = self.representation.get_enemy_color(my_color)
        if x1 > x:
            i = x
            while i < x1:
                i += 1
                if self.representation.get_disc(i, y) == enemy_color:
                    out_under.add((i, y))
                elif self.representation.get_disc(i, y) == '-':
                    out_under.clear()
                    break
        elif x1 < x:
            i = x
            while i > x1:
                i -= 1
                if self.representation.get_disc(i, y) == enemy_color:
                    out_above.add((i, y))
                elif self.representation.get_disc(i, y) == '-':
                    out_above.clear()
                    break
        return out_above | out_under

    # as above but in the first diag.: top-left -> bottom-right
    def get_affected_first_diag(self, x, y, x1, y1, my_color):
        out_previous = set([])
        out_next = set([])
        enemy_color = self.representation.get_enemy_color(my_color)
        if x > x1 and y > y1:
            i = x
            j = y
            while i > x1 and j > y1:
                i -= 1
                j -= 1
                if self.representation.get_disc(i, j) == enemy_color:
                    out_previous.add((i, j))
                elif self.representation.get_disc(i, j) == '-':
                    out_previous.clear()
                    break
        elif x < x1 and y < y1:
            i = x
            j = y
            while i < x1 and j < y1:
                i += 1
                j += 1
                if self.representation.get_disc(i, j) == enemy_color:
                    out_next.add((i, j))
                elif self.representation.get_disc(i, j) == '-':
                    out_next.clear()
                    break
        return out_next | out_previous

    # as above but in the first diag.: top-right -> bottom-left
    def get_affected_second_diag(self, x, y, x1, y1, my_color):
        out_previous = set([])
        out_next = set([])
        enemy_color = self.representation.get_enemy_color(my_color)
        if x > x1 and y < y1:
            i = x
            j = y
            while i > x1 and j < y1:
                i -= 1
                j += 1
                if self.representation.get_disc(i, j) == enemy_color:
                    out_previous.add((i, j))
                elif self.representation.get_disc(i, j) == '-':
                    out_previous.clear()
                    break
        elif x < x1 and y > y1:
            i = x
            j = y
            while i < x1 and j > y1:
                i += 1
                j -= 1
                if self.representation.get_disc(i, j) == enemy_color:
                    out_next.add((i, j))
                elif self.representation.get_disc(i, j) == '-':
                    out_next.clear()
                    break
        return out_next | out_previous

    # given a position returns the nearest disc of the same color in the row
    def get_nearest_discs_row(self, x, y, color):
        next_d = None
        previous = None
        j = y
        while j > 0:
            j -= 1
            if self.representation.get_disc(x, j) == color:
                previous = (x, j)
                break
        j = y
        while j < 7:
            j += 1
            if self.representation.get_disc(x, j) == color:
                next_d = (x, j)
                break
        return previous, next_d

    # given a position returns the nearest disc of the same color in the col
    def get_nearest_discs_col(self, x, y, color):
        above = None
        under = None
        i = x
        while i > 0:
            i -= 1
            if self.representation.get_disc(i, y) == color:
                above = (i, y)
                break
        i = x
        while i < 7:
            i += 1
            if self.representation.get_disc(i, y) == color:
                under = (i, y)
                break
        return above, under

    # given a position returns the nearest disc of the same color in the first diag
    # first diag means the one that goes from top-left to bottom-right
    def get_nearest_discs_first_diag(self, x, y, color):
        previous = None
        next_d = None
        # checking 1st semi-diagonal (from x,y to top-left)
        i = x
        j = y
        while i > 0 and j > 0:
            i -= 1
            j -= 1
            if self.representation.get_disc(i, j) == color:
                previous = (i, j)
                break
        # checking 2nd semi-diagonal (from x,y to bottom-right)
        i = x
        j = y
        while i < 7 and j < 7:
            i += 1
            j += 1
            if self.representation.get_disc(i, j) == color:
                next_d = (i, j)
                break
        return previous, next_d

    # given a position returns the nearest disc of the same color in the second diag
    # second diag means the one that goes from top-right to bottom-left
    def get_nearest_discs_second_diag(self, x, y, color):
        previous = None
        next_d = None
        # checking 1st semi-diagonal (from x,y to top-right)
        i = x
        j = y
        while i > 0 and j < 7:
            i -= 1
            j += 1
            if self.representation.get_disc(i, j) == color:
                next_d = (i, j)
                break
        # checking 2nd semi-diagonal (from x,y to bottom-left)
        i = x
        j = y
        while i < 7 and j > 0:
            i += 1
            j -= 1
            if self.representation.get_disc(i, j) == color:
                previous = (i, j)
                break
        return previous, next_d


class OthelloGame(Game):

    def __init__(self, h):
        self.state = OthelloState(h)

    # place a disc at coordinates x,j and reverse the affected enemy discs accordingly
    @staticmethod
    def make_move(state, x, y, my_color, coordinates):
        out = cp.deepcopy(state)
        # for every affected disc, change it to my color
        if len(coordinates) > 0:
            out.set_disc(x, y, my_color)
            for pos in coordinates:
                out.set_disc(pos[0], pos[1], my_color)
                logging.debug("make_move: changed color of disc in pos ({}, {}) to {}\n".format(pos[0], pos[1], my_color))
        return out

    # computes the neighbors of the given state
    def neighbors(self, turn, ext_state=None):
        if ext_state is None:
            state = cp.deepcopy(self.state)
        else:
            state = cp.deepcopy(ext_state)
        logging.debug("neighbors: copied state =\n {}".format(state.representation.board))
        out = set([state])
        for i in range(8):
            for j in range(8):
                if state.representation.get_disc(i, j) == '-':
                    affected_discs = state.get_affected_discs(i, j, turn)
                    if len(affected_discs) > 0:
                        logging.debug("neighbors: state = \n {}".format(state.representation.board))
                        new_state = self.make_move(state, i, j, turn, affected_discs)
                        logging.debug("neighbors: new_state =\n {}".format(new_state.representation.board))
                        out.add(new_state)
        logging.debug("neighbours: discovered {} neighbours".format(len(out)))
        return out
