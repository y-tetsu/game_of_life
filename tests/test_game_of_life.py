import unittest
from game_of_life import GameOfLife


class TestGameOfLife(unittest.TestCase):
    def test_init_default(self):
        game = GameOfLife()
        self.assertIsNone(game.sample)
        self.assertEqual(game.console.name, 'game_of_life')
        self.assertEqual(game.x, 30)
        self.assertEqual(game.y, 15)
        self.assertEqual(len(game.world[0]), 30)
        self.assertEqual(len(game.world), 15)
        self.assertEqual(game.max_step, 100)
        self.assertEqual(game.wait_time, 0.05)
        self.assertEqual(game.delay, 0.0)
        self.assertEqual(game.console.alive, '■')
        self.assertEqual(game.ratio, 0.5)
        self.assertEqual(game.loop, False)
        self.assertEqual(game.torus, False)
        self.assertEqual(game.mortal, False)
        self.assertEqual(game.color, False)

    def test_init_specific(self):
        x = 3
        y = 5
        world = [
            [1, 1, 1],
            [1, 0, 1],
            [1, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
        ]
        sample = 'test'
        name = 'test'
        max_step = 10
        wait_time = 0.5
        delay = 0.5
        alive = '★'
        ratio = 0.9
        loop = True
        torus = True
        mortal = True
        color = True
        game = GameOfLife(sample=sample, name=name, world=world,
                          max_step=max_step, wait_time=wait_time, delay=delay,
                          alive=alive, ratio=ratio, loop=loop, torus=torus,
                          mortal=mortal, color=color)
        self.assertEqual(game.sample, sample)
        self.assertEqual(game.console.name, name)
        self.assertEqual(game.x, x)
        self.assertEqual(game.y, y)
        self.assertEqual(game.world, world)
        self.assertEqual(game.max_step, max_step)
        self.assertEqual(game.wait_time, wait_time)
        self.assertEqual(game.delay, delay)
        self.assertEqual(game.console.alive, alive)
        self.assertEqual(game.ratio, ratio)
        self.assertEqual(game.loop, loop)
        self.assertEqual(game.torus, torus)
        self.assertEqual(game.mortal, mortal)
        self.assertEqual(game.color, color)

    def test_count_alive(self):
        world = [
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 1, 0, 1, 1, 1],
            [1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ]
        game = GameOfLife(world=world)
        self.assertEqual(game.count_alive(0, 0), (0, 0))
        self.assertEqual(game.count_alive(0, 2), (1, 0))
        self.assertEqual(game.count_alive(0, 3), (2, 0))
        self.assertEqual(game.count_alive(0, 4), (3, 0))
        self.assertEqual(game.count_alive(1, 5), (4, 0))
        self.assertEqual(game.count_alive(3, 5), (5, 0))
        self.assertEqual(game.count_alive(2, 4), (6, 0))
        self.assertEqual(game.count_alive(4, 4), (7, 0))
        self.assertEqual(game.count_alive(6, 4), (8, 0))

    def test_count_alive_torus(self):
        world = [
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 1, 0, 1, 1, 1],
            [1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ]
        game = GameOfLife(world=world, torus=True)
        self.assertEqual(game.count_alive(0, 0), (3, 0))
        self.assertEqual(game.count_alive(0, 2), (2, 0))
        self.assertEqual(game.count_alive(0, 3), (4, 0))
        self.assertEqual(game.count_alive(0, 4), (6, 0))
        self.assertEqual(game.count_alive(1, 5), (5, 0))
        self.assertEqual(game.count_alive(3, 5), (5, 0))
        self.assertEqual(game.count_alive(2, 4), (6, 0))
        self.assertEqual(game.count_alive(4, 4), (7, 0))
        self.assertEqual(game.count_alive(6, 4), (8, 0))

    def test_count_alive_color(self):
        world = [
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 1, 0, 1, 1, 1],
            [1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ]
        colors = [
            [1, 2, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 1, 0, 1, 1, 1],
            [1, 0, 1, 1, 8, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ]
        game = GameOfLife(world=world, torus=True, color=True)
        game.colors = colors
        self.assertEqual(game.count_alive(0, 0), (3, 2))
        self.assertEqual(game.count_alive(3, 5), (5, 8))

    def test_new_cell_from_alive(self):
        world = [
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 1, 0, 1, 1, 1],
            [1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ]
        game = GameOfLife(world=world)
        self.assertEqual(game.new_cell(0, 0), 0)  # alive=0 to dead
        self.assertEqual(game.new_cell(0, 2), 0)  # alive=1 to dead
        self.assertEqual(game.new_cell(0, 3), 1)  # alive=2 keep
        self.assertEqual(game.new_cell(0, 4), 1)  # alive=3 keep
        self.assertEqual(game.new_cell(1, 5), 0)  # alive=4 to dead
        self.assertEqual(game.new_cell(3, 5), 0)  # alive=5 to dead
        self.assertEqual(game.new_cell(2, 4), 0)  # alive=6 to dead
        self.assertEqual(game.new_cell(4, 4), 0)  # alive=7 to dead
        self.assertEqual(game.new_cell(6, 4), 0)  # alive=8 to dead

    def test_new_cell_from_dead(self):
        world = [
            [0, 0, 1, 1, 1, 1],
            [0, 0, 0, 1, 1, 1],
            [0, 1, 0, 1, 1, 1],
            [0, 1, 1, 1, 1, 1],
            [0, 1, 0, 1, 0, 1],
            [1, 1, 0, 1, 1, 1],
        ]
        game = GameOfLife(world=world)
        self.assertEqual(game.new_cell(0, 0), 0)  # dead=0 keep
        self.assertEqual(game.new_cell(0, 1), 0)  # dead=1 keep
        self.assertEqual(game.new_cell(0, 2), 0)  # dead=2 keep
        self.assertEqual(game.new_cell(0, 3), 1)  # dead=3 to alive
        self.assertEqual(game.new_cell(0, 4), 0)  # dead=4 keep
        self.assertEqual(game.new_cell(2, 1), 0)  # dead=5 keep
        self.assertEqual(game.new_cell(2, 2), 0)  # dead=6 keep
        self.assertEqual(game.new_cell(2, 4), 0)  # dead=7 keep
        self.assertEqual(game.new_cell(4, 4), 0)  # dead=8 keep

    def test_update(self):
        world = [
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
        ]
        expected = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        game = GameOfLife(world=world)
        for _ in range(4):
            game.update()
        self.assertEqual(game.world, expected)

    def test_update_mortal(self):
        world = [
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ]
        expected = [
            [0, 0, 0, 0],
            [0, 5, 5, 0],
            [0, 5, 5, 0],
            [0, 0, 0, 0],
        ]
        game = GameOfLife(world=world, mortal=True)
        for _ in range(4):
            game.update()
        self.assertEqual(game.ages, expected)

    def test_update_mortal2(self):
        world = [
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
        ]
        expected = [
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 5, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
        ]
        game = GameOfLife(world=world, mortal=True)
        for i in range(4):
            game.update()
        self.assertEqual(game.ages, expected)
