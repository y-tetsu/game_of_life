import os
import time
from platform import system
from ctypes import windll
from random import randint


DEAD = 0
ALIVE = 1

SAMPLES = {
    'glider': {
        'world': [
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        'max_step': 40,
    },
    'galaxy': {
        'world': [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        'max_step': 45,
    },
}


class GameOfLife:
    def __init__(self, title='game_of_life', x=30, y=15, world=None,
                 max_step=100, wait_time=0.05, life='■'):
        self.x = x
        self.y = y
        if title in SAMPLES:
            world = SAMPLES[title]['world']
            max_step = SAMPLES[title]['max_step']
        if world is not None:
            self.x = len(world[0])
            self.y = len(world)
            self.world = [[x for x in row] for row in world]
        else:
            self.world = [[randint(0, 1) for _ in range(x)] for _ in range(y)]
        self.max_step = max_step
        self.wait_time = wait_time
        self.dirs = [
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1),
        ]
        self.step = 1
        self.console = Console(self.x, self.y, title, life)

    def start(self):
        try:
            self.console.setup()
            for _ in range(self.max_step):
                self.console.display(self.world, self.step)
                self.update()
                self.wait()
        except KeyboardInterrupt:
            return
        finally:
            self.console.teardown()

    def update(self):
        next_state = [[x for x in row] for row in self.world]
        for y, row in enumerate(self.world):
            for x, cell in enumerate(row):
                alive = 0
                for dx, dy in self.dirs:
                    next_x, next_y = x + dx, y + dy
                    if (0 <= next_x < self.x) and (0 <= next_y < self.y):
                        if self.world[next_y][next_x] == ALIVE:
                            alive += 1
                if cell:
                    next_cell = ALIVE if alive == 2 or alive == 3 else DEAD
                else:
                    next_cell = ALIVE if alive == 3 else DEAD
                next_state[y][x] = next_cell
        self.world = [[x for x in row] for row in next_state]
        self.step += 1

    def wait(self):
        time.sleep(self.wait_time)


class Console:
    def __init__(self, x, y, title, life):
        self.x = x
        self.y = y
        self.title = title
        self.life = life
        if 'win' in system().lower():
            self.enable_win_escape_sequence()

    def enable_win_escape_sequence(self):
        kernel = windll.kernel32
        kernel.SetConsoleMode(kernel.GetStdHandle(-11), 7)

    def setup(self):
        self.cls()
        self.cursor_hyde()

    def teardown(self):
        self.cursor_show()

    def cls(self):
        os.system('cls')

    def cursor_hyde(self):
        print('\033[?25l', end='')

    def cursor_show(self):
        print('\033[?25h', end='')

    def cursor_up(self, n):
        print(f'\033[{n}A', end='')

    def display(self, world, step):
        if step > 1:
            self.cursor_up(self.y + 4)
        self.display_title()
        self.display_world(world)
        self.display_step(step)

    def display_title(self):
        print(f'{self.title} ({self.x} x {self.y})')

    def display_world(self, world):
        print('┌' + '─' * (self.x * 2) + '┐')
        line = []
        for y in range(self.y):
            cells = ''.join([self.life if i else '  ' for i in world[y]])
            line.append('│' + cells + '│')
        print('\n'.join(line))
        print('└' + '─' * (self.x * 2) + '┘')

    def display_step(self, step):
        print(f'step = {step}')


if __name__ == '__main__':
    import sys
    argv = sys.argv
    if len(argv) == 2 and argv[1] in SAMPLES:
        GameOfLife(title=argv[1]).start()
    elif len(argv) == 3 and int(argv[1]) > 0 and int(argv[2]) > 0:
        GameOfLife(x=int(argv[1]), y=int(argv[2])).start()
    else:
        GameOfLife().start()
