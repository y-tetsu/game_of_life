import time
from platform import system
from ctypes import windll
from random import random
from datetime import datetime
import json
import pprint

import numpy as np
import cv2


class GameOfLife:
    def __init__(self, sample=None, name='game_of_life', x=30, y=15,
                 world=None, max_step=None, wait=0.03, delay=0.0,
                 alive='■', ratio=0.5, loop=False, torus=False, mortal=False,
                 color=False, json_file=None):
        self.sample = sample
        self.name = name
        samples, colors = self._load_samples('samples.json'), None
        if sample in samples:
            self.name = sample
            if 'world' in samples[sample]:
                world = samples[sample]['world']
            if 'max_step' in samples[sample]:
                if max_step is None:
                    max_step = samples[sample]['max_step']
            if 'colors' in samples[sample]:
                colors = samples[sample]['colors']
            if 'wait' in samples[sample]:
                wait = samples[sample]['wait']

        self.x, self.y = x, y
        rand = False
        if world is not None:
            self.x, self.y = len(world[0]), len(world)
            self.world = [[x for x in row] for row in world]
        else:
            rand = True
            self.world = [
                [random() < ratio for _ in range(x)] for _ in range(y)
            ]

        self.max_step = max_step if max_step is not None else 100
        self.wait = wait
        self.delay = delay
        self.alive = alive
        self.ratio = ratio
        self.loop = loop
        self.torus = torus
        self.mortal = mortal
        self.color = color

        if json_file is not None:
            rand = False
            self._load(json_file)

        self.step = 1
        self.colors = [[0 for _ in row] for row in self.world]
        if colors:
            self.colors = colors

        self.alives = [('  ', 0), (self.alive, 10), ('□', 30), ('・', 60)]
        self.lifespans = [alive[1] for alive in self.alives]
        self.marks = [alive[0] for alive in self.alives]

        self.console = Console(self.x, self.y, self.name,
                               self.marks, self.color)

        if rand:
            self._dump()

        # numpy & open-cv
        self.world = np.array(self.world, dtype=np.uint8)
        self.ages = np.copy(self.world)
        self.colors = np.array(self.colors, dtype=np.uint8)
        self.kernel = np.array(
                [[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.uint8)

    def start(self):
        try:
            self.console.setup()
            while True:
                self.console.display(self.world, self.step, self.colors)
                if self.step == self.max_step:
                    if not self.loop:
                        # if loop option is enabled, game_of_life is never end.
                        break
                if self.step == 1:
                    time.sleep(self.delay)
                self._update()
                self._wait()
        except KeyboardInterrupt:
            return
        finally:
            self.console.teardown()

    def _load_samples(self, samples_file):
        samples = {}
        try:
            with open(samples_file, 'r') as f:
                samples = json.load(f)
        except FileNotFoundError:
            pass
        return samples

    def _load(self, json_file):
        try:
            with open(json_file, 'r') as f:
                settings = json.load(f)
                self.name = settings['name']
                self.x = settings['x']
                self.y = settings['y']
                self.world = settings['world']
                self.max_step = settings['step']
                self.wait = settings['wait']
                self.delay = settings['delay']
                self.alive = settings['alive']
                self.ratio = settings['ratio']
                self.loop = settings['loop']
                self.torus = settings['torus']
                self.mortal = settings['mortal']
                self.color = settings['color']
        except FileNotFoundError:
            pass

    def _update(self):
        torus, mortal = self.torus, self.mortal
        kernel = self.kernel

        now_world, now_colors = None, None
        if torus:
            now_world = np.pad(self.world, 1, 'wrap')
            now_colors = np.pad(self.colors, 1, 'wrap')
        else:
            now_world = np.copy(self.world)
            now_colors = np.copy(self.colors)

        ones = np.ones_like(now_world, dtype=np.uint8)
        now_alives = (now_world >= 1) * ones
        border_type = cv2.BORDER_ISOLATED
        count = cv2.filter2D(now_alives, -1, kernel, borderType=border_type)

        max_colors = cv2.dilate(now_colors, kernel, borderType=border_type)

        if torus:
            now_world = now_world[1:-1, 1:-1]
            now_colors = now_colors[1:-1, 1:-1]
            count = count[1:-1, 1:-1]
            max_colors = max_colors[1:-1, 1:-1]
            ones = ones[1:-1, 1:-1]
            now_alives = now_alives[1:-1, 1:-1]

        alive = (now_alives == 1) * ((count == 2) | (count == 3))
        born = (now_alives == 0) * (count == 3)
        all_cells = alive | born

        self.world = all_cells * ones
        self.colors = alive * now_colors + born * (max_colors + ones)

        if mortal:
            # ageing
            max_index = len(self.lifespans) - 1
            for index, lifespan in enumerate(reversed(self.lifespans)):
                ageing_cell = np.where(alive & (self.ages < lifespan))
                self.world[ageing_cell] = max_index - index
            self.ages[np.where(alive)] += 1
            self.ages[np.where(born)] = 1

            # check if expiring lifespan
            max_lifespan = self.lifespans[-1]
            self.world[np.where(self.ages >= max_lifespan)] = 0
            self.ages[np.where(self.world == 0)] = 0

        self.step += 1

    def _wait(self):
        time.sleep(self.wait)

    def _dump(self):
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        json_file = 'world' + now + '.json'
        settings = {
            'name': self.console.name,
            'x': self.x,
            'y': self.y,
            'world': self.world,
            'step': self.max_step,
            'wait': self.wait,
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
    def __init__(self, x, y, name, marks, color):
        self.x = x
        self.y = y
        self.name = name
        self.marks = marks
        if 'win' in system().lower():
            self._enable_win_escape_code()
        self.color_list = [
            '\033[39m',                # 0: default
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
        self.title = self._setup_title()

        self._get_world = self._get_uncolorized_world
        if color:
            self._get_world = self._get_colorized_world

    def setup(self):
        self._clear_screen()
        self._cursor_hyde()

    def teardown(self):
        self._cursor_show()

    def display(self, world, step, colors):
        cursor_up = ''
        if step > 1:
            cursor_up = self._cursor_up(self.y + 4)
        screen = cursor_up + self._get_title() + \
            self._get_world(world, colors) + self._get_step(step)
        print(screen, end='')

    def _enable_win_escape_code(self):
        kernel = windll.kernel32
        kernel.SetConsoleMode(kernel.GetStdHandle(-11), 7)

    def _clear_screen(self):
        print("\033[;H\033[2J")

    def _cursor_hyde(self):
        print('\033[?25l', end='')

    def _cursor_show(self):
        print('\033[?25h', end='')

    def _cursor_up(self, n):
        return f'\033[{n}A'

    def _setup_title(self):
        name, x, y = self.name, self.x, self.y
        count = x * y
        max_cell_size = 3250
        title = f'{name} ({x} x {y})'
        if count > max_cell_size:
            title += f' * warning : max_cell_size({max_cell_size}) is over! *'
        return title

    def _get_title(self):
        return f"{self.title}\n"

    def _get_uncolorized_world(self, world, _):
        marks = self.marks
        max_y, max_x = self.y, self.x
        line = []
        # setup screen for display world on cli
        screen = '┌' + ('─' * (max_x * 2)) + '┐\n'
        for y in range(max_y):
            cells = ''
            for x in range(max_x):
                cells += marks[world[y][x]]
            line += ['│' + cells + '│']
        screen += '\n'.join(line) + '\n'
        screen += '└' + ('─' * (max_x * 2)) + '┘\n'
        return screen

    def _get_colorized_world(self, world, colors):
        color_list = self.color_list
        marks = self.marks
        max_y, max_x = self.y, self.x
        max_color = len(color_list)
        line = []
        # setup screen for display world on cli
        screen = '┌' + ('─' * (max_x * 2)) + '┐\n'
        for y in range(max_y):
            cells, pre_color = '', 0
            for x in range(max_x):
                mark = marks[world[y][x]]
                if mark == '  ':
                    # if no mark, color must be not care
                    cells += mark
                else:
                    # change color if it is different from previous
                    if color := colors[y][x] % max_color:
                        if color == pre_color:
                            cells += mark
                        else:
                            cells += color_list[color] + mark
                    else:
                        if pre_color:
                            cells += color_list[0] + mark
                        else:
                            cells += mark
                    pre_color = color
            if pre_color:
                line += ['│' + cells + color_list[0] + '│']
            else:
                line += ['│' + cells + '│']
        screen += '\n'.join(line) + '\n'
        screen += '└' + ('─' * (max_x * 2)) + '┘\n'
        return screen

    def _get_step(self, step):
        return f'step = {step}\n'


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
                description='A game of life simulator on CLI')

    # requied arg
    parser.add_argument('sample', nargs='?')
    # requied optional text arg
    options = (('-n', '--name'), ('-j', '--json'), ('-a', '--alive'))
    for option in options:
        parser.add_argument(*option)
    # requied optional int arg
    options = (('-x',), ('-y',), ('-s', '--step'))
    for option in options:
        parser.add_argument(*option, type=int)
    # requied optional float arg
    options = (('-w', '--wait'), ('-d', '--delay'), ('-r', '--ratio'))
    for option in options:
        parser.add_argument(*option, type=float)
    # optional flag
    options = (
        ('-l', '--loop'), ('-t', '--torus'), ('-m', '--mortal'),
        ('-c', '--color'))
    for option in options:
        parser.add_argument(*option, action="store_true")
    args = parser.parse_args()

    setting = {}
    # set args if defined
    options = (
        ('sample', args.sample), ('name', args.name), ('x', args.x),
        ('y', args.y), ('json_file', args.json), ('max_step', args.step),
        ('delay', args.delay), ('alive', args.alive), ('ratio', args.ratio))
    for key, value in options:
        if value:
            setting[key] = value
    # set args if not None
    if args.wait is not None:
        setting['wait'] = args.wait
    # set args
    options = (
        ('loop', args.loop), ('torus', args.torus), ('mortal', args.mortal),
        ('color', args.color))
    for key, value in options:
        setting[key] = value

    GameOfLife(**setting).start()
