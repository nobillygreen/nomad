import numpy as np
import subprocess
from random import random, choice
from copy import copy
from Levenshtein import distance as leven_dist
from operator import itemgetter
from collections import defaultdict
from math import floor, ceil
# https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html#Levenshtein-setmedian

def levenshtein_multi_char_inserts(s_target, s_list):
    dp_memo = np.zeros(len(s_target) + 1)

    # Stores the action that resulted in the best score at a location in the string
    dp_action_memo = [None for i in range(len(s_target) + 1)]
    levenshtein_multi_char_inserts_rec(s_target, 0, s_list, dp_memo, dp_action_memo)
    return dp_memo, dp_action_memo

# s_target: the string to compute a cost of generating
# s_index: the current index of the string
# S_list: the possible strings to use to create s_target
# dp_memo: holds the current best known score for creating the string up to a given index
# dp_action_memo: stores what string was used as in insertion to get to a given index and
#    specifies which index it was added at too.
def levenshtein_multi_char_inserts_rec(s_target, s_index, S_list, dp_memo, dp_action_memo):
    if (len(s_target) <= s_index):
        return

    cur_score = dp_memo[s_index]

    for s in S_list:
        # upperbound to twice the length of the string. This is arbitrarily set for now
        # lowerbound = int(max(1, floor((2/3.0) * len(s))))
        # upperbound = max(2, min(floor(1.5*len(s)), len(s_target[s_index:])))
        # print s, lowerbound, max(2, min(2*len(s), len(s_target[s_index:])+2))
        for i in range(1, int(max(2, min(2*len(s), len(s_target[s_index:])+2)))):
        # print lowerbound, upperbound - 1
        # if lowerbound >= upperbound:
        #     break
        # for i in range(int(lowerbound), int(upperbound)):
            s_score = cur_score + 1
            target_substring = s_target[s_index:s_index+i]
            substring_score = leven_dist(target_substring, s)
            s_score += substring_score
            
            if dp_memo[min(s_index+i, s_index + len(target_substring))] == 0 or dp_memo[min(s_index+i, s_index + len(target_substring))] > s_score:
                dp_memo[s_index+i] = s_score
                dp_action_memo[s_index+i] = {'from': s_index, 'via': s}
                levenshtein_multi_char_inserts_rec(s_target, s_index + i, S_list, dp_memo, dp_action_memo)

