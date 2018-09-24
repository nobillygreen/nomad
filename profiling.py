import cProfile
from nomad import Nomad

if __name__ == "__main__":
    s = '111122221111222211112222'
    model = Nomad([s])
    # model.find_best_grammar(100)
    cProfile.run('model.find_best_grammar(100, True)', )
    # cProfile.run('model.find_best_grammar(100, False)')