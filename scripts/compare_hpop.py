import numpy as np
import itertools
import pickle
from collections import defaultdict
import sys

hpop_file = sys.argv[1]
althap = False

ploidy = 4
H_truth = []

#haps_file = './triploid_files/haplo.p'
#hpop_file = './triploid_files/hpop_triploid_qual.txt'

haps_file = sys.argv[2]
#haps_file = './tetraploid_files/haplo.p'
#hpop_file = './tetraploid_files/hpop.txt'

total_ham_rate = 0
total_swer = 0
end_of_block_last_block = 0
H_blocks = []
H_truth = pickle.load(open(haps_file,'rb'))
ploidy = len(H_truth)
with open(hpop_file,'r') as file:
    next(file)
    H = []
    for i in range(ploidy):
        H.append([])
    for row in file:
        #print(row)
        sp = row.split()
        if '#' in row or '*' in row:
            #print(row)
            #new block
            if len(H[0]) == 0:
                continue
            H_blocks.append(H)
            H = []
            for i in range(ploidy):
                H.append([])
            continue
        if not althap:
            ##New block
            if len(H[0]) == 0:
                num_lines_to_append = int(sp[0]) - end_of_block_last_block
                for l in range(num_lines_to_append-1):
                    for i in range(ploidy):
                        H[i].append(-1)
                if num_lines_to_append > 1:
                    print(row)

            for i in range(1,ploidy+1):
        #        print(sp[i],row)
                if sp[i] != '0' and sp[i] != '1' and sp[i] != '2' and sp[i] != '3':
                    H[i-1].append(-1)
                else:
                    H[i-1].append(int(sp[i]))
        else:
            for i in range(ploidy):
        #        print(sp[i],row)
                if sp[i] != '0' and sp[i] != '1' and sp[i] != '2' and sp[i] != '3':
                    H[i-1].append(-1)
                else:
                    H[i-1].append(int(sp[i]))
        end_of_block_last_block = int(sp[0])

    #for i in range(length_of_haplotype - len(H[0])):
    #    for j in range(ploidy):
    #        H[j].append(-1)
    #print(H)
#H_blocks.append(H)

hist = []
total_len = 0
truth_coords = 0
total_wrongeno = 0
for block in H_blocks:
    #print(block,len(block[0]))
    length_of_first_block = len(block[0])
    print(length_of_first_block)
    hist.append(length_of_first_block)
    total_len += length_of_first_block

    best_score = np.inf
    best_permut = None
    for permut in itertools.permutations(range(ploidy)):
        score = 0
        for i in range(ploidy):
            hap1 = block[i]
            hap2 = H_truth[permut[i]]
            start = 0
            end = length_of_first_block-1
            start2 = truth_coords
            end2 = truth_coords + end

            score += len([x+1 for x in np.nonzero((abs(np.array(hap1[start:end]) - np.array(hap2[start2:end2]))))][0])
        if score < best_score:
            best_score = score
            best_permut = permut

    #for i in range(ploidy):
    #    hap1 = block[i]
    #    hap2 = H_truth[best_permut[i]]
        #print([x+start+truth_coords+1 for x in np.nonzero((abs(np.array(hap1[start:end]) - np.array(hap2[start2:end2]))))])
    print(best_score)
    hamming_rate = best_score/ploidy

    genotype_dict_truth = defaultdict(lambda : defaultdict(int))
    for hap in H_truth:
        for i,allele in enumerate(hap):
            genotype_dict_truth[i+1][allele] += 1

    genotype_dict_test = defaultdict(lambda : defaultdict(int))
    for hap in block:
        for i,allele in enumerate(hap):
            genotype_dict_test[i+1+truth_coords][allele] += 1

    prev_perms = None
    num_wrong_geno = 0
    num_switch = 0
    for key in sorted(genotype_dict_test.keys()):
        #print(key)
        if genotype_dict_test[key] == genotype_dict_truth[key]:
            truth_list = []
            test_list = []
            for i in range(ploidy):
                test_list.append(block[i][key-1-truth_coords])
                truth_list.append(H_truth[i][key-1])
            #print(prev_perms,key,test_list,truth_list)
            current_perms = []
            for permut in itertools.permutations(range(ploidy)):
                if [test_list[i] for i in permut] == truth_list:
                    current_perms.append(permut)
            if prev_perms == None:
                prev_perms = tuple(current_perms)
            else:
#                if 100 > key and key > 1:
#                    print(current_perms,prev_perms,truth_list,test_list,key)
                if len(set(tuple(current_perms)).intersection(set(prev_perms))) > 0:
                    prev_perms = list(set(tuple(current_perms)).intersection(set(prev_perms)))
                    continue
                else:
                    print("SWITCH!",key)
                    prev_perms = current_perms
                    num_switch += 1
        else:
            print(key, 'WRONG GENO')
            num_wrong_geno +=1 
            prev_perms = None


    truth_coords += length_of_first_block
    print('Hamming rate : %s' % (hamming_rate/length_of_first_block))
    print('Num wrong geno: %s' % (num_wrong_geno))
    print('SWER: %s' % (num_switch))
    print('BLOCK LEN %s' % (length_of_first_block))
    total_ham_rate+= hamming_rate/length_of_first_block 
    total_swer += num_switch
    total_wrongeno += num_wrong_geno
#    if truth_coords > 2000:
#        break

print("Final hamming rate : %s" % (total_ham_rate/len(H_blocks)))
print("Final SWER : %s" % (total_swer))
print("Final  wrong geno : %s" % (total_wrongeno))
print(total_ham_rate,len(H_blocks),length_of_first_block)

N50_inter = 0
N50 = 0
truth_coords = 0
sorted_lengths = sorted(hist,reverse = True)
for l in sorted_lengths:
    N50_inter += l
    if N50_inter > total_len/2:
        N50 = l
        break

print(N50,'N50!!')
exit()


