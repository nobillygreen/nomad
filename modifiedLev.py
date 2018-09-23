import numpy as np
import subprocess
from random import random, choice
from copy import copy
from Levenshtein import distance as leven_dist
from operator import itemgetter
# https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html#Levenshtein-setmedian


def modified_lev(s_target, S_list):
    # The dynamic programming memo
    dp_memo = np.zeros(len(s_target) + 1)

    # Stores the action that resulted in the best score at a location in the string
    dp_action_memo = [None for i in range(len(s_target) + 1)]
    modified_lev_rec_improved(s_target, 0, S_list, dp_memo, dp_action_memo)
    return dp_memo, dp_action_memo

# s_target: the string to compute a cost of generating
# s_index: the current index of the string
# S_list: the possible strings to use to create s_target
# dp_memo: holds the current best known score for creating the string up to a given index
# dp_action_memo: stores what string was used as in insertion to get to a given index and
#    specifies which index it was added at too.
def modified_lev_rec_improved(s_target, s_index, S_list, dp_memo, dp_action_memo):
    if (len(s_target) <= s_index):
        return

    cur_score = dp_memo[s_index]

    for s in S_list:
        # upperbound to twice the length of the string. This is arbitrarily set for now
        for i in range(1, min(2*len(s), len(s_target[s_index:])+2)):
            s_score = cur_score + 1
            target_substring = s_target[s_index:s_index+i]
            substring_score = leven_dist(target_substring, s)
            s_score += substring_score
            
            if dp_memo[min(s_index+i, s_index + len(target_substring))] == 0 or dp_memo[min(s_index+i, s_index + len(target_substring))] > s_score:
                dp_memo[s_index+i] = s_score
                dp_action_memo[s_index+i] = {'from': s_index, 'via': s}
                modified_lev_rec_improved(s_target, s_index + i, S_list, dp_memo, dp_action_memo)

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

        pattern_score =  pattern_freq / float(length_of_pattern)

        repeatedStrings.append((pattern_string, pattern_freq, pattern_score))

    return repeatedStrings

def make_random_candidates(strings, num_candidates):
    candidates = []
    for i in range(num_candidates):
        s = choice(strings)
        a, b = int(random() * (len(s) -1)), int(random() * (len(s)-1) + 1)
        a, b = sorted([a,b])
        b = b + 1
        candidates.append((s[a:b], 0, 0))

    return candidates

def extract_path_from_action_list(action_list):
    pass

# Compute the total cost of a given grammar
def total_cost(alphabet, middle_strings, target_strings):
    total_cost = 0
    for ms in middle_strings:
        possible_children = [s for s in middle_strings if len(s) < len(ms)]
        possible_children.extend(alphabet)
        costs, actions = modified_lev(ms, possible_children) 
        total_cost += costs[-1]

    for ts in target_strings:
        possible_children = copy(alphabet)
        possible_children.extend(middle_strings)
        costs, actions = modified_lev(ts, possible_children)
        total_cost += costs[-1]

    return total_cost
        
def strings_to_int_arrays(strings):
    int_array = []
    for s in strings:
        int_array.append(map(int, list(s)))
    
    return reduce(lambda a, b: a + b, int_array)

def nomad(strings):
    alphabet = list(set("".join(strings)))
    middle_strings = []
    target_strings = strings
    print("initial cost", total_cost(alphabet, middle_strings, target_strings))

    for i in range(30):
        cost = total_cost(alphabet, middle_strings, target_strings)
        all_strings = middle_strings + target_strings
        candidates = extractRepeats(strings_to_int_arrays(all_strings))
        candidates = sorted(candidates, key=lambda x: len(x[0]))
        print(candidates)

        best_candidate = ""
        best_cost = cost
        best_score = float('inf')
        for candidate, candidate_freq, candidate_score in candidates:
            if best_candidate != "" and candidate_score < best_score:
                break
            new_middle_strings = copy(middle_strings)
            new_middle_strings.append(candidate)
            new_cost = total_cost(alphabet, new_middle_strings, target_strings)
            if new_cost <= best_cost:
                best_length = len(candidate)
                best_candidate = candidate
                best_score = candidate_score

        if best_candidate == "":
            break
        else:
            # print("BEST CANDIDATE", best_candidate)
            middle_strings.append(best_candidate)

    final_cost = total_cost(alphabet, middle_strings, target_strings)
    return middle_strings, final_cost


if __name__ == "__main__":  
    s1 = '1111222233334444111122223333444411112222333344441111222233334444'
    # outcome = nomad([s1])
    # print("FINAL")
    # print(outcome)


    print(total_cost(['1','2','3','4'],
        ['4444', '3333', '2222', '1111'],
        ['1111222233334444']
    ))
