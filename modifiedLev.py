import numpy as np
import subprocess
from random import random, choice
from copy import copy
from Levenshtein import distance as leven_dist
from operator import itemgetter
# https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html#Levenshtein-setmedian

def modified_lev(s_target, S_list):
    dp_memo = np.zeros(len(s_target) + 1)
    modified_lev_rec_improved(s_target, S_list, dp_memo)
    return dp_memo[-1]

def modified_lev_rec_improved(s_target, S_list, dp_memo):
    if (len(s_target) == 0):
        return

    cur_score = dp_memo[0]

    for s in S_list:
        # upperbound to twice the length of the string
        for i in range(min(2*len(s), len(s_target))):
            s_score = cur_score + 1
            target_substring = s_target[:i+1]
            substring_score = leven_dist(target_substring, s)
            s_score += substring_score
            
            if dp_memo[i+1] == 0 or dp_memo[i+1] > s_score:
                dp_memo[i+1] = s_score
                modified_lev_rec_improved(s_target[i+1:], S_list, dp_memo[i+1:])

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

        # pattern_score =  pattern_freq ** length_of_pattern
        pattern_score =  pattern_freq

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



# Compute the total cost of the current grammar
def total_cost(alphabet, middle_strings, target_strings):
    total_cost = 0
    for ms in middle_strings:
        possible_children = [s for s in middle_strings if len(s) < len(ms)]
        possible_children.extend(alphabet)
        total_cost += modified_lev(ms, possible_children)

    for ts in target_strings:
        possible_children = copy(alphabet)
        possible_children.extend(middle_strings)
        total_cost += modified_lev(ts, possible_children)

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

    # while(True):
    for i in range(30):
        cost = total_cost(alphabet, middle_strings, target_strings)
        print('cost at iteration ', i, ': ', cost)
        all_strings = middle_strings + target_strings
        candidates = extractRepeats(strings_to_int_arrays(all_strings))
        # candidates = sorted(candidates, key=lambda x: x[2], reverse=True)
        # candidates = make_random_candidates(all_strings, 100)

        print ("num candidates", len(candidates))

        best_candidate = ""
        best_cost = cost
        for candidate, candidate_freq, candidate_score in candidates:
            print('candidate', candidate)
            new_middle_strings = copy(middle_strings)
            new_middle_strings.append(candidate)
            new_cost = total_cost(alphabet, new_middle_strings, target_strings)
            # print("    ", candidate, candidate_freq, new_cost)
            if new_cost < best_cost:
                best_candidate = candidate
                best_cost = new_cost
                # break

        # if best_candidate == "":
        #     print("NO MORE CANDIDATES")
        #     break

        if best_candidate == "":
            break
        else:
            print("BEST CANDIDATE", best_candidate)
            middle_strings.append(best_candidate)

    return middle_strings


if __name__ == "__main__":  
    s1 = '44433111222111'
    s2 = '4411122333444'
    # print(make_random_candidates([s1, s1], 100))
    print(nomad([s1, s2]))