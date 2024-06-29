from game_of_life import GameOfLife

if __name__ == '__main__':
    setting = {}
    setting['sample'] = 'glider-gun'
    setting['torus'] = True
    setting['mortal'] = True
    setting['color2'] = True
    setting['wait'] = 0.0

    GameOfLife(**setting).start()
