import queue
from enum import IntEnum

import numpy as np
import threading

import sys


class Direction(IntEnum):
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3


DIRECTIONS = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]


class Board:
    def __init__(self, board, goal, path=None):
        if path is None:
            path = []

        self.board = board
        self.shape = self.board.shape
        self.path = path

        if goal is not None:
            self.heuristic = self.manhattan(goal) #+ len(self.path)
        else:
            self.heuristic = 0

    @classmethod
    def from_file(cls, file_path):
        return Board(board=np.loadtxt(file_path, skiprows=1, dtype=bytes).astype(np.uint8), goal=None)

    def children(self, goal):
        blank_index = np.where(self.board == 0)
        blank_index = (blank_index[0][0], blank_index[1][0])

        height, width = self.shape
        moves = []

        for direction in DIRECTIONS:
            r, c = self._adjust_index(blank_index, direction)

            if 0 <= r < height and 0 <= c < width:
                copy = np.copy(self.board)
                copy[blank_index] = copy[r, c]
                copy[r, c] = 0

                copy_board = Board(board=copy, goal=goal, path=self.path + [direction])
                moves.append(copy_board)

        return moves

    @staticmethod
    def _adjust_index(position, direction):
        r, c = position

        if direction == Direction.NORTH:
            r -= 1
        elif direction == Direction.SOUTH:
            r += 1
        elif direction == Direction.EAST:
            c += 1
        elif direction == Direction.WEST:
            c -= 1

        return r, c

    @staticmethod
    def goal_board(size):
        height, width = size
        goal = np.full((height, width), dtype=np.uint8, fill_value=0)

        for r in range(height):
            for c in range(width):
                goal[r, c] = c + r * width + 1

        goal[height - 1, width - 1] = 0

        return goal

    def manhattan(self, template):
        height, width = self.shape
        distance = 0

        for r in range(height):
            for c in range(width):
                misplaced_index = (r, c)
                if self.board[r, c] != template.board[r, c]:
                    misplaced_index = np.where(self.board == template.board[r, c])
                    misplaced_index = (misplaced_index[0][0], misplaced_index[1][0])

                miss_r, miss_c = misplaced_index
                distance += abs(r - int(miss_r)) + abs(c - int(miss_c))

        return distance

    def is_goal(self):
        return self.heuristic == 0

    def reverse_path(self):
        return [{Direction.NORTH: Direction.SOUTH,
                 Direction.EAST: Direction.WEST,
                 Direction.SOUTH: Direction.NORTH,
                 Direction.WEST: Direction.EAST}[direction]
                for direction in self.path]

    def __str__(self):
        height, width = self.shape

        ret = ''
        for r in range(height):
            for c in range(width):
                if self.board[r, c] == 0:
                    ret += '  ' + ' '
                else:
                    if self.board[r, c] < 10:
                        ret += ' '

                    ret += str(self.board[r, c]) + ' '
            ret += '\n'
        return ret

    def __lt__(self, other):
        return self.heuristic + len(self.path) < other.heuristic + len(self.path)

    def __eq__(self, other):
        return np.array_equal(self.board, other.board)

    def __hash__(self):
        return hash(str(self.board))


class Solver:
    def __init__(self, file_path):
        self.start = Board.from_file(file_path)
        self.goal = Board(self.start.goal_board(self.start.shape), self.start)
        self.start.heuristic = self.start.manhattan(self.goal)

        self.down_channel = queue.Queue()
        self.up_channel = queue.Queue()

    def down(self):
        frontier = queue.PriorityQueue()
        frontier.put(self.start)
        up_boards = set()
        explored = set()

        while not frontier.empty():
            current = frontier.get()
            explored.add(current)

            if current.is_goal():
                print('DOWN GOAL', current.path)
                return current

            while not self.down_channel.empty():
                up_boards.add(self.down_channel.get())

            if current in up_boards:

                best_score = sys.maxsize
                best_board = (None, None)

                for possible_goal in up_boards:
                    if np.array_equal(possible_goal.board, current.board):
                        total_path_cost = len(possible_goal.path) + len(current.path)

                        if total_path_cost < best_score:
                            best_score = total_path_cost
                            best_board = (current, possible_goal)

                ret = Board(self.goal, None)
                up_board, down_board = best_board
                ret.path = up_board.path + down_board.reverse_path()
                print('DOWN JOIN', ret.path)

                return ret

            for child in current.children(self.goal):
                if child not in explored:
                    frontier.put(child)
                    self.up_channel.put(child)

        return None

    def up(self):
        frontier = queue.PriorityQueue()
        frontier.put(self.goal)
        down_boards = set()
        explored = set()

        while not frontier.empty():
            current = frontier.get()
            explored.add(current)

            if current.is_goal():
                print('UP GOAL', current.path)
                return current

            while not self.up_channel.empty():
                down_boards.add(self.up_channel.get())

            if current in down_boards:

                best_score = sys.maxsize
                best_board = (None, None)

                for possible_goal in down_boards:
                    if np.array_equal(possible_goal.board, current.board):
                        total_path_cost = len(possible_goal.path) + len(current.path)

                        if total_path_cost < best_score:
                            best_score = total_path_cost
                            best_board = (possible_goal, current)

                ret = Board(self.goal, None)
                up_board, down_board = best_board
                ret.path = up_board.path + down_board.reverse_path()
                print('UP JOIN', ret.path)

                return ret
            for child in current.children(self.start):
                if child not in explored:
                    frontier.put(child)
                    self.down_channel.put(child)

        return None


def main():
    s = Solver(file_path='puzzles/puzzle06.txt')

    up = threading.Thread(target=s.up)
    down = threading.Thread(target=s.down)

    up.start()
    down.start()



if __name__ == '__main__':
    main()
