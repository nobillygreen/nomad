import numpy as np
import subprocess
from random import random, choice
from copy import copy
from modifiedLev import levenshtein_multi_char_inserts
from collections import defaultdict
from pprint import pprint
from numpy.random import choice


def extract_path_from_action_list(action_list):
    index = len(action_list) - 1
    used_strings = []
    while (index > 0):
        used_strings.append(action_list[index]['via'])
        index = action_list[index]['from']
    return used_strings[::-1]


def extractRepeats(strings_as_array):
    process = subprocess.Popen(["./repeats1/repeats11", "-i", "-r"+"mr", "-n2",
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
        pattern_string = reduce(lambda a, b: a + chr(b), pattern_string, "")

        repeatedStrings.append((pattern_string, pattern_freq))

    return repeatedStrings


class Nomad():

    def __init__(self, target_strings):
        self.target_strings = target_strings
        self.alphabet = list(set("".join(target_strings)))
        self.middle_strings = []
        self.grammar_cost = None
        self.recompute_graph_and_trim_middle_strings()

    def save_grammer_if_better(self):
        with open('minningrammar/grammar.txt', 'r') as f:
            cost = f.readline()
            if cost != "" and float(cost) < self.grammar_cost:
                print 'new grammar wasnt better: not saving'
                return

        with open('minningrammar/grammar.txt', 'w') as f:
            print "self cost", self.grammar_cost
            f.write(str(self.grammar_cost))
            f.write('\n')
            for motif in model.middle_strings:
                f.write(motif)
                f.write("\n")

    def filter_substring_repeats(self, candidates, max_num=None):
        print 'starting with', len(candidates), 'candidates'
        filtered_candidates = []
        filtered_candidates_frequencies = []
        for c in candidates:
            s_c = str(c[0])
            if '0' in s_c:
                continue

            if "".join(s_c.split()) != s_c:
                continue

            if len(s_c) == 1:
                continue

            if s_c in self.middle_strings or s_c in self.target_strings:
                continue

            filtered_candidates.append(c[0])
            filtered_candidates_frequencies.append(c[1])

        # normalize frequence to 1
        total = sum(filtered_candidates_frequencies)
        filtered_candidates_frequencies = [x/float(total) for x in filtered_candidates_frequencies]

        if not (max_num is None):
            substring_filtered_candidates = choice(
                filtered_candidates,
                size=max_num,
                replace=False,
                p=filtered_candidates_frequencies),

        print "candidates", substring_filtered_candidates[0]
        return substring_filtered_candidates[0]

    # Compute the total cost of a grammar
    # returns the total cost of the grammar, the dp memo for each string, and the
    # list of middle strings after strings that were used less than twice are removed
    def total_cost(self, middle_strings):
        # cost to compute each string
        string_costs = {}

        # Initialize the dictionary for counting the used strings
        used_string_counts = {s: 0 for s in middle_strings}
        for a in self.alphabet:
            used_string_counts[a] = 0

        for ms in middle_strings:
            # Assume that the middle strings can only be create by strings smaller that themselves
            possible_children = [s for s in middle_strings if len(s) < len(ms)]
            possible_children.extend(self.alphabet)
            memo = levenshtein_multi_char_inserts(ms, possible_children)
            string_costs[ms] = memo[-1]['cost']
            used_strings = extract_path_from_action_list(memo)
            for s in used_strings:
                used_string_counts[s] += 1

        possible_children = copy(self.alphabet)
        possible_children.extend(middle_strings)
        for ts in self.target_strings:
            ts_possible_children = copy(possible_children)
            memo = levenshtein_multi_char_inserts(ts, ts_possible_children)
            string_costs[ts] = memo[-1]['cost']
            used_strings = extract_path_from_action_list(memo)
            for s in used_strings:
                used_string_counts[s] += 1

        total_cost = sum(string_costs.values())

        was_string_removed_flag = False
        for s in used_string_counts:
            count = used_string_counts[s]
            if count <= 1 and not s in self.alphabet:
                middle_strings.remove(s)
                print "----------------------------removing", s
                string_costs[s] = 0
                was_string_removed_flag = True

        while(was_string_removed_flag):
            total_cost, middle_strings, was_string_removed_flag = self.total_cost(
                middle_strings)

        return total_cost, middle_strings, was_string_removed_flag

    def recompute_graph_and_trim_middle_strings(self):
        total_cost, middle_strings, _ = self.total_cost(self.middle_strings)
        self.grammar_cost = total_cost
        self.middle_strings = middle_strings
        return total_cost

    def strings_to_int_arrays(self, strings):
        int_array = []
        for s in strings:
            int_array.append(map(ord, list(s)))

        return reduce(lambda a, b: a + [0] + b, int_array)

    def find_best_grammar(self, max_iterations):
        cost = self.grammar_cost
        print "Starting cost: ", cost
        for i in xrange(max_iterations):
            all_strings = self.middle_strings + self.target_strings
            candidates = extractRepeats(
                self.strings_to_int_arrays(all_strings))

            filtered_candidates = self.filter_substring_repeats(candidates, 10)
            former_middle_strings = sorted(copy(self.middle_strings))
            self.middle_strings.extend(filtered_candidates)
            print "considering", len(filtered_candidates), "new candidates"
            new_cost = self.recompute_graph_and_trim_middle_strings()
            if new_cost >= cost:
                print "wasn't better, going back to former middle strings"
                self.middle_strings = former_middle_strings
            else:
                cost = new_cost
            print 'iteration', i, 'cost:', cost, "\n\n"
            self.save_grammer_if_better()

        print 'best grammar', self.middle_strings, cost,
        return cost


if __name__ == "__main__":
    minnin = []
    with open('minnin.txt', 'r') as f:
        for line in f:
            minnin.append(line)

    model = Nomad(minnin)
    model.find_best_grammar(100)

    with open('./minningrammar/grammar.txt', 'w') as f:
        for motif in model.middle_strings:
            f.write(motif)
            f.write("\n")
