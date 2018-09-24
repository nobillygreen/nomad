import numpy as np
import subprocess
from random import random, choice
from copy import copy
from modifiedLev import levenshtein_multi_char_inserts
from collections import defaultdict
from pprint import pprint

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
        pattern_string = reduce(lambda a, b: str(
            a) + str(b), pattern_string, "")

        repeatedStrings.append((pattern_string, pattern_freq))

    return repeatedStrings

class Nomad():

    def __init__(self, target_strings):
        self.considered_canditates = []
        self.finding_candidates = True

        self.target_strings = target_strings
        self.alphabet = list(set("".join(target_strings)))
        self.middle_strings = []
        self.grammar_cost = None

        # saves the memo of the dynamic programming algo for creating the strings
        self.dp_memos_cache = {}
        self.recompute_graph_and_trim_middle_strings()

        self.max_motif_length = min(map(len, target_strings)) * 0.51

    def make_random_candidates(self, strings, num_candidates):
        candidates = []
        for i in xrange(num_candidates):
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
        dp_memos_cache = {}

        # Initialize the disctionary for counting the used strings
        used_string_counts = {s: 0 for s in middle_strings}
        for a in self.alphabet:
            used_string_counts[a] = 0

        for ms in middle_strings:
            # Assume that the middle strings can only be create by strings smaller that themselves
            possible_children = [s for s in middle_strings if len(s) < len(ms)]
            possible_children.extend(self.alphabet)
            memo = levenshtein_multi_char_inserts(ms, possible_children)
            dp_memos_cache[ms] = memo
            string_costs[ms] = memo[-1]['cost']
            used_strings = extract_path_from_action_list(memo)
            for s in used_strings:
                used_string_counts[s] += 1

        possible_children = copy(self.alphabet)
        possible_children.extend(middle_strings)
        for ts in self.target_strings:
            possible_children = copy(possible_children)
            memo = levenshtein_multi_char_inserts(ts, possible_children)
            dp_memos_cache[ts] = memo
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
                string_costs[s] = 0
                was_string_removed_flag = True

        while(was_string_removed_flag):
            total_cost, dp_memos_cache, middle_strings, was_string_removed_flag = self.total_cost(middle_strings)

        self.dp_memos_cache = dp_memos_cache
        return total_cost, dp_memos_cache, middle_strings, was_string_removed_flag

    def recompute_graph_and_trim_middle_strings(self):
        total_cost, dp_memos_cache, middle_strings, _ = self.total_cost(self.middle_strings)
        self.grammar_cost = total_cost
        self.dp_memos_cache = dp_memos_cache
        self.middle_strings = middle_strings
        return total_cost

    def strings_to_int_arrays(self, strings):
        int_array = []
        for s in strings:
            int_array.append(map(int, list(s)))

        return reduce(lambda a, b: a + [0] + b, int_array)

    def find_best_grammar(self, iterations, greedy):
        for i in xrange(iterations):
            print 'iteration', i
            cost = self.recompute_graph_and_trim_middle_strings()
            print "-------", cost, self.middle_strings

            all_strings = self.middle_strings + self.target_strings
            candidates = extractRepeats(
                self.strings_to_int_arrays(all_strings))

            filtered_canditates = []
            for c in candidates:
                s_c = str(c[0])
                if '0' in str(s_c):
                    continue
                
                if len(s_c) == 1:
                    continue

                if c[0] in self.considered_canditates:
                    continue

                if len(s_c) > self.max_motif_length:
                    continue
                
                self.considered_canditates.append(c[0])
                filtered_canditates.append(c[0])
            # candidates = self.make_random_candidates(all_strings, 100)

            # best_candidate = self.select_best_longest_candidate(candidates, cost)
            # best_candidate = self.select_best_shortest_candidate(filtered_canditates, cost, greedy)
            # if best_candidate == "":
            #     print "no good candidate"
            #     break
            # else:
            #     self.middle_strings.append(best_candidate)

            print "candidates", filtered_canditates
            self.middle_strings.extend(filtered_canditates)
            # good_candidates = self.select_all_good_candidates(candidates, cost)
            # if not good_candidates:
            #     if self.finding_candidates == True:
            #         self.considered_canditates = []
            #         self.finding_candidates = False
            #     else:
            #         break
            #     print "no more good candidates"
            #     # break
            # else:
            #     self.finding_candidates = True
            #     self.middle_strings.extend(good_candidates)



        print 'best grammar', self.middle_strings, cost
        return cost

    def select_best_longest_candidate(self, candidates, current_cost, greedy=True):
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
            new_cost, _, _, _ = self.total_cost(new_middle_strings)

            if new_cost < best_cost:
                best_candidate = candidate
                if greedy:
                    break

        return best_candidate

    # If greedy is true, returns the first candidate that has a positive impact on the cost
    def select_best_shortest_candidate(self, candidates, current_cost, greedy):
        best_candidate = ""
        best_cost = current_cost
        candidates = sorted(candidates, key=lambda x: len(x[0]))

        for candidate, _ in candidates:
            print 'considering candidate', candidate
            if candidate in self.middle_strings or candidate in self.target_strings:
                continue

            if best_candidate != "" and len(candidate) > len(best_candidate):
                break

            new_middle_strings = copy(self.middle_strings)
            new_middle_strings.append(candidate)
            new_cost, _, _, _ = self.total_cost(new_middle_strings)

            if new_cost < best_cost:
                best_candidate = candidate
                if greedy:
                    break

        return best_candidate

    def select_all_good_candidates(self, candidates, current_cost):
        good_candidates = []
        for candidate, _ in candidates:
            if candidate in self.middle_strings or candidate in self.target_strings:
                continue

            if len(candidate) > self.max_motif_length:
                continue

            print 'considering candidate', candidate

            middle_strings = copy(self.middle_strings)
            middle_strings.append(candidate)
            new_cost, _, _, _ = self.total_cost(middle_strings)

            if new_cost < current_cost:
                good_candidates.append(candidate)

        return good_candidates

if __name__ == "__main__":
    s = '5113511361136113511351136113611351135113611361135113511361136113'
    model = Nomad([s])
    # print model.recompute_graph_and_trim_middle_strings(greedy=False)
    model.find_best_grammar(100, False)