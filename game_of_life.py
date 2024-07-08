import time
from platform import system
from ctypes import windll
from random import random, randrange
from datetime import datetime
import json
import pprint

import numpy as np
import cv2


# for lineprofiler
try:
    profile
except NameError:
    # dummy for no profile
    def profile(func):
        return func


class GameOfLife:
    def __init__(self, sample=None, name='game_of_life', x=30, y=15,
                 world=None, max_step=None, wait=0.03, delay=0.0,
                 alive='■', ratio=0.5, loop=False, torus=False, mortal=False,
                 rand=False,
                 color=False, color2=False, color3=False, json_file=None):
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
        random_cells = False
        if world is not None:
            self.x, self.y = len(world[0]), len(world)
            self.world = [[x for x in row] for row in world]
        else:
            random_cells = True
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
        self.random = rand
        self.color = color
        self.color2 = color2
        self.color3 = color3

        if json_file is not None:
            random_cells = False
            self._load(json_file)

        self.step = 1
        self.colors = [[0 for _ in row] for row in self.world]
        if colors:
            self.colors = colors

        self.alives = [('　', 0), (self.alive, 10), ('□', 30), ('・', 60)]
        self.lifespans = [alive[1] for alive in self.alives]
        self.marks = [''] + [alive[0] for alive in self.alives]

        color_type = None
        if color:
            color_type = 'vitamin'
        elif color2:
            color_type = 'pastel'
        elif color3:
            color_type = 'thermography'
        self.console = Console(self.x, self.y, self.name,
                               self.marks, color_type, self.random)

        if random_cells:
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
            self.console.display(self.world, self.step, self.colors)
            time.sleep(self.delay)
            while True:
                if self.step == self.max_step:
                    if not self.loop:
                        # if loop option is enabled, game_of_life is never end.
                        break
                self._update()
                self._wait()
                self.console.update(self.diff_world, self.step, self.colors)
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
                self.random = settings['random']
                self.color = settings['color']
                self.color2 = settings['color2']
                self.color3 = settings['color3']
        except FileNotFoundError:
            pass

    def _update(self):
        # get previous
        pre_world = np.copy(self.world)
        ones = np.ones_like(pre_world, dtype=np.uint8)
        pre_cells = (pre_world >= 1) * ones
        pre_colors = np.copy(self.colors)

        if self.torus:
            # wrap around
            pre_cells = np.pad(pre_cells, 1, 'wrap')
            pre_colors = np.pad(pre_colors, 1, 'wrap')

        # get alive and born
        kernel = self.kernel
        border_type = cv2.BORDER_ISOLATED
        around_cells = cv2.filter2D(pre_cells, -1,
                                    kernel, borderType=border_type)
        max_colors = cv2.dilate(pre_colors, kernel, borderType=border_type)

        if self.torus:
            # remove around
            pre_cells = pre_cells[1:-1, 1:-1]
            pre_colors = pre_colors[1:-1, 1:-1]
            around_cells = around_cells[1:-1, 1:-1]
            max_colors = max_colors[1:-1, 1:-1]

        alive = (pre_cells == 1) * ((around_cells == 2) | (around_cells == 3))
        born = (pre_cells == 0) * (around_cells == 3)

        # update next cells
        next_cells = alive | born
        self.world = next_cells * ones
        self.colors = alive * pre_colors + born * (max_colors + ones)

        if self.mortal:
            # aging
            max_index = len(self.lifespans) - 1
            for index, lifespan in enumerate(reversed(self.lifespans)):
                aging_cells = np.where(alive & (self.ages < lifespan))
                self.world[aging_cells] = max_index - index
            self.ages[np.where(next_cells)] += 1

            # check if expiring lifespan
            max_lifespan = self.lifespans[-1]
            self.world[np.where(self.ages >= max_lifespan)] = 0
            self.ages[np.where(self.world == 0)] = 0

        # erase same cells
        self.diff_world = self.world + ones
        self.diff_world[np.where(self.world == pre_world)] = 0

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
            'random': self.random,
            'color': self.color,
            'color2': self.color2,
            'color3': self.color3,
        }
        with open(json_file, 'w') as f:
            output = pprint.pformat(settings, indent=4,
                                    width=1000, sort_dicts=False)
            output = output.replace("'", '"')
            output = output.replace('True', 'true')
            output = output.replace('False', 'false')
            f.write(output)


