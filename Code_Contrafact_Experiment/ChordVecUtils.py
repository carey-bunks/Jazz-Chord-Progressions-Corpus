import numpy as np
from itertools import groupby
from gensim.models import Word2Vec

def distinct_chords(corpus):
    """
    Return the set of unique chords in the corpus
    """
    corpus_words = []
    flat = [y for x in corpus for y in x]
    corpus_words = list(set(flat))
    corpus_words.sort()
    return corpus_words

def compress_sequence(chords):
    """This function takes a list of chords and the output is a list of
    tuples.  Each tuple represents a chord and the number of times
    that chord occurs contiguously in the input

    """

    grouped_chords = [(k, len(list(g))) for k, g in groupby(chords)]
    return grouped_chords

def compute_co_occurrence_matrix(corpus, window_size=2):
    """
    Return the co-occurrence matrix of the distinct chords based on the
    collection of songs in the corpus
    """
    words = distinct_chords(corpus)
    word_idx = dict(zip(words,range(len(words))))
    word2ind = {}
    for doc in corpus:
        # TODO: consider using compress_sequence(doc) before computing co-occurrence 
        N = len(doc)
        for c in range(N):
            wc = doc[c]
            wc_idx = word_idx[wc]
            window = list(range(max(0,c-window_size),c)) + list(range(c+1, min(N,c+window_size+1)))
            idx = []
            for o in window:
                wo = doc[o]
                wo_idx = word_idx[wo]
                idx = [wc_idx, wo_idx]
                if wc in word2ind:
                    word2ind[wc].append(idx)
                else:
                    word2ind[wc] = []
                    word2ind[wc].append(idx)
    K = len(words)
    M = np.zeros((K,K))
    for j in word2ind:
        for x, y in word2ind[j]:
            M[x][y] += 1
    return M, word_idx

def compute_word2vec_matrix(corpus, window_size=1):
    """
    Return the co-occurrence matrix of the distinct chords based on the
    collection of songs in the corpus
    """

    model = Word2Vec(sentences=corpus, vector_size=63, window=window_size, min_count=1, workers=4)

    words = distinct_chords(corpus)
    word_idx = dict(zip(words,range(len(words))))

    K = len(words)
    M = np.zeros((K,K))
    for j,w in enumerate(words):
        M[j] = model.wv[w]
    return M, word_idx

def compute_compressed_co_occurrence_matrix(corpus, window_size=2):
    """
    Return the co-occurrence matrix of the distinct chords based on the
    collection of songs in the corpus
    """
    words = distinct_chords(corpus)
    word_idx = dict(zip(words,range(len(words))))
    word2ind = {}
    for fulldoc in corpus:
        doctup = compress_sequence(fulldoc)
        doc = [k for k,j in doctup]
        N = len(doc)
        for c in range(N):
            wc = doc[c]
            wc_idx = word_idx[wc]
            window = list(range(max(0,c-window_size),c)) + list(range(c+1, min(N,c+window_size+1)))
            idx = []
            for o in window:
                wo = doc[o]
                wo_idx = word_idx[wo]
                idx = [wc_idx, wo_idx]
                if wc in word2ind:
                    word2ind[wc].append(idx)
                else:
                    word2ind[wc] = []
                    word2ind[wc].append(idx)
    K = len(words)
    M = np.zeros((K,K))
    for j in word2ind:
        for x, y in word2ind[j]:
            M[x][y] += 1
    return M, word_idx

def compute_causal_co_occurrence_matrix(corpus, window_size=2):
    """
    Return the co-occurrence matrix of the distinct chords based on the
    collection of songs in the corpus
    """
    words = distinct_chords(corpus)
    word_idx = dict(zip(words,range(len(words))))
    word2ind = {}
    for doc in corpus:
        # TODO: consider using compress_sequence(doc) before computing co-occurrence 
        N = len(doc)
        for c in range(N):
            wc = doc[c]
            wc_idx = word_idx[wc]
            window = list(range(max(0,c-window_size),c))
            idx = []
            for o in window:
                wo = doc[o]
                wo_idx = word_idx[wo]
                idx = [wc_idx, wo_idx]
                if wc in word2ind:
                    word2ind[wc].append(idx)
                else:
                    word2ind[wc] = []
                    word2ind[wc].append(idx)
    K = len(words)
    M = np.zeros((K,K))
    for j in word2ind:
        for x, y in word2ind[j]:
            M[x][y] += 1
    return M, word_idx

def make_song_vecs(song, chord_idx, M):
    """
    Return the sequence of vectors representing the chords in the song
    """
    sv = []
    for symbol in song:
        sv.append(M[chord_idx[symbol]])
    sv = np.array(sv)
    return sv

def vector_point(sample, vecs, meter):
    """
    Return the vector space point the distance along the song's
    piecewise linear representation corresponding to the value of
    sample in [0, 1]
    """
    cum_meter = np.cumsum(meter)
    normalized_position = cum_meter/cum_meter[-1]
    norm_meter = meter/cum_meter[-1]
    i = np.argwhere(normalized_position > sample)[0][0]
    delta = (sample - normalized_position[i-1])/(normalized_position[i] - normalized_position[i-1])
    point = np.matmul(norm_meter[:i], vecs[:i,:]) + delta * norm_meter[i] * vecs[i,:]
    return point

def compute_membrane_area(vec1,vals1,vec2,vals2):
    """
    Return the membrane area between two songs represented by 
    [vec1, vals1] and [vec2, vals2]
    """
    samples = np.linspace(0,1,256)[1:-1]

    E = 0
    for s in samples:
        p1 = vector_point(s, vec1, vals1)
        p2 = vector_point(s, vec2, vals2)
        E += np.linalg.norm(p1-p2)
    return E

