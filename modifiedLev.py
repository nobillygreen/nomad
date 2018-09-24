import numpy as np
import subprocess
from random import random, choice
from copy import copy
# from Levenshtein import distance as leven_dist
from levenshtein import edit_distance as leven_dist
from operator import itemgetter
from collections import defaultdict
from math import floor, ceil
from pprint import pprint
# https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html#Levenshtein-setmedian


def levenshtein_multi_char_inserts(s_target, s_list):
    # Stores the action that resulted in the best score at a location in the string
    dp_memo = [{'score': 0, 'from': None, 'via': None} for _ in s_target]
    levenshtein_multi_char_inserts_rec(s_target, -1, s_list, dp_memo)
    return dp_memo

# s_target: the string to compute a cost of generating
# m_index: the current index of the memo
# S_list: the possible strings to use to create s_target
# dp_memo: holds the current best known score for creating the string up to a given index
# dp_action_memo: stores what string was used as in insertion to get to a given index and
#    specifies which index it was added at too.


def levenshtein_multi_char_inserts_rec(s_target, m_index, S_list, dp_memo):
    if len(s_target) - 1 <= m_index:
        return

    if m_index == -1:
        cur_score = 0
    else:
        cur_score = dp_memo[m_index]['score']

    for s in S_list:
        s_index = m_index + 1
        upperbound = int(min(len(s) * 1.5, len(s_target) - m_index))
        substring_target = s_target[s_index:s_index + upperbound + 1]
        leven_memo = leven_dist(s, substring_target)

        for i in range(1, len(leven_memo[-1])):
            s_score = cur_score + 1
            # target_substring = s_target[s_index:s_index+i+1]
            s_score += leven_memo[-1][i]
            if dp_memo[m_index + i]['from'] is None or dp_memo[m_index + i]['score'] > s_score:
                if s == "1111" and s_index == 2:
                    pass
                dp_memo[m_index + i] = {'score': s_score, 'from': m_index, 'via': s}
                levenshtein_multi_char_inserts_rec(s_target, m_index + i, S_list, dp_memo)

def extract_path_from_action_list(action_list):
    index = len(action_list) - 1
    used_strings = []
    while (index > 0):
        used_strings.append(action_list[index]['via'])
        index = action_list[index]['from']
    return used_strings[::-1]

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
        pattern_string = reduce(lambda a, b: str(
            a) + str(b), pattern_string, "")

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
            a, b = int(random() * (len(s) - 1)), int(random() * (len(s)-1) + 1)
            a, b = sorted([a, b])
            b = b + 1
            candidates.append((s[a:b], 0))

        return candidates

    # Compute the total cost of a grammar
    # returns the total cost of the grammar, the dp memo for each string, and the
    # list of middle strings after strings that were used less than twice are removed
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
            memo = levenshtein_multi_char_inserts(ms, possible_children)
            dp_memo_cache[ms] = memo
            string_costs[ms] = memo[-1]['score']
            used_strings = extract_path_from_action_list(memo)
            for s in used_strings:
                used_string_counts[s] += 1

        possible_children = copy(self.alphabet)
        possible_children.extend(middle_strings)
        for ts in self.target_strings:
            possible_children = copy(possible_children)
            memo = levenshtein_multi_char_inserts(ts, possible_children)
            dp_memo_cache[ts] = memo
            string_costs[ts] = memo[-1]['score']
            used_strings = extract_path_from_action_list(memo)
            for s in used_strings:
                used_string_counts[s] += 1

        for s in used_string_counts:
            count = used_string_counts[s]
            if count == 0 and not s in self.alphabet:
                middle_strings.remove(s)
                string_costs[s] = 0

        total_cost = sum(string_costs.values()) + len(middle_strings)
        return total_cost, dp_memo_cache, middle_strings

    def recompute_graph_and_trim_middle_strings(self):
        total_cost, dp_memo_cache, middle_strings = self.total_cost(
            self.middle_strings)
        self.grammar_cost = total_cost
        self.dp_memos_cache = dp_memo_cache
        self.middle_strings = middle_strings
        return total_cost

    def strings_to_int_arrays(self, strings):
        int_array = []
        for s in strings:
            int_array.append(map(int, list(s)))

        return reduce(lambda a, b: a + b, int_array)

    def find_best_grammar(self, iterations):
        for i in range(iterations):
            print 'iteration', i
            cost = self.recompute_graph_and_trim_middle_strings()
            # cost, dp_memos,  = self.total_cost(self.middle_strings)
            print "-------", cost, self.middle_strings

            all_strings = self.middle_strings + self.target_strings
            candidates = extractRepeats(
                self.strings_to_int_arrays(all_strings))
            # candidates = self.make_random_candidates(all_strings, 100)

            # best_candidate = self.select_best_longest_candidate(candidates, cost)
            best_candidate = self.select_best_shortest_candidate(
                candidates, cost)
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
            if candidate in self.middle_strings or candidate in self.target_strings:
                continue

            if best_candidate != "" and len(candidate) < len(best_candidate):
                break

            new_middle_strings = copy(self.middle_strings)
            new_middle_strings.append(candidate)
            new_cost, _, _ = self.total_cost(new_middle_strings)

            if new_cost < best_cost:
                best_candidate = candidate

        return best_candidate

    def select_best_shortest_candidate(self, candidates, current_cost):
        best_candidate = ""
        best_cost = current_cost
        candidates = sorted(candidates, key=lambda x: len(x[0]))

        for candidate, _ in candidates:
            if candidate in self.middle_strings or candidate in self.target_strings:
                continue

            if best_candidate != "" and len(candidate) > len(best_candidate):
                break

            new_middle_strings = copy(self.middle_strings)
            new_middle_strings.append(candidate)
            new_cost, _, _ = self.total_cost(new_middle_strings)

            if new_cost < best_cost:
                best_candidate = candidate

        return best_candidate


if __name__ == "__main__":
    s = '111122221111222211112222111122221111222211112222111122221111222211112222'
    model = Nomad([s])
    print model.recompute_graph_and_trim_middle_strings()
    model.find_best_grammar(100)