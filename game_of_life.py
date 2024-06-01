import time
from platform import system
from ctypes import windll
from random import random
from datetime import datetime
import json
import pprint


class GameOfLife:
    def __init__(self, sample=None, name='game_of_life', x=30, y=15,
                 world=None, max_step=None, wait_time=0.05, delay=0.0,
                 alive='■', ratio=0.5, loop=False, torus=False, mortal=False,
                 color=False, json_file=None):
        self.sample = sample
        self.name = name
        self.x = x
        self.y = y
        rand = False
        samples = self.load_samples('samples.json')
        colors = None
        if sample in samples:
            self.name = sample
            if 'world' in samples[sample]:
                world = samples[sample]['world']
            if 'max_step' in samples[sample]:
                if max_step is None:
                    max_step = samples[sample]['max_step']
            if 'colors' in samples[sample]:
                colors = samples[sample]['colors']
        if world is not None:
            self.x = len(world[0])
            self.y = len(world)
            self.world = [[x for x in row] for row in world]
        else:
            rand = True
            self.world = [[1 if random() < ratio else 0 for _ in range(x)]
                          for _ in range(y)]
        self.max_step = max_step if max_step is not None else 100
        self.wait_time = wait_time
        self.delay = delay
        self.alive = alive
        self.ratio = ratio
        self.loop = loop
        self.torus = torus
        self.mortal = mortal
        self.color = color

        if json_file is not None:
            rand = False
            self.load(json_file)

        self.dirs = [
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1),
        ]
        self.step = 1
        self.ages = [[x for x in row] for row in self.world]
        self.colors = [[0 for _ in row] for row in self.world]
        if colors:
            self.colors = colors

        self.alives = (('  ', 0), (self.alive, 10), ('□', 30), ('・', 60))
        self.lifespans = [alive[1] for alive in self.alives]
        self.marks = [alive[0] for alive in self.alives]

        self.console = Console(self.x, self.y, self.name, self.marks)

        if rand:
            self.dump()

    def load_samples(self, samples_file):
        samples = {}
        try:
            with open(samples_file, 'r') as f:
                samples = json.load(f)
        except FileNotFoundError:
            pass
        return samples

    def load(self, json_file):
        try:
            with open(json_file, 'r') as f:
                settings = json.load(f)
                self.name = settings['name']
                self.x = settings['x']
                self.y = settings['y']
                self.world = settings['world']
                self.max_step = settings['step']
                self.wait_time = settings['wait']
                self.delay = settings['delay']
                self.alive = settings['alive']
                self.ratio = settings['ratio']
                self.loop = settings['loop']
                self.torus = settings['torus']
                self.mortal = settings['mortal']
                self.color = settings['color']
        except FileNotFoundError:
            pass

    def start(self):
        try:
            self.console.setup()
            while True:
                self.console.display(self.world, self.step,
                                     self.colors)
                if not self.loop and self.step == self.max_step:
                    break
                if self.step == 1:
                    time.sleep(self.delay)
                self.update()
                self.wait()
        except KeyboardInterrupt:
            return
        finally:
            self.console.teardown()

    def update(self):
        new_world = []
        for y in range(self.y):
            new_cells = []
            for x in range(self.x):
                new_cell = self.new_cell(x, y)
                if new_cell:
                    if self.mortal:
                        if self.world[y][x]:
                            # ageing
                            self.ages[y][x] += 1
                            for index, lifespan in enumerate(self.lifespans):
                                if self.ages[y][x] < lifespan:
                                    new_cell = index
                                    break
                            else:
                                self.ages[y][x] = 0
                                new_cell = 0
                        else:
                            self.ages[y][x] = 1
                else:
                    self.ages[y][x] = 0
                    self.colors[y][x] = 0
                new_cells += [new_cell]
            new_world += [new_cells]
        self.world = [[x for x in row] for row in new_world]
        self.step += 1

    def new_cell(self, x, y):
        alive, color = self.count_alive(x, y)
        if self.world[y][x]:
            return 1 if alive == 2 or alive == 3 else 0
        if alive == 3:
            if self.color:
                self.colors[y][x] = color + 1
            return 1
        return 0

    def count_alive(self, x, y):
        alive, color = 0, 0
        for dx, dy in self.dirs:
            next_x, next_y = x + dx, y + dy
            if self.torus:
                next_x %= self.x
                next_y %= self.y
            if (0 <= next_x < self.x) and (0 <= next_y < self.y):
                color = max(color, self.colors[next_y][next_x])
                if self.world[next_y][next_x]:
                    alive += 1
        return alive, color

    def wait(self):
        time.sleep(self.wait_time)

    def dump(self):
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        json_file = 'world' + now + '.json'
        settings = {
            'name': self.console.name,
            'x': self.x,
            'y': self.y,
            'world': self.world,
            'step': self.max_step,
            'wait': self.wait_time,
            'delay': self.delay,
            'alive': self.alive,
            'ratio': self.ratio,
            'loop': self.loop,
            'torus': self.torus,
            'mortal': self.mortal,
            'color': self.color,
        }
        with open(json_file, 'w') as f:
            output = pprint.pformat(settings, indent=4,
                                    width=1000, sort_dicts=False)
            output = output.replace("'", '"')
            output = output.replace('True', 'true')
            output = output.replace('False', 'false')
            f.write(output)


