import queue
import threading
from enum import IntEnum

import numpy as np


class Direction(IntEnum):
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3

    def __str__(self):
        return {Direction.NORTH: 'N',
                Direction.SOUTH: 'S',
                Direction.EAST: 'E',
                Direction.WEST: 'W'}[self.value]


DIRECTIONS = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]


class Board:
    def __init__(self, board, goal, path=None):
        if path is None:
            path = []

        self.board = board
        self.shape = self.board.shape
        self.path = path

        if goal is not None:
            self.heuristic = self.manhattan(goal)
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

        # Create channels for communicating between the boards
        self.down_channel = queue.Queue()
        self.up_channel = queue.Queue()

        # Give each channel its end state
        self.down_channel.put(self.goal)
        self.up_channel.put(self.start)

        self.up_path = None
        self.down_path = None

    def down(self):
        frontier = queue.PriorityQueue()
        frontier.put(self.start)

        explored = set()

        # set for storing boards from the other thread that come in via the channel
        other_boards = set()

        while not frontier.empty():
            current = frontier.get()
            explored.add(current)
            self.up_channel.put(current)

            for child in current.children(self.goal):
                if child not in explored:
                    print(child.path)
                    frontier.put(child)

            while not self.down_channel.empty():
                other_boards.add(self.down_channel.get())

            # ghetto set intersection
            match_boards = explored - (explored - other_boards)

            if len(match_boards) > 0:
                # TODO return the min path len match
                print(list(match_boards)[0])
                print(list(match_boards)[0].path)
                print()

                self.down_path = list(match_boards)[0].path
                return self.down_path

        return None

    def up(self):
        frontier = queue.PriorityQueue()
        frontier.put(self.goal)

        other_boards = set()
        explored = set()

        while not frontier.empty():
            current = frontier.get()
            explored.add(current)
            self.down_channel.put(current)

            for child in current.children(self.start):
                if child not in explored:
                    frontier.put(child)

            while not self.up_channel.empty():
                other_boards.add(self.up_channel.get())

            match_boards = explored - (explored - other_boards)

            if len(match_boards) > 0:
                self.up_path = list(match_boards)[0].reverse_path()
                self.up_path = list(reversed(self.up_path))
                return self.up_path

        return None


def main():
    for i in range(4, 5):
        s = Solver(file_path='puzzles/puzzle{0:02d}.txt'.format(i))

        up = threading.Thread(target=s.up)
        down = threading.Thread(target=s.down)

        up.start()
        down.start()

        down.join()
        up.join()

        print('{}: {}\t {}|{}'.format(i, len(s.up_path) + len(s.down_path),
                                      ''.join([str(d) for d in s.down_path]),
                                      ''.join([str(d) for d in s.up_path])))
        print()


if __name__ == '__main__':
    main()
