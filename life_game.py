import os
import time
from platform import system
from ctypes import windll
from random import randint


class LifeGame:
    def __init__(self, x=10, y=10, state=None, title='Life Game', step=45):
        self.y = y
        self.x = x
        if state:
            self.y = len(state)
            self.x = len(state[0])
            self.state = [[x for x in row] for row in state]
        else:
            self.state = [[randint(0, 1) for _ in range(x)] for _ in range(y)]
        self.title = title
        self.step = step
        self.dirs = [
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1),
        ]
        self.count = 1
        if 'win' in system().lower():
            kernel = windll.kernel32
            kernel.SetConsoleMode(kernel.GetStdHandle(-11), 7)
        os.system('cls')

    def show(self):
        ret = []
        if self.count != 1:
            print(f'\033[{self.y+4}A', end='')
        print(f'{self.title} ({self.x} x {self.y})')
        print('┌' + '─' * (self.x * 2) + '┐')
        for y in range(self.y):
            cells = ''.join(['■' if i else '  ' for i in self.state[y]])
            ret.append('│' + cells + '│')
        print('\n'.join(ret))
        print('└' + '─' * (self.x * 2) + '┘')
        print(f'step = {self.count}')

    def update(self):
        next_state = [[x for x in row] for row in self.state]
        for y, row in enumerate(self.state):
            for x, cell in enumerate(row):
                alive = 0
                for dx, dy in self.dirs:
                    next_x, next_y = x + dx, y + dy
                    if (0 <= next_x < self.x) and (0 <= next_y < self.y):
                        if self.state[next_y][next_x]:
                            alive += 1
                if cell:
                    next_cell = 1 if alive == 2 or alive == 3 else 0
                else:
                    next_cell = 1 if alive == 3 else 0
                next_state[y][x] = next_cell
        self.state = [[x for x in row] for row in next_state]
        self.count += 1

    def start(self):
        for _ in range(self.step):
            self.show()
            time.sleep(0.08)
            self.update()


if __name__ == '__main__':
    # state = [
    #     [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # ]
    # LifeGame(state=state, title='グライダー', step=43).start()
    LifeGame().start()
