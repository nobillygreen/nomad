import pysais
sequence = "aaabbbcccdddaaacccbbbddd"

sa = pysais.sais(sequence)
print('before')
lcp, lcp_lm, lcp_mr = pysais.lcp(sequence, sa)

print('answers', lcp, lcp_lm, lcp_mr)