import unittest
import os
from life_game import LifeGame


class TestLifeGame(unittest.TestCase):
    os_tmp = None

    def setUp(self):
        self.os_tmp = os.system
        os.system = lambda x: False

    def tearDown(self):
        os.system = self.os_tmp

    def test_init_default(self):
        lifegame = LifeGame()
        self.assertEqual(lifegame.x, 10)
        self.assertEqual(lifegame.y, 10)
        self.assertEqual(len(lifegame.state), 10)
        self.assertEqual(len(lifegame.state[0]), 10)
        self.assertEqual(lifegame.title, 'Life Game')
        self.assertEqual(lifegame.step, 45)

    def test_init_specific(self):
        x = 3
        y = 5
        state = [
            [1, 1, 1],
            [1, 0, 1],
            [1, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
        ]
        title = 'test'
        step = 10
        lifegame = LifeGame(state=state, title=title, step=step)
        self.assertEqual(lifegame.x, x)
        self.assertEqual(lifegame.y, y)
        self.assertEqual(lifegame.state, state)
        self.assertEqual(lifegame.title, title)
        self.assertEqual(lifegame.step, step)
