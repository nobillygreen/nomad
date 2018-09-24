import cProfile
from modifiedLev import Nomad

if __name__ == "__main__":
    s = '111122221111222211112222111122221111222211112222111122221111222211112222'
    model = Nomad([s])
    print model.recompute_graph_and_trim_middle_strings()
    model.find_best_grammar(100)