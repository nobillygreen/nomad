import cProfile
from nomad import Nomad

if __name__ == "__main__":
    s = '251131511325113151135611376113251131511325113151135611376113'
    model = Nomad([s])
    # model.find_best_grammar(100)
    cProfile.run('model.find_best_grammar(100, False)', )
    # cProfile.run('model.find_best_grammar(100, False)')