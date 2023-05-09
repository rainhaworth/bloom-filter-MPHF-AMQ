from bloom_filter2 import BloomFilter
import random
import numpy as np
import time

# define lengths of K, K'
K_lengths = [1000, 5000, 10000]

# define fraction of canonical keys in K'
# do we like do 9 trails or
key_fracs = [0.25, 0.5, 0.75]

# define expected FP rates
error_rates = [1/(2**7), 1/(2**8), 1/(2**10)]
print(error_rates)

# define k-mer things, seed random
nucleotides = ['A','C','G','T']
size = 31
random.seed(0)

print('length frac expected_rate real_rate time size')
for length in K_lengths:
    # populate K
    K = []

    for i in range(length):
        # generate 31-mers
        K.append(''.join(random.choice(nucleotides) for _i in range(size)))

    #print(K[-1])

    for frac in key_fracs:
        # populate K'
        # canonical strings
        K_ = K[:round(length*frac)]

        # non-canonical
        for i in range(len(K_), length):
            seq = ''.join(random.choice(nucleotides) for _i in range(size))
            while seq in K:
                seq = ''.join(random.choice(nucleotides) for _i in range(size))
            K_.append(seq)
        
        for rate in error_rates:
            # populate bloom filter
            bloom = BloomFilter(length, rate)

            for seq in K:
                bloom.add(seq)
            
            # query over all K'
            queries = np.empty(len(K_), dtype=bool)
            start = time.time()
            for i, seq in enumerate(K_):
                query = seq in bloom
                queries[i] = query
            end = time.time()
            
            # TODO: figure out timeit
            total_time = end - start

            FP_rate = 0.0
            vals, counts = np.unique(queries[round(length*frac):], return_counts=True)
            if len(vals) == 2:
                FP_rate = counts[1] / (counts[0] + counts[1])

            print(length, frac, rate, FP_rate, total_time, bloom.num_bits_m)
            #print('FN check:', np.unique(queries[:round(length*frac)], return_counts=True))
            