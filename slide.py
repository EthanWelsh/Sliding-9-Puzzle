import numpy as np
import queue


class Board:
    def __init__(self, board, forward=True):
        self.board = board
        self.shape = self.board.shape
        self.path = []

        self.heuristic = self.forward_manhattan() if forward else self.backward_manhattan()

    @classmethod
    def from_file(cls, file_path):
        return Board(np.loadtxt(file_path, skiprows=1, dtype=bytes).astype(str))

    def children(self):
        blank_index = np.where(self.board == '0')
        blank_index = (blank_index[0][0], blank_index[1][0])

        height, width = self.shape
        moves = []

        for direction in ['n', 'e', 's', 'w']:
            r, c = self._adjust_index(blank_index, direction)
            if 0 <= r < height and 0 <= c < width:
                copy = np.copy(self.board)
                copy[blank_index] = copy[r, c]
                copy[r, c] = '0'

                copy_board = Board(copy)
                copy_board.path.extend(self.path + [direction])
                moves.append(copy_board)

        return moves

    @staticmethod
    def _adjust_index(position, direction):
        r, c = position

        r -= direction.count('n')
        r += direction.count('s')
        c += direction.count('e')
        c -= direction.count('w')

        return r, c

    @staticmethod
    def goal_board(size):
        height, width = size
        goal = np.full((height, width), dtype=str, fill_value='0')

        for r in range(height):
            for c in range(width):
                goal[r, c] = str(c + r * width + 1)

        goal[height - 1, width - 1] = '0'

        return goal

    def manhattan(self, template=None):
        height, width = self.shape
        distance = 0

        for r in range(height):
            for c in range(width):
                misplaced_index = (r, c)
                if self.board[r, c] != template.board[r, c]:
                    misplaced_index = np.where(self.board == str(template.board[r, c]))
                    misplaced_index = (misplaced_index[0][0], misplaced_index[1][0])

                miss_r, miss_c = misplaced_index
                distance += abs(r - int(miss_r)) + abs(c - int(miss_c))

        return distance

    def forward_manhattan(self, goal):
        return self.manhattan(goal)

    def backward_manhattan(self, start):
        return self.manhattan(start)

    def __str__(self):
        height, width = self.shape

        ret = ''
        for r in range(height):
            for c in range(width):
                if self.board[r, c] == '0':
                    ret += '  ' + ' '
                else:
                    if int(self.board[r, c]) < 10:
                        ret += ' '

                    ret += self.board[r, c] + ' '
            ret += '\n'
        return ret

    def __eq__(self, other):
        return np.array_equal(self.board, other.board)

    def __cmp__(self, other):
        if self.heuristic < other.heuristic:
            return -1
        elif self.heuristic > other.heuristic:
            return 1
        else:
            return 0

    def __lt__(self, other):
        return self.heuristic < other.heuristic

    def __hash__(self):
        return hash(str(self.board))


class Solver:
    def __init__(self, file_path):
        self.start = Board.from_file(file_path)
        self.goal = self.start.goal_board(self.start.shape)

        self.down_channel = queue.Queue()
        self.up_channel = queue.Queue()

    def is_goal(self, board):
        return np.array_equal(board.board, self.goal)

    def down(self):
        frontier = queue.PriorityQueue()
        frontier.put(self.start)
        up_boards = set()
        explored = set()

        while not frontier.empty():
            current = frontier.get()
            explored.add(current)

            if self.is_goal(current):
                return current

            while not self.up_channel.empty():
                up_boards.add(self.up_channel.get())

            if current in up_boards:
                for possible_goal in up_boards:
                    if np.array_equal(possible_goal.board, current.board):
                        return current, up_boards.remove(current)

            for child in current.children():
                if child not in explored:
                    frontier.put(child)
                    self.down_channel.put(child)

        return None

    def up(self):
        frontier = queue.PriorityQueue()
        frontier.put(self.start.goal_board(self.start.shape))
        down_boards = set()
        explored = set()

        while not frontier.empty():
            current = frontier.get()
            explored.add(current)

            if self.is_goal(current):
                return True

            while not self.down_channel.empty():
                down_boards.add(self.down_channel.get())

            if current in down_boards:
                for possible_goal in down_boards:
                    if np.array_equal(possible_goal.board, current.board):
                        return current, possible_goal

            if current in self.down_channel:
                return True

            for child in current.children():
                self.up_channel.put(child)
                frontier.put(child)

        return False


def main():
    s = Solver(file_path='puzzles/puzzle03.txt')
    s.up_channel.put(Board(s.start))
    print(s.up())


if __name__ == '__main__':
    main()
