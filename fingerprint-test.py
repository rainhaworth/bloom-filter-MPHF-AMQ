import bbhash
import random
import numpy as np
import time

import os

# define lengths of K, K'
K_lengths = [1000, 10000, 20000]

# define fraction of canonical keys in K'
key_fracs = [0.25, 0.5, 0.75]

# number of bits to mask for fingerprint array
mask_sizes = [7, 8, 10]

# seed random
random.seed(0)

# define bbhash params
num_threads = 1
gamma = 1.0

print('Length Frac Mask_size Real_rate Time Size FNs_found')
for length in K_lengths:
    # populate K
    K = []

    for _i in range(length):
        # generate random ints
        num = random.randint(0, 2**32-1)
        while num in K:
            num = random.randint(0, 2**32-1)
        K.append(num)

    # populate MPHF, get size of serialized file in bytes
    mph = bbhash.PyMPHF(K, len(K), num_threads, gamma)
    mph.save('fileout')
    mph_size = os.path.getsize('fileout') * 8 # convert bytes to bits

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
        
        for size in mask_sizes:
            # create mask
            mask = (1 << size) - 1

            # populate fingerprint array
            fingerprint = [0] * len(K)
            for val in K:
                h = mph.lookup(val)
                # use internal python hash() for fingerprint hash function
                fingerprint[h] = hash(val) & mask

            # calculate "simulated" fingerprint array size
            fp_size = len(K) * size

            # query over all K'
            queries = []
            start = time.process_time_ns()
            for seq in K_:
                result = mph.lookup(seq)
                if result == None:
                    queries.append(False)

                # check vs fingerprint array
                elif fingerprint[result] != hash(seq) & mask:
                    queries.append(False)
                    
                else:
                    queries.append(result < length)
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

            print(length, frac, size, round(FP_rate, 8), total_time, mph_size + fp_size, len(canonical) != 1)