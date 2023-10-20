# This code replicates Figure 3 in the paper:
#
# Modeling Harmonic Similarity for Jazz Using Co-occurrence Vectors
# and the Membrane Area.  
#
# Please cite:
#
#   Bunks, C., Dixon, S., Weyde, T. and Di Giorgi, B., 2023. Modeling
#   Harmonic Similarity for Jazz Using Co-occurrence Vectors and the
#   Membrane Area. In Proceedings of the International Society for
#   Music Information Retrieval Conference (ISMIR), Milan, Italy, 2023.

import os
import sys
import re
import numpy as np
import pandas as pd
from ChordProgUtils import *
import ChordVecUtils as cvu

################################################################################
# Read in the curated list of contrafacts (and their corresponding
# originals).  This list was derived from the Wikipedia page of jazz
# contrafacts.  The songs available in the Impro-Visor corpus were
# identified and checked for errors.  Songs that are only partial
# contrafacts were removed.  The result is 80 contrafacts for 36
# original songs.
################################################################################

df = pd.read_csv('CONTRAFACT_DATA/contrafact_list.csv')
contrafacts = list(df.contrafacts)
originals= list(df.originals)
Ncontrafacts = len(contrafacts)

################################################################################
# Read in all the chord progression data
# NB: Songs are split across three subdirectories
################################################################################
songdb_paths = ['../SongDB/Songs[#,A-G]', '../SongDB/Songs[H-O]', '../SongDB/Songs[P-Z]']

################################################################################
# The chord progression for each song is converted to roman numeral
# notation.  This requires key estimation.  The entire corpus is
# structured into lists for the progressions (corpus_romans), the
# number of beats (corpus_meters) for each chord, and the song titles
# (corpus_titles).
################################################################################

corpus_romans = []
corpus_titles = []
corpus_meters = []
for sdb in songdb_paths:
    files = os.listdir(sdb)
    for f in files:
        song_name, composer, dbkey, timesig, nbars, progression = getsong(sdb+'/'+f)
        ranked_keys = estimatekey(timesig[0], progression)
        bestkey = ranked_keys[0][0]
        roman_prog = map2roman(bestkey, progression)
        beats = get_beats(timesig, roman_prog)
        corpus_romans.append(['<START>'] + strip_bars(roman_prog) + ['<END>'])
        corpus_meters.append([0] + beats + [0])
        corpus_titles.append(f)

################################################################################
# As per equation (1) in the paper cited above, compute the
# co-occurrence matrix, M, and normalize its rows.  The paper
# discusses several parameterizations of the co-occurrence matrix,
# including causal versus symmetric sliding windows, window size, and
# compressed versus raw chord progressions.  See paper for details.
################################################################################

win_size = 1
causal = False
cmpress = True
if causal == True:
    M, chord_idx = cvu.compute_causal_co_occurrence_matrix(corpus_romans, win_size)
elif cmpress == True:
    M, chord_idx = cvu.compute_compressed_co_occurrence_matrix(corpus_romans, win_size)
else:
    M, chord_idx = cvu.compute_co_occurrence_matrix(corpus_romans, win_size)
        
M = np.array([[item/np.linalg.norm(row) for item in row] for row in M])

ranks = []
rank_areas = []

# max_olen = max([len(k) for k in originals])
# max_clen = max([len(k) for k in contrafacts])
print('-'*80)
print('{:^5} {:<34} {:<33} {:>5}'.format('#/N','Contrafact File','Original File','Rank'))
print('-'*80)

################################################################################
# For each contrafact, compute the membrane area between it and each
# of the other songs in the corpus
################################################################################
for cfact_num, cfact_file in enumerate(contrafacts):
    # cfact_num is the index of the contrafact in the contrafact list
    # and cfact_file is the filename containing the data of that contrafact

    # orig_file is the filename containing the data of the original song
    orig_file = originals[cfact_num]

    # orig_corpus_index and cfact_corpus_index are the indices of the original and
    # contrafact in the corpus 
    orig_corpus_index = corpus_titles.index(orig_file)
    cfact_corpus_index = corpus_titles.index(cfact_file)
    cfact_title = corpus_titles[cfact_corpus_index]
    cfact_roman = corpus_romans[cfact_corpus_index]
    cfact_meter = corpus_meters[cfact_corpus_index]
    cfact_vecs = cvu.make_song_vecs(cfact_roman, chord_idx, M)

    areas = []
    for k in range(len(corpus_romans)):
        test_title = corpus_titles[k]
        if test_title == cfact_title:
            areas.append(-1)           # test is same as contrafact
            continue
        test_roman = corpus_romans[k]
        test_meter = corpus_meters[k]
        test_vecs = cvu.make_song_vecs(test_roman, chord_idx, M)
        area_k = cvu.compute_membrane_area(cfact_vecs, cfact_meter, test_vecs, test_meter)
        areas.append(area_k)

    # Find and save the rank of the original in the list of sorted
    # areas (and output it)
    sorted_idx_by_area = np.argsort(areas)
    sorted_areas = [areas[k] for k in sorted_idx_by_area]
    sorted_titles = [corpus_titles[k] for k in sorted_idx_by_area]
    this_rank = sorted_titles.index(orig_file)
    # Remember sorted_areas[0] is for the contrafact itself
    this_area = sorted_areas[this_rank]
    # Adjust for ties when area of original ties with another song (prefer original)
    adjusted_rank = sorted_areas.index(sorted_areas[this_rank]) 
    ranks.append(adjusted_rank)
    rank_areas.append(this_area)
    print('{:>5} {:<34} {:<33} {:>5}'.format(str(cfact_num)+'/'+str(Ncontrafacts-1),cfact_file,orig_file,adjusted_rank))
    
################################################################################
# Save data 
################################################################################

    fname = str(adjusted_rank).zfill(4)+'__'+orig_file.split('.')[0]+'__'+cfact_file
    f = open('EXPERIMENTAL_RESULTS/'+fname, 'w')
    for d, i in enumerate(sorted_idx_by_area):
        title_i = corpus_titles[i].split('.')[0]
        f.write(str(d) + '\t' + str(areas[i]) + '\t' + title_i + '\n')
    f.close()

################################################################################
# Output histogram and performance stats
################################################################################

import matplotlib.pyplot as plt
import statistics

best_rank = np.sort(ranks)
MIN, MAX = 1, np.max(best_rank)
bins = np.arange(1,MAX+5,1)
ax = plt.hist(best_rank, bins = bins, edgecolor='black')
plt.gca().set_xscale("log")
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Ranks')
plt.ylabel('Frequency')
plt.title('Distribution of Original Song Ranks')
median_rank = statistics.median(best_rank)
mean_rank = statistics.mean(best_rank)

plt.text(22, 12.7, 'Median Rank = '+str(int(median_rank)))
plt.plot([18,18],[0,20], 'r--')
plt.ylim([0,20])
plt.yticks(np.arange(0,20,2))
plt.grid(axis='x', alpha=0.75)
plt.grid(which='minor', color='#888888', linestyle=':', linewidth=0.5)

plt.show()


