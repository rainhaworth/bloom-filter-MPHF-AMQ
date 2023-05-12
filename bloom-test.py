from bloom_filter2 import BloomFilter
import random
import numpy as np
import time

# define lengths of K, K'
K_lengths = [1000, 10000, 20000]

# define fraction of canonical keys in K'
key_fracs = [0.25, 0.5, 0.75]

# define expected FP rates
error_rates = [1/(2**7), 1/(2**8), 1/(2**10)]

# seed random
random.seed(0)

print('Length Frac Expected_rate Real_rate Time Size FNs_found')
for length in K_lengths:
    # populate K
    K = []

    for _i in range(length):
        # generate random integers
        num = random.randint(0, 2**32-1)
        while num in K:
            num = random.randint(0, 2**32-1)
        K.append(num)

    for frac in key_fracs:
        # populate K'
        # canonical strings
        K_ = K[:round(length*frac)]

        # non-canonical
        for i in range(len(K_), length):
            num = random.randint(0, 2**32-1)
            while num in K:
                num = random.randint(0, 2**32-1)
            K_.append(num)
        
        for rate in error_rates:
            # populate bloom filter
            bloom = BloomFilter(length, rate)

            for seq in K:
                bloom.add(seq)
            
            # query over all K'
            queries = np.empty(len(K_), dtype=bool)
            start = time.process_time_ns()
            for i, seq in enumerate(K_):
                query = seq in bloom
                queries[i] = query
            end = time.process_time_ns()
            
            # convert to ms
            total_time = (end - start) / 1000000

            # compute FP rate
            FP_rate = 0.0
            vals, counts = np.unique(queries[round(length*frac):], return_counts=True)
            if len(vals) == 2:
                FP_rate = counts[1] / (counts[0] + counts[1])

            # check for FNs
            canonical = np.unique(queries[:round(length*frac)])

            print(length, frac, rate, round(FP_rate, 8), total_time, bloom.num_bits_m, len(canonical) != 1)
            