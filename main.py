from game import Game

GME = Game()

GME.run_move_sequence((2, 1, 0), .1, True)

while GME.running:
    GME.main_func()