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