class Console:
    def __init__(self, x, y, name, marks):
        self.x = x
        self.y = y
        self.name = name
        self.marks = marks
        if 'win' in system().lower():
            self.enable_win_escape_code()
        self.color_list = [
            '\x1b[39m',                # 0: default
            '\033[38;2;255;255;255m',  # 1: white
            '\033[38;2;0;153;68m',     # 2: green
            '\033[38;2;230;0;18m',     # 3: red
            '\033[38;2;235;202;27m',   # 4: yellow
            '\033[38;2;145;0;0m',      # 5: brown
            '\033[38;2;0;160;233m',    # 6: cyan
            '\033[38;2;241;158;194m',  # 7: pink
            '\033[38;2;240;131;0m',    # 8: orange
            '\033[38;2;146;7;131m',    # 9: purple
        ]

    def enable_win_escape_code(self):
        kernel = windll.kernel32
        kernel.SetConsoleMode(kernel.GetStdHandle(-11), 7)

    def setup(self):
        self.clear_screen()
        self.cursor_hyde()

    def teardown(self):
        self.cursor_show()

    def clear_screen(self):
        print("\033[;H\033[2J")

    def cursor_hyde(self):
        print('\033[?25l', end='')

    def cursor_show(self):
        print('\033[?25h', end='')

    def cursor_up(self, n):
        print(f'\033[{n}A', end='')

    def display(self, world, step, colors):
        if step > 1:
            self.cursor_up(self.y + 4)
        self.display_title()
        self.display_world(world, colors)
        self.display_step(step)

    def display_title(self):
        print(f'{self.name} ({self.x} x {self.y})')

    def display_world(self, world, colors):
        print('┌' + '─' * (self.x * 2) + '┐')
        line = []
        for y in range(self.y):
            cells = ''
            for x in range(self.x):
                color = colors[y][x] % len(self.color_list)
                mark = self.marks[world[y][x]]
                cells += self.color_list[color] + mark + self.color_list[0]
            line += ['│' + cells + '│']
        print('\n'.join(line))
        print('└' + '─' * (self.x * 2) + '┘')

    def display_step(self, step):
        print(f'step = {step}')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
                description='A game of life simulator on CLI')
    parser.add_argument('sample', nargs='?')
    parser.add_argument('-n', '--name')
    parser.add_argument('-x', type=int)
    parser.add_argument('-y', type=int)
    parser.add_argument('-j', '--json')
    parser.add_argument('-s', '--step', type=int)
    parser.add_argument('-w', '--wait', type=float)
    parser.add_argument('-d', '--delay', type=float)
    parser.add_argument('-a', '--alive')
    parser.add_argument('-r', '--ratio', type=float)
    parser.add_argument('-l', '--loop', action="store_true")
    parser.add_argument('-t', '--torus', action="store_true")
    parser.add_argument('-m', '--mortal', action="store_true")
    parser.add_argument('-c', '--color', action="store_true")
    args = parser.parse_args()

    setting = {}
    if args.sample:
        setting['sample'] = args.sample
    if args.name:
        setting['name'] = args.name
    if args.x:
        setting['x'] = args.x
    if args.y:
        setting['y'] = args.y
    if args.json:
        setting['json_file'] = args.json
    if args.step:
        setting['max_step'] = args.step
    if args.wait:
        setting['wait_time'] = args.wait
    if args.delay:
        setting['delay'] = args.delay
    if args.alive:
        setting['alive'] = args.alive
    if args.ratio:
        setting['ratio'] = args.ratio
    setting['loop'] = args.loop
    setting['torus'] = args.torus
    setting['mortal'] = args.mortal
    setting['color'] = args.color

    GameOfLife(**setting).start()
