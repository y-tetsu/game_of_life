import unittest
from game_of_life import GameOfLife


class TestGameOfLife(unittest.TestCase):
    def test_init_default(self):
        game = GameOfLife()
        self.assertEqual(game.console.title, 'game_of_life')
        self.assertEqual(game.x, 30)
        self.assertEqual(game.y, 15)
        self.assertEqual(len(game.world[0]), 30)
        self.assertEqual(len(game.world), 15)
        self.assertEqual(game.max_step, 100)
        self.assertEqual(game.wait_time, 0.05)
        self.assertEqual(game.console.life, '■')

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
        title = 'test'
        max_step = 10
        wait_time = 0.5
        life = '★'
        game = GameOfLife(title=title, world=world,
                          max_step=max_step, wait_time=wait_time, life=life)
        self.assertEqual(game.console.title, title)
        self.assertEqual(game.x, x)
        self.assertEqual(game.y, y)
        self.assertEqual(game.world, world)
        self.assertEqual(game.max_step, max_step)
        self.assertEqual(game.wait_time, wait_time)
        self.assertEqual(game.console.life, life)

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
        self.assertEqual(game.count_alive(0, 0), 0)
        self.assertEqual(game.count_alive(0, 2), 1)
        self.assertEqual(game.count_alive(0, 3), 2)
        self.assertEqual(game.count_alive(0, 4), 3)
        self.assertEqual(game.count_alive(1, 5), 4)
        self.assertEqual(game.count_alive(3, 5), 5)
        self.assertEqual(game.count_alive(2, 4), 6)
        self.assertEqual(game.count_alive(4, 4), 7)
        self.assertEqual(game.count_alive(6, 4), 8)

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
