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

    def test_init(self):
        lifegame = LifeGame()
        self.assertEqual(lifegame.x, 10)
        self.assertEqual(lifegame.y, 10)
        self.assertIsNotNone(lifegame.state)
        self.assertEqual(lifegame.title, 'Life Game')
        self.assertEqual(lifegame.step, 45)
