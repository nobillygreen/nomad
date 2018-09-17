import numpy as np
# import subprocess
import pysais
from Levenshtein import distance as leven_dist

def modified_lev(s_target, S_list):
    dp_memo = np.zeros(len(s_target) + 1)
    modified_lev_rec_improved(s_target, S_list, dp_memo)
    print(dp_memo)
    print("SCORE", dp_memo[len(dp_memo)-1])


# def modified_lev_rec(s_target, S_list, dp_memo):
#     if (len(s_target) == 0):
#         return
#     cur_score = dp_memo[0]
#     for s in S_list:
#         if len(s) > len(s_target):
#             continue

#         s_score = cur_score + 1
#         for i in range(len(s)):

#             if s_target[i] != s[i]:
#                 s_score += 1        

#         if dp_memo[len(s)] == 0 or dp_memo[len(s)] > s_score:
#             dp_memo[len(s)] = s_score
#             modified_lev_rec(s_target[len(s):], S_list, dp_memo[len(s):])


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

def extractRepeats(strings):
    pass

# def extractRepeats(targets, repeatClass):
#     process = subprocess.Popen(["./repeats1/repeats11", "-i", "-r"+repeatClass, "-n2",
#                                 "-psol"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
#     print(' '.join(map(str, targets)))
#     print(type(' '.join(map(str, targets))))
#     process.stdin.write(' '.join(targets))
#     text_file = ''
#     while process.poll() is None:
#         output = process.communicate()[0].rstrip()
#         text_file += str(output)
#     process.wait()
#     repeats = []
#     firstLine = False
#     for line in text_file.splitlines():
#         if firstLine == False:
#             firstLine = True
#             continue
#         repeats.append(line.rstrip('\n'))
#     return repeats

if __name__ == "__main__":
    target1 = '1122334412332244122234123443212344$'
    sa = pysais.sais(target1)
    lcp, lcp_lm, lcp_mr = pysais.lcp(target1, sa)
    
    for off in sa:
        print(off, sa[off:])

    

    # target2 = '33441234123443224411442221'
    # modified_lev(target1, 
    #     ['11223', '11', '22', '2344', '1', '2', '3', '4'])

    # print(extractRepeats([target1]))