class Console:
    def __init__(self, x, y, name, marks, color_type, random):
        self.x = x
        self.y = y
        self.name = name
        self.marks = marks
        self.random = random
        if 'win' in system().lower():
            self._enable_win_escape_code()
        if color_type == 'vitamin':
            self.color_list = [
                '\033[39m',                # 0: default
                '\033[38;2;255;255;255m',  # 1: white
                '\033[38;2;0;170;85m',     # 2: green
                '\033[38;2;238;0;68m',     # 3: red
                '\033[38;2;255;238;85m',   # 4: yellow
                '\033[38;2;85;00;00m',     # 5: brown
                '\033[38;2;0;170;238m',    # 6: cyan
                '\033[38;2;238;136;187m',  # 7: pink
                '\033[38;2;255;170;51m',   # 8: orange
                '\033[38;2;136;0;119m',    # 9: purple
            ]
        elif color_type == 'pastel':
            self.color_list = [
                '\033[39m',                # 0: default
                '\033[38;2;255;255;255m',  # 1: white
                '\033[38;2;168;255;211m',  # 2: green
                '\033[38;2;255;168;211m',  # 3: red
                '\033[38;2;255;255;168m',  # 4: yellow
                '\033[38;2;255;168;168m',  # 5: brown
                '\033[38;2;168;255;255m',  # 6: cyan
                '\033[38;2;255;168;255m',  # 7: pink
                '\033[38;2;255;211;168m',  # 8: orange
                '\033[38;2;211;168;255m',  # 9: purple
            ]
        elif color_type == 'thermography':
            self.color_list = [
                '\033[38;2;254;252;238m',  # 1:
                '\033[38;2;255;240;130m',  # 2:
                '\033[38;2;254;199;2m',    # 3:
                '\033[38;2;244;105;2m',    # 4:
                '\033[38;2;223;47;75m',    # 5:
                '\033[38;2;223;47;75m',    # 5:
                '\033[38;2;178;1;148m',    # 6:
                '\033[38;2;178;1;148m',    # 6:
                '\033[38;2;105;1;158m',    # 7:
                '\033[38;2;105;1;158m',    # 7:
                '\033[38;2;16;1;121m',     # 8:
                '\033[38;2;16;1;121m',     # 8:
            ]
        self.title = self._setup_title()

        self._get_world = self._get_world_mono
        self.update = self._update_mono
        if color_type is not None:
            self._get_world = self._get_world_color
            self.update = self._update_color
            self.max_col = 18 if self.x * self.y > 3000 else 50
            if y < self.max_col:
                self.max_col = y
        else:
            self.max_col = 80
        self.print_cnt = (y + self.max_col - 1) // self.max_col

    def setup(self):
        self._clear_screen()
        self._cursor_hyde()

    def teardown(self):
        self._cursor_show()

    def display(self, world, step, colors):
        screens = self._get_world(world, colors)
        screens[0] = self._get_title() + screens[0]
        screens[-1] = screens[-1] + self._get_step(step)
        for screen in screens:
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

    def _cursor_forward(self, n):
        return f'\033[{n}C'

    def _cursor_next_line(self, n):
        return f'\033[{n}E'

    def _cursor_previous_line(self, n):
        return f'\033[{n}F'

    def _setup_title(self):
        name, x, y = self.name, self.x, self.y
        count = x * y
        max_cell_size = 22500  # 150x150
        title = f'{name} ({x} x {y})'
        if count > max_cell_size:
            title += f' * warning : max_cell_size({max_cell_size}) is over! *'
        return title

    def _get_title(self):
        return f"{self.title}\n"

    def _get_world_mono(self, world, _):
        marks = self.marks
        max_y, max_x = self.y, self.x
        line = []
        # setup screen for display world on cli
        screens = ['┌' + ('─' * (max_x * 2 + 1)) + '┐\n']
        for y in range(max_y):
            cells = ''
            for x in range(max_x):
                cells += marks[world[y][x] + 1]
            line += ['│ ' + cells + '│']
        for i in range(self.print_cnt):
            start = i * self.max_col
            end = (i + 1) * self.max_col
            screens += ['\n'.join(line[start:end]) + '\n']
        screens += ['└' + ('─' * (max_x * 2 + 1)) + '┘\n']
        return screens

    def _get_world_color(self, world, colors):
        color_list = self.color_list
        marks = self.marks
        max_y, max_x = self.y, self.x
        max_color = len(color_list)
        line = []
        # setup screen for display world on cli
        screens = ['┌' + ('─' * (max_x * 2 + 1)) + '┐\n']
        for y in range(max_y):
            cells, pre_color = '', 0
            world_y = world[y]
            colors_y = colors[y]
            cells = ['　'] * max_x
            for x, cell in enumerate(world_y):
                if cell:
                    mark = marks[cell + 1]
                    # change color if it is different from previous
                    if color := colors_y[x] % max_color:
                        if color == pre_color:
                            cells[x] = mark
                        else:
                            cells[x] = color_list[color] + mark
                    else:
                        if pre_color:
                            cells[x] = color_list[0] + mark
                        else:
                            cells[x] = mark
                    pre_color = color
            if pre_color:
                line += ['│ ' + ''.join(cells) + color_list[0] + '│']
            else:
                line += ['│ ' + ''.join(cells) + '│']
        for i in range(self.print_cnt):
            start = i * self.max_col
            end = (i + 1) * self.max_col
            screens += ['\n'.join(line[start:end]) + '\n']
        screens += ['└' + ('─' * (max_x * 2 + 1)) + '┘\n']
        return screens

    def _update_mono(self, diff_world, step, _):
        marks, max_y = self.marks, self.y
        line, screens = [], []
        for y in range(max_y):
            cells = self._cursor_next_line(1)
            last_x = -2
            diff_world_y = diff_world[y]
            for x, cell in enumerate(diff_world_y):
                if cell:
                    forward = (x - last_x - 1) * 2
                    if forward:
                        cells += self._cursor_forward(forward)
                    mark = marks[cell]
                    if self.random:
                        if cell > 1:
                            mark = marks[randrange(1, len(marks))]
                    cells += mark
                    last_x = x
            if cells:
                line += [cells]

        for i in range(self.print_cnt):
            start = i * self.max_col
            end = (i + 1) * self.max_col
            screens += [''.join(line[start:end])]

        screens[0] = self._cursor_previous_line(max_y + 3) + screens[0]
        screens[-1] += self._cursor_next_line(2)
        screens[-1] += self._get_step(step)

        for screen in screens:
            print(screen, end='')

    @profile
    def _update_color(self, diff_world, step, colors):
        marks = self.marks
        color_list = self.color_list
        max_color = len(color_list)
        max_y = self.y
        line, screens = [], []
        for y in range(max_y):
            cells = self._cursor_next_line(1)
            last_x = -2
            diff_world_y = diff_world[y]
            colors_y = colors[y]
            for x, cell in enumerate(diff_world_y):
                if cell:
                    forward = (x - last_x - 1) * 2
                    if forward:
                        cells += self._cursor_forward(forward)
                    mark = marks[cell]
                    if self.random:
                        if cell > 1:
                            mark = marks[randrange(1, len(marks))]
                    cells += color_list[colors_y[x] % max_color] + mark
                    last_x = x
            line += [cells + color_list[0]]

        for i in range(self.print_cnt):
            start = i * self.max_col
            end = (i + 1) * self.max_col
            screens += [''.join(line[start:end])]

        screens[0] = self._cursor_previous_line(max_y + 3) + screens[0]
        screens[-1] += self._cursor_next_line(2)
        screens[-1] += self._get_step(step)

        for screen in screens:
            print(screen, end='')

    def _get_step(self, step):
        return '\033[39m' + f'step = {step}\n'


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
                description="Conway's Game of Life simulator on CLI")

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
        ('-rand', '--random'),
        ('-c', '--color'), ('-c2', '--color2'), ('-c3', '--color3'))
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
        ('rand', args.random),
        ('color', args.color), ('color2', args.color2),
        ('color3', args.color3))
    for key, value in options:
        setting[key] = value

    GameOfLife(**setting).start()