def extractRepeats(strings_as_array):
    process = subprocess.Popen(["./repeats1/repeats11", "-i", "-r"+"m", "-n2",
                                "-psol"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    process.stdin.write(' '.join(map(str, strings_as_array)))
    text_file = ''
    while process.poll() is None:
        output = process.communicate()[0].rstrip()
        text_file += output
    process.wait()
    repeats = []
    firstLine = False
    for line in text_file.splitlines():
        if firstLine == False:
            firstLine = True
            continue
        repeats.append(line.rstrip('\n'))
    
    return parseRepeats(repeats, strings_as_array)

def parseRepeats(repeats, strings_as_array):
    # tuples of (string, count, pattern score) where count is the number of times this pattern occurs
    # and pattern score is the length of the pattern to the power of its frequency
    repeatedStrings = []
    for repeat in repeats:
        if repeat[0] == '#':
            continue

        length_of_pattern, pattern_freq, pattern_loc = repeat.split(' ')
        length_of_pattern = int(length_of_pattern)
        pattern_freq = int(pattern_freq)
        pattern_loc = pattern_loc[1:-1]
        pattern_loc = map(int, pattern_loc.split(','))
        pattern_string = strings_as_array[pattern_loc[0]: pattern_loc[0] + length_of_pattern]
        pattern_string = reduce(lambda a, b: str(a) + str(b), pattern_string, "")

        repeatedStrings.append((pattern_string, pattern_freq))

    return repeatedStrings

class Nomad():

    def __init__(self, target_strings):
        self.target_strings = target_strings
        self.alphabet = list(set("".join(target_strings)))
        self.middle_strings = []
        self.grammar_cost = None

        # saves the memo of the dynamic programming algo for creating the strings
        self.dp_memos_cache = {}
        self.recompute_graph_and_trim_middle_strings()

    def make_random_candidates(self, strings, num_candidates):
        candidates = []
        for i in range(num_candidates):
            s = choice(strings)
            a, b = int(random() * (len(s) -1)), int(random() * (len(s)-1) + 1)
            a, b = sorted([a,b])
            b = b + 1
            candidates.append((s[a:b], 0, 0))

        return candidates

    # Compute the total cost of a grammar
    def total_cost(self, middle_strings):
        # cost to compute each string
        string_costs = {}

        # cache of the dp memo used to calculate the cost of each string
        dp_memo_cache = {}

        # Initialize the disctionary for counting the used strings
        used_string_counts = {s: 0 for s in middle_strings}
        for a in self.alphabet:
            used_string_counts[a] = 0

        for ms in middle_strings:
            # Assume that the middle strings can only be create by strings smaller that themselves
            possible_children = [s for s in middle_strings if len(s) < len(ms)]
            possible_children.extend(self.alphabet)
            costs, actions = levenshtein_multi_char_inserts(ms, possible_children) 
            string_costs[ms] = actions
            used_strings = self.extract_path_from_action_list(actions)
            for s in used_strings:
                used_string_counts[s] += 1
            string_costs[ms] = costs[-1]

        possible_children = copy(self.alphabet)
        possible_children.extend(middle_strings)
        for ts in self.target_strings:
            possible_children = copy(possible_children)
            costs, actions = levenshtein_multi_char_inserts(ts, possible_children)
            string_costs[ts] = actions
            used_strings = self.extract_path_from_action_list(actions)
            for s in used_strings:
                used_string_counts[s] += 1
            string_costs[ts] = costs[-1]

        for s in used_string_counts:
            count = used_string_counts[s]
            if count == 0 and not s in self.alphabet:
                middle_strings.remove(s)
                string_costs[s] = 0
                print '*****************removing', s


        total_cost = sum(string_costs.values())
        # returns the total cost of the grammar, the dp memo for each string, and the
        # list of middle strings after strings that were used less than twice are removed
        return total_cost, dp_memo_cache, middle_strings

    def recompute_graph_and_trim_middle_strings(self):
        total_cost, dp_memo_cache, middle_strings = self.total_cost(self.middle_strings)
        self.grammar_cost = total_cost
        self.dp_memos_cache = dp_memo_cache
        self.middle_strings = middle_strings
        return total_cost

    def extract_path_from_action_list(self, action_list):
        index = len(action_list) - 1
        used_strings = []
        while (index > 0):
            used_strings.append(action_list[index]['via'])
            index = action_list[index]['from']
        return used_strings

    def strings_to_int_arrays(self, strings):
        int_array = []
        for s in strings:
            int_array.append(map(int, list(s)))
        
        return reduce(lambda a, b: a + b, int_array)

    def find_best_grammar(self, iterations):
        for i in range(iterations):
            cost = self.recompute_graph_and_trim_middle_strings()
            # cost, dp_memos,  = self.total_cost(self.middle_strings)
            print "iteration", i, cost, self.middle_strings

            all_strings = self.middle_strings + self.target_strings
            candidates = extractRepeats(self.strings_to_int_arrays(all_strings))

            best_candidate = self.select_best_longest_candidate(candidates, cost)
            if best_candidate == "":
                print "no good candidate"
                break
            else:
                self.middle_strings.append(best_candidate)

        print 'best grammar', self.middle_strings, cost
        return cost

    def select_best_longest_candidate(self, candidates, current_cost):
        best_candidate = ""
        best_cost = current_cost
        candidates = sorted(candidates, key=lambda x: len(x[0]), reverse=True)

        for candidate, _ in candidates:
            if best_candidate != "" and len(candidate) < len(best_candidate):
                break

            new_middle_strings = copy(self.middle_strings)
            new_middle_strings.append(candidate)
            new_cost, _, _ = self.total_cost(new_middle_strings)
            print 'candidate', candidate, new_cost

            if new_cost < best_cost:
                best_candidate = candidate
        
        return best_candidate

    def select_best_shortest_candidate(self, candidates, current_cost):
        best_candidate = ""
        best_cost = current_cost
        candidates = sorted(candidates, key=lambda x: len(x[0]))

        for candidate, _ in candidates:
            if best_candidate != "" and len(candidate) > len(best_candidate):
                break

            new_middle_strings = copy(self.middle_strings)
            new_middle_strings.append(candidate)
            new_cost, _, _ = self.total_cost(new_middle_strings)

            if new_cost < best_cost:
                best_candidate = candidate
        
        return best_candidate

if __name__ == "__main__":  
    s1 = '111111222222333333444444111111222222333333444444'
    model = Nomad([s1])
    model.find_best_grammar(10)