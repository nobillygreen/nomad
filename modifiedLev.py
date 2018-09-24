from levenshtein import edit_distance as leven_dist
# https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html#Levenshtein-setmedian
from collections import defaultdict

# Stores values to past calls to level_dist
lev_dist_cache = defaultdict(lambda: defaultdict(lambda: None))
def memoized_leven_dist(s1, s2):
    memory = lev_dist_cache[s1][s2]
    if not (memory is None):
        return memory
    else:
        output = leven_dist(s1, s2)
        lev_dist_cache[s1][s2] = output
        return output

def levenshtein_multi_char_inserts(s_target, s_list):
    # Stores the action that resulted in the best score at a location in the string
    dp_memo = [{'cost': 0, 'from': None, 'via': None} for _ in s_target]

    for s_index, entry in enumerate(dp_memo):
        if s_index == 0:
            current_cost = 0
        else:
            current_cost = dp_memo[s_index-1]['cost']
        for s in s_list:
            upperbound = int(min(len(s) * 1.5, len(s_target) - s_index))
            substring_target = s_target[s_index:s_index + upperbound]
            leven_memo = memoized_leven_dist(s, substring_target)

            for i in xrange(1, len(leven_memo[-1])):
                s_cost = current_cost + 1 + leven_memo[-1][i]

                if dp_memo[s_index + i - 1]['from'] is None or dp_memo[s_index + i - 1]['cost'] > s_cost:
                    dp_memo[s_index + i - 1]['cost'] = s_cost
                    dp_memo[s_index + i - 1]['from'] = s_index - 1
                    dp_memo[s_index + i - 1]['via'] = s

    # levenshtein_multi_char_inserts_rec(s_target, -1, s_list, dp_memo, best_guesses)
    return dp_memo


if __name__ == "__main__":
    print 'cost', levenshtein_multi_char_inserts('1111222233334444', ['1111', '2222', '3', '4'])