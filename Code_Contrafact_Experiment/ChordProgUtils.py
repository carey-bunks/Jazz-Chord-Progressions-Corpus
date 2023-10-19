import os
import re
from itertools import groupby
from texttable import Texttable

def display_prog(progression, bpl = 8):
    """Display the progression in tabular format to the terminal

    """

    t = Texttable()
    progression = [str(p) for p in progression]
    pstr = ' '.join(progression)
    bars = pstr.split(' | ')
    N = len(bars)
    data = []
    for k in range(0, N, bpl):
        data.append(bars[k:k+bpl])

    M = len(data[-1])
    if len(data[-1]) < bpl:
        data[-1] += ['-']*(bpl-M)
        
    t.set_cols_align(["c"]*bpl)
    t.add_rows(data, header = False)
    t.set_max_width(0)
    print(t.draw())
        
def convert2progression(timesig, data):
    """Convert the tuple (chords, beats) into a progression

    """

    # Remove the <START> and <END> tags from the chords and the zeros from the beats
    c = data[0][1:-1]
    b = data[1][1:-1]

    bnum = timesig[0]
    btype = timesig[1]

    cnt = 0
    progression = []
    for k,b in enumerate(b):
        cnt += b
        progression.append(c[k])
        if cnt%bnum == 0:
            progression.append('|')

    if progression[-1] == '|':
        progression.pop()
        
    return progression
        
def map2roman(songkey, progression):
    """Given a key and a chord progression (consisting of chords and bar
    separation symbols), map the progression to roman numeral notation

    """

    target = ['i', 'bii', 'ii', 'biii', 'iii', 'iv', 'bv', 'v', 'bvi', 'vi', 'bvii', 'vii']
    
    chordmap = {'C': ('C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'),
             'F': ('F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E'),
             'Bb': ('Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A'),
             'Eb': ('Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B', 'C', 'Db', 'D'),
             'Ab': ('Ab', 'A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G'),
             'Db': ('Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B', 'C'),
             'Gb': ('Gb', 'G', 'Ab', 'A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F'),
             'B': ('B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb'),
             'E': ('E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb'),
             'A': ('A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab'),
             'D': ('D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B', 'C', 'Db'),
             'G': ('G', 'Ab', 'A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb')}

    # Select the major scale corresponding to the reference key
    
    scale = chordmap[songkey]

    # Lemmatize the progression and extract the list of just chords
    # (without the bar symbols)
    
    normalized_prog = lemmatize(progression)
    chords = strip_bars(normalized_prog)

    # For each chord find the equivalent roman numeral corresponding
    # to the estimated key

    roman = []
    for c in chords:
        if c != 'NC' and c != '|':
            r = getroot(c)
            t = getclass(c)
            if re.search('o', t): t = 'o'
            if re.search('M|M7', t): t = 'M'
            if re.search('m|m7', t): t = 'm'
            if re.search('h|h7', t): t = 'h'
            roman.append(target[scale.index(r)] + t)
        else:
            roman.append(c)

    # Returm the result
    
    roman_prog = inject_bars(progression, roman)
    return roman_prog
    

def estimatekey(bpm, progression):

# Find the weighted major key of each chord (except diminished) and return the
# most frequent

    normalized_prog = lemmatize(progression)
    chords = strip_bars(normalized_prog)
    bars = ' '.join(progression).split(' | ')
    cpm = [len(b.split(' ')) for b in bars]  # chords per measure

    beats = []
    for b in cpm:
        m0 = [bpm/b for k in range(b)]
        beats += m0
    
# A major chord could come from two major scales
    
    major_dict = {
        'C':  ('C', 'G'),
        'F':  ('F', 'C'),
        'Bb': ('Bb', 'F'),
        'Eb': ('Eb', 'Bb'),
        'Ab': ('Ab', 'Eb'),
        'Db': ('Db', 'Ab'),
        'Gb': ('Gb', 'Db'),
        'B': ('B', 'Gb'),
        'E': ('E', 'B'),
        'A': ('A', 'E'),
        'D': ('D', 'A'),
        'G': ('G', 'D')
    }

# A minor chord could come from three major scales

    minor_dict = {
        'C': ('Bb', 'Ab', 'Eb'),
        'F': ('Eb', 'Db', 'Ab'),
        'Bb': ('Ab', 'Gb', 'Db'),
        'Eb': ('Db', 'B', 'Gb'),
        'Ab': ('Gb', 'E', 'B'),
        'Db': ('B', 'A', 'E'),
        'Gb': ('E', 'D', 'A'),
        'B': ('A', 'G', 'D'),
        'E': ('D', 'C', 'G'),
        'A': ('G', 'F', 'C'),
        'D': ('C', 'Bb', 'F'),
        'G': ('F', 'Eb', 'Bb')
    }

# A 7th chord could come from one major scale

    seven_dict = {
        'C': ('F',),
        'F': ('Bb',),
        'Bb': ('Eb',),
        'Eb': ('Ab',),
        'Ab': ('Db',),
        'Db': ('Gb',),
        'Gb': ('B',),
        'B': ('E',),
        'E': ('A',),
        'A': ('D',),
        'D': ('G',),
        'G': ('C',)
    }

# A m7b5 chord could come from one major scale
    
    half_dict = {
        'C': ('Db',),
        'F': ('Gb',),
        'Bb': ('B',),
        'Eb': ('E',),
        'Ab': ('A',),
        'Db': ('D',),
        'Gb': ('G',),
        'B': ('C',),
        'E': ('F',),
        'A': ('Bb',),
        'D': ('Eb',),
        'G': ('Ab',)
    }

# A five chord (eg, a power chord like C5) can belong to six major scales
    

    five_dict = {
        'C': ('C', 'Eb', 'F', 'G', 'Ab', 'Bb'),
        'F': ('C', 'Db', 'Eb', 'F', 'Ab', 'Bb'),
        'Bb': ('Db', 'Eb', 'F', 'Gb', 'Ab', 'Bb'),
        'Eb': ('Db', 'Eb', 'Gb', 'Ab', 'Bb', 'B'),
        'Ab': ('Db', 'Eb', 'E', 'Gb', 'Ab', 'B'),
        'Db': ('Db', 'E', 'Gb', 'Ab', 'A', 'B'),
        'Gb': ('Db', 'D', 'E', 'Gb', 'A', 'B'),
        'B': ('D', 'E', 'Gb', 'G', 'A', 'B'),
        'E': ('C', 'D', 'E', 'G', 'A', 'B'),
        'A': ('C', 'D', 'E', 'F', 'G', 'A'),
        'D': ('C', 'D', 'F', 'G', 'A', 'Bb'),
        'G': ('C', 'D', 'Eb', 'F', 'G', 'Bb')
    }
        
# Tabulate chord root populations

    majkey_frq = {item: 0 for item in major_dict}

    for k, c in enumerate(chords):
        w = beats[k]
        q = getclass(c);
        r = getroot(c);

        s = ()
        if q == '7':
            s = seven_dict[r]
        elif re.match('M7|M', q):
            s = major_dict[r]
        elif re.match('m7|m', q):
            s = minor_dict[r]
        elif q == 'h7':
            s = half_dict[r]
        elif q == '5':
            s = five_dict[r]

        for k in s:
            majkey_frq[k] += w
            
    sorted_majkeys = sorted(majkey_frq.items(), reverse = 1, key = lambda x: x[1])
    return sorted_majkeys
            
def lemmatize(progression):
    """Convert all slash chords, sus chords, major triads, and add9 chords
    to their functional equivalents

    """

    # Extract out all the chord symbols and their indicial positions
    # from the progression, skipping over the bar symbols

    chords = strip_bars(progression)

    # Map all chord symbols to an enharmonically unique set and
    # convert slashchords to a non-slash equivalent.  Both of these
    # operations can be performed without knowing the chords
    # neighboring context chords, and so is implemented as a list
    # comprehension.

    enharmonically_unique_chords = [map_enharmonic(k) for k in chords]
    deslashed_chords = [convert_slash(k) for k in enharmonically_unique_chords]

    # The following operations converting add9 triads, major triads,
    # and sus chords depend on chordal context.  To efficiently
    # process the chord sequences, all contiguous duplicate chord
    # symbols are compressed to a single tuple containing a single
    # instance of the duplicated chord and its number of repetitions

    compressed_chords = compress_sequence(deslashed_chords)
    out = compressed_chords[:]
    out = convert_add9(out)
    out = convert_major_triad(out)
    out = convert_sus_chord(out)

    # Expand the compressed chord sequence, and reinject it into the
    # progression
    
    disambiguated_chords = expand_sequence(out)
    disambiguated_progression = inject_bars(progression, disambiguated_chords)

    return disambiguated_progression

def map_enharmonic(chord):

    """The symbolic processing of chords is facilitated by the use of a
    single enharmonic representation.  This function normalizes all
    sharpened roots to their flattened alternatives.  It also
    normalizes Fb to E, E# to F, and Cb to B, and B# to C.  All other
    symbols (for example 'NC' and '|') are unchanged.

    """
    chord = re.sub(r'\s+', '', chord)
    chorddict = {
        'A':  'A',
        'B':  'B',
        'C':  'C',
        'D':  'D',
        'E':  'E',
        'F':  'F',
        'G':  'G',
        'Ab':  'Ab',
        'Bb':  'Bb',
        'Cb':  'B',
        'Db':  'Db',
        'Eb':  'Eb',
        'Fb':  'E',
        'Gb':  'Gb',
        'A#':  'Bb',
        'B#':  'C',
        'C#':  'Db',
        'D#':  'Eb',
        'E#':  'F',
        'F#':  'Gb',
        'G#':  'Ab',
        'NC':  'NC',
        '|':   '|'
        }

    # Split slash chords and polychords into two parts and process
    # each separarately
    
    slashchord = re.split(r'\/', chord)
    polychord = re.split(r'\\', chord)
    type = ''
    if len(slashchord) == 2:
        c0 = map_enharmonic(slashchord[0])
        c1 = map_enharmonic(slashchord[1])
        return c0 + '/' + c1
    elif len(polychord) == 2:
        c0 = map_enharmonic(polychord[0])
        c1 = map_enharmonic(polychord[1])
        return c0 + '\\' + c1
    elif re.match(r'[A-G](b|#)?', chord):
        m = re.match(r'([A-G](b|#)?)(.*)', chord)
        (root, accidental, type) = m.groups()
    else:
        root = chord
        type = ''

    chordn = chorddict[root] + type
    return chordn

def convert_slash(chord):
    """Slash chords are in the form X/Y, where the symbol to the left of
    the slash is a chord and the one to the right is a bass note.  The
    bass note has several potential interpretations: (1) as the root
    of a sus chord, (2) as the 7th of a triad, and (3) as an
    inversion, extension, or alteration of the chord.  This function
    analyzes the context and decides how to appropriately convert
    slash chords.

    """

    if re.search('/', chord):
        slashchord = chord
        [upperchord, bass] = re.split('/', slashchord)
        interval = getinterval(upperchord, bass)
        root = getroot(upperchord)
        quality = getclass(upperchord)
        
        # Check for triad case (major, minor, diminished, augmented).
        # - Major triads with a vii interval => M7
        # - Major triads with a bvii interval => 7
        # - Major triads with a ii interval => add9
        # - Minor triads with a vii interval => mM7
        # - Minor triads with a bvii interval => m7
        # - Minor triads with a ii interval => madd9
        # - Diminished triads with a vi interval => o7
        # - Diminished triads with a bvii interval => h7
        # - Augmented triads with a bvii interval => 7#5
        # - Augmented triads with a vii interval => M7#5

        # Check for 9sus4 and sus4b9 chords
        # -   Dm7/G => G9sus4
        # - Dm7b5/G => G7sus4b9
        # -     F/G => G9sus4
        # -    Fm/G => G7sus4b9

        if quality == 'M' and interval == 'vii':
            converted_chord = root + 'M7'
        elif quality == 'M' and interval == 'bvii':
            converted_chord = root + '7'
        elif quality == 'M' and interval == 'ii':
            converted_chord = root + '9sus4'
        elif quality == 'm' and interval == 'vii':
            converted_chord = root + 'mM7'
        elif quality == 'm' and interval == 'bvii':
            converted_chord = root + 'm7'
        elif quality == 'm' and interval == 'ii':
            converted_chord = root + '7sus4b9'
        elif quality == 'o' and interval == 'vi':
            converted_chord = root + 'o7'
        elif quality == 'o' and interval == 'bvii':
            converted_chord = root + 'm7b5'
        elif quality == '+' and interval == 'vii':
            converted_chord = root + 'M7#5'
        elif quality == '+' and interval == 'bvii':
            converted_chord = root + '7#5'
        elif quality == 'm7' and interval == 'iv':
            converted_chord = bass + '9sus4'
        elif quality == 'h7' and interval == 'iv':
            converted_chord = bass + 'sus4b9'
        else:
            converted_chord = upperchord
    elif re.search('\\\\', chord):
        polychord = chord
        [lowerchord, upperchord] = re.split('\\\\', polychord)
        converted_chord = upperchord
    else:
        converted_chord = chord
            
    return converted_chord
    
        
def compress_sequence(chords):
    """This function takes a list of chords and the output is a list of
    tuples.  Each tuple represents a chord and the number of times
    that chord occurs contiguously in the input

    """

    grouped_chords = [(k, len(list(g))) for k, g in groupby(chords)]
    return grouped_chords

def convert_add9(compressed):
    """An add9 chord is like a sus4 chord.  For example, Fadd9 is an
    inversion of F/G.  For the moment, this will be treated like a sus
    chord, and managed in the function dedicated to sus chords.  This
    might change later.

    """

    ninth_dict = {
             'C':  'D',
             'Db': 'Eb',
             'D':  'E',
             'Eb': 'F',
             'E':  'Gb',
             'F':  'G',
             'Gb': 'Ab',
             'G':  'A',
             'Ab': 'Bb',
             'A':  'B',
             'Bb': 'C',
             'B':  'Db'
    }

    N = len(compressed)
    for k in range(N):
        c1 = compressed[k][0]
        r1 = getroot(c1)
        q1 = getclass(c1)
        reps = compressed[k][1]
        if q1 == 'add9':
            newc = ninth_dict[r1] + '9sus4'
            compressed[k] = (newc, reps)
        elif q1 == 'madd9':
            newc = ninth_dict[r1] + 'sus4b9'
            compressed[k] = (newc, reps)

    return compressed
    
def convert_sus_chord(compressed):
    """Sus4 chords can function as subdominant chords when they precede a
    dominant7 chord down by a fifth or a semi-tone (like a tritone
    substitution). Otherwise they map to a dominant7.  This function
    detects and replaces the sus chords that can be mapped to a
    subdominant.  All others map to a dominant7 chord.  The input is a
    compressed list of tuples.  Sus2 chords are first mapped to sus4
    chords by an inversion, and sus24 chords map to sus4 chords.

    Population of sus chord in the corpus and mapping rules:

    sus2 [6]                           => becomes a sus4 by inversion
    sus4 [1091], sus [199], sus24 [15] => becomes 7 or m7 per the following chord
    sus4b9 [18], susb9 [10]            => becomes 7b9 or m7b5 per the following chord

    """
    
    fifth_dict = {
             'C':  'F',
             'Db': 'Gb',
             'D':  'G',
             'Eb': 'Ab',
             'E':  'A',
             'F':  'Bb',
             'Gb': 'B',
             'G':  'C',
             'Ab': 'Db',
             'A':  'D',
             'Bb': 'Eb',
             'B':  'E'
    }
    
    fourth_dict = {
              'F':  'C',
              'Gb': 'Db',
              'G':  'D', 
              'Ab': 'Eb',
              'A':  'E', 
              'Bb': 'F', 
              'B':  'Gb',
              'C':  'G', 
              'Db': 'Ab',
              'D':  'A', 
              'Eb': 'Bb',
              'E':  'B',
        }

    semitone_dict = {
             'C':  'B',
             'Db': 'C',
             'D':  'Db',
             'Eb': 'D',
             'E':  'Eb',
             'F':  'E',
             'Gb': 'F',
             'G':  'Gb',
             'Ab': 'G',
             'A':  'Ab',
             'Bb': 'A',
             'B':  'Bb'
    }

    # Map all sus2 chords to their sus4 inversions
    for k, cc in enumerate(compressed):
        if re.search('sus2$', cc[0]):
            c = cc[0]
            r = getroot(c)
            sub = fourth_dict[r] + 'sus4'
            compressed[k] = (sub, cc[1])

    # Map all sus24 chords to sus4 
    for k, cc in enumerate(compressed):
        if re.search('sus24', cc[0]):
            c = cc[0]
            sub = c.replace('sus24', 'sus4')
            compressed[k] = (sub, cc[1])

    # search for (7|9|13)?sus4?
    # - convert to 7 or m
    # search for (7|7b9)?sus4?(b9|b13|b9b13)
    # - convert to 7b9 or m7b5
            
    N = len(compressed)
    extended = compressed[:]
    extended.append(compressed[0])
    for k in range(N):
        c1 = extended[k][0]
        c2 = extended[k+1][0]
        r1 = getroot(c1)
        r2 = getroot(c2)
        q1 = getclass(c1)
        q2 = getclass(c2)
        if q1 == 'sus' and fifth_dict[r1] == r2  and q2 == 'M':
            newc = r1 + '7'
            compressed[k] = (newc, compressed[k][1])
        elif q1 == 'sus' and semitone_dict[r1] == r2  and q2 == 'M':
            newc = r1 + '7'
            compressed[k] = (newc, compressed[k][1])
        elif q1 == 'sus' and fifth_dict[r1] == r2  and q2 == 'm':
            newc = r1 + '7b9'
            compressed[k] = (newc, compressed[k][1])
        elif q1 == 'sus' and semitone_dict[r1] == r2  and q2 == 'm':
            newc = r1 + '7b9'
            compressed[k] = (newc, compressed[k][1])
        elif q1 == 'sus' and r1 == r2  and q2 == '7':
            newc = fourth_dict[r1] + 'm7'
            compressed[k] = (newc, compressed[k][1])
        elif q1 == 'sus' and r1 == r2  and q2 == '7b9':
            newc = fourth_dict[r1] + 'm7b5'
            compressed[k] = (newc, compressed[k][1])
        elif q1 == 'sus':
            newc = r1 + '7'
            compressed[k] = (newc, compressed[k][1])

    return compressed

def convert_major_triad(compressed):
    """Major triads can function as dominant7 chords when they precede a
    major7 or minor7 that is down a fifth or down a semi-tone (like a
    tritone substitution).  This function detects the major triads
    that can be mapped to dominant7 chords.  All others map to a
    major7 chord.  The input is a compressed list of tuples.

    """
    
    fifth_dict = {
             'C':  'F',
             'Db': 'Gb',
             'D':  'G',
             'Eb': 'Ab',
             'E':  'A',
             'F':  'Bb',
             'Gb': 'B',
             'G':  'C',
             'Ab': 'Db',
             'A':  'D',
             'Bb': 'Eb',
             'B':  'E'
    }
    
    semitone_dict = {
             'C':  'B',
             'Db': 'C',
             'D':  'Db',
             'Eb': 'D',
             'E':  'Eb',
             'F':  'E',
             'Gb': 'F',
             'G':  'Gb',
             'Ab': 'G',
             'A':  'Ab',
             'Bb': 'A',
             'B':  'Bb'
    }

    N = len(compressed)
    extended = compressed[:]
    extended.append(compressed[0])
    for k in range(N):
        c1 = extended[k][0]
        reps = compressed[k][1]
        c2 = extended[k+1][0]
        r1 = getroot(c1)
        r2 = getroot(c2)
        q1 = getclass(c1)
        q2 = getclass(c2)
        if q1 == 'MT' and fifth_dict[r1] == r2  and q2 == 'M':
            newc = r1 + '7'
            compressed[k] = (newc, reps)
        elif q1 == 'MT' and fifth_dict[r1] == r2  and q2 == 'MT':
            newc = r1 + '7'
            compressed[k] = (newc, reps)
        elif q1 == 'MT' and semitone_dict[r1] == r2  and q2 == 'M':
            newc = r1 + '7'
            compressed[k] = (newc, reps)
        elif q1 == 'MT' and semitone_dict[r1] == r2  and q2 == 'MT':
            newc = r1 + '7'
            compressed[k] = (newc, reps)
        elif q1 == 'MT' and fifth_dict[r1] == r2  and q2 == 'm':
            newc = r1 + '7b9'
            compressed[k] = (newc, reps)
        elif q1 == 'MT' and semitone_dict[r1] == r2  and q2 == 'm':
            newc = r1 + '7b9'
            compressed[k] = (newc, reps)
        elif q1 == 'MT':
            newc = r1 + 'M7'
            compressed[k] = (newc, reps)

    return compressed

def inject_bars(progression, symbols):
    """Create a symbol progression by injecting the input symbols into a
       structure with the same bar separators as the input progression

    """

    indices = [k for k in range(len(progression)) if progression[k] != '|']
    symbol_prog = progression[:] 
    for k, s in zip(indices, symbols):
        symbol_prog[k] = s

    return symbol_prog

def expand_sequence(compressed_chords):
    """Expand a compressed chord sequence.  The input is a list of tuples
       where the first element of the tuple gives a chord and the
       second one the number of times that chord is to be contiguously
       repeated in the output

    """
    
    output_chord_sequence = []
    for k in compressed_chords:
        for n in range(k[1]):
            output_chord_sequence.append(k[0])

    return output_chord_sequence

def strip_bars(progression):
    """The input is a progression, a list of symbols within bar
    separators.  The output is an extracted list of just symbols.

    """

    symbols = [s for s in progression if s != '|']
    return symbols

def getinterval(chord1, chord2):
    r1 = getroot(chord1)
    r2 = getroot(chord2)
    chromatic = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    interval = ['0', 'bii', 'ii', 'biii', 'iii', 'iv', 'bv', 'v', 'bvi', 'vi', 'bvii', 'vii']
    b1 = chromatic.index(r1)
    b2 = chromatic.index(r2)
    delta = b2 - b1
    if delta < 0: delta += 12
    return interval[delta]

def getroot(chord):
    if chord != 'NC':
        m = re.match('([A-G]b?)', chord)
        root = m.groups()[0]
    else:
        root = chord
    return root

def getclass(chord):
    """Determine the class the input chord belongs to.  The result is one
    of the five 7th chords types (M7, 7, m7, h7, o7) or one of the
    four triads types (M, m, +, o).  Power chords (5) and no-chord
    (NC) each get a class type, and there is a return for unknown
    symbols (U).  Extensions and alterations have no effect on the
    result.

    """

    # The order of the tests is important (e.g., 7sus4 vs 7)
    
    if re.match('^[A-G]b?(m7b5|h7)', chord):
        chordclass = 'h'
    elif re.match('^[A-G]b?(7|9|13)?sus4?', chord):
        chordclass = '7'
    elif re.match('^[A-G]b?maj(7|9|11|13)', chord):
        chordclass = 'M'
    elif re.match('^[A-G]b?(M|M7|M9|2|6|69)', chord):
        chordclass = 'M'
    elif re.match('^[A-G]b?m(M|Maj)?(7|9|11|13|6|b6|69)', chord):
        chordclass = 'm'
    elif re.match('^[A-G]b?(o|dim)M?7', chord):
        chordclass = 'o'
    elif re.match('^[A-G]b?(7sus4b9|7sus4b9b13|7b9sus4|susb9)', chord):
        chordclass = '7'
    elif re.match('^[A-G]b?(7|9|11|13|7alt|7\+)', chord):
        chordclass = '7'
    elif re.match('^[A-G]b?$', chord):
        chordclass = 'M'
    elif re.match('^[A-G]b?m', chord):
        chordclass = 'm'
    elif re.match('^[A-G]b?(4|phryg)', chord):
        chordclass = 'm'
    elif re.match('^[A-G]b?(\+|aug)', chord):
        chordclass = '7'
    elif re.match('^[A-G]b?(o|dim)$', chord):
        chordclass = 'o'
    elif re.match('^[A-G]b?addb?9', chord):
        chordclass = 'M'
    elif re.match('^[A-G]b?maddb?9', chord):
        chordclass = 'm'
    elif re.match('^[A-G]b?5$', chord):
        chordclass = 'M'
    elif chord == 'NC':
        chordclass = 'NC'
    else:
        chordclass = 'U'
    return chordclass

def getsong(song):
    """Given a song filename, import the song's data, and make its
    contents available as variables

    """
    data = open(song, 'r')
    data = [l.rstrip() for l in data]
    data = [re.sub('\s+', ' ', l) for l in data]
    
    title = re.split(r' = ', data[0])[1]
    composedby = re.split(r' = ', data[1])[1]
    dbkeysig = re.split(r' = ', data[2])[1]
    timesig = re.split(r' = ', data[3])[1]
    timesig = re.split(r'\s+', timesig)
    timesig = [int(k) for k in timesig]
    nbars = int(re.split(r' = ', data[4])[1])
    
    prog = ' '.join(data[5:])
    prog = re.sub(r'^\s+', '', prog)
    prog = re.sub(r'\s+\|\s*$', '', prog)
    prog = prog.split()
    
    return title, composedby, dbkeysig, timesig, nbars, prog

def findsong(search_term):
    """Input is string containing tokens separated by white space.  Result
    is list of songs that contain all the tokens.  Example: 
    
    song = findsong('gre do') 
    print(song) 
    'SongDB/OnGreenDolphinStreet.txt'

    """
    terms = search_term.split()
    allsongs = os.listdir('SongDB')
    lst = []
    for t in terms:
        idx = {k for k in range(len(allsongs)) if re.search(t, allsongs[k], re.IGNORECASE)}
        lst.append(idx)
    res = list(lst[0].intersection(*lst))
    if len(res) == 1:
        song = allsongs[res[0]]
    elif len(res) > 1:
        for i, j in enumerate(res):
            print(i, allsongs[j])
        choice = int(input('\nSong number? '))
        song = allsongs[res[choice]]
    else:
        print('\n ==> Search term ambiguous\n')

    return song

def get_beats(timesig, roman):
    bpm = timesig[0]
    btyp = timesig[1]
    pstr = ' '.join(roman)
    bars = pstr.split(' | ')
    
    beats = []
    for bk in bars:
        symbols = bk.split()
        Ns = len(symbols)

        if bpm == 4 and btyp == 4:
            if Ns == 1:
                beats.append(4)
            elif Ns == 2:
                beats += [2, 2]
            elif Ns == 4:
                beats += [1, 1, 1, 1]
            elif Ns == 8:
                beats += [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
            elif Ns == 6:
                beats += [0.75, 0.75, 0.75, 0.75, 0.75, 0.75]
            elif Ns == 5:
                beats += [0.8, 0.8, 0.8, 0.8, 0.8]
            elif Ns == 3:
                beats += [2, 1, 1]
            elif Ns == 12:
                beats += [0.33, 0.33, 0.33, 0.33, 0.33, 0.33, 0.33, 0.33, 0.33, 0.33, 0.33, 0.33]
            elif Ns == 16:
                beats += [0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25]
        elif bpm == 3 and btyp == 4:
            if Ns == 1:
                beats.append(3)
            elif Ns == 2:
                beats += [1, 2]
            elif Ns == 3:
                beats += [1, 1, 1]
        elif bpm == 6 and btyp == 8:
            if Ns == 2:
                beats += [3, 3]
            elif Ns == 3:
                beats += [2, 2, 2]
            elif Ns == 1:
                beats.append(6)
        elif bpm == 2 and btyp == 4:
            if Ns == 1:
                beats.append(2)
            elif Ns == 2:
                beats += [1, 1]
            elif Ns == 4:
                beats += [0.5, 0.5, 0.5, 0.5]
        elif bpm == 6 and btyp == 4:
            if Ns == 3:
                beats += [2, 2, 2]
            elif Ns == 2:
                beats += [3, 3]
            elif Ns == 1:
                beats.append(6)
            elif Ns == 6:
                beats += [1, 1, 1, 1, 1, 1]
            elif Ns == 12:
                beats += [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
        elif bpm == 5 and btyp == 4:
            if Ns == 5:
                beats += [1, 1, 1, 1, 1]
            elif Ns == 1:
                beats.append(5)
            elif Ns == 4:
                beats += [1.25, 1.25, 1.25, 1.25]
        elif bpm == 2 and btyp == 2:
            if Ns == 1:
                beats.append(2)
            elif Ns == 2:
                beats += [1, 1]
            elif Ns == 4:
                beats += [0.5, 0.5, 0.5, 0.5]
        elif bpm == 12 and btyp == 8:
            if Ns == 1:
                beats.append(12)
            elif Ns == 2:
                beats += [6, 6]
        elif bpm == 7 and btyp == 4:
            if Ns == 7:
                beats += [1, 1, 1, 1, 1, 1, 1]
            elif Ns == 1:
                beats.append(7)
        elif bpm == 3 and btyp == 2:
            if Ns == 1:
                beats.append(3)
            elif Ns == 2:
                beats += [1.5, 1.5]
            elif Ns == 6:
                beats += [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
            elif Ns == 12:
                beats += [0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25]
        elif bpm == 11 and btyp == 4:
            if Ns == 11:
                beats += [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            elif Ns == 1:
                beats.append(11)
        elif bpm == 10 and btyp == 4:
            if Ns == 10:
                beats += [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            elif Ns == 2:
                beats += [5, 5]
            elif Ns == 1:
                beats.append(10)

    return beats

def transpose2C(songkey, progression):
    # Transpose a song to a new key

    chordmap = {}
    chordmap['C'] = 'C.Db.D.Eb.E.F.Gb.G.Ab.A.Bb.B'
    chordmap['F'] = 'F.Gb.G.Ab.A.Bb.B.C.Db.D.Eb.E'
    chordmap['Bb'] = 'Bb.B.C.Db.D.Eb.E.F.Gb.G.Ab.A'
    chordmap['Eb'] = 'Eb.E.F.Gb.G.Ab.A.Bb.B.C.Db.D'
    chordmap['Ab'] = 'Ab.A.Bb.B.C.Db.D.Eb.E.F.Gb.G'
    chordmap['Db'] = 'Db.D.Eb.E.F.Gb.G.Ab.A.Bb.B.C'
    chordmap['Gb'] = 'Gb.G.Ab.A.Bb.B.C.Db.D.Eb.E.F'
    chordmap['B'] = 'B.C.Db.D.Eb.E.F.Gb.G.Ab.A.Bb'
    chordmap['E'] = 'E.F.Gb.G.Ab.A.Bb.B.C.Db.D.Eb'
    chordmap['A'] = 'A.Bb.B.C.Db.D.Eb.E.F.Gb.G.Ab'
    chordmap['D'] = 'D.Eb.E.F.Gb.G.Ab.A.Bb.B.C.Db'
    chordmap['G'] = 'G.Ab.A.Bb.B.C.Db.D.Eb.E.F.Gb'

    chords = strip_bars(progression)

    orig_key_array = chordmap[songkey].split('.')
    transpose_array = chordmap['C'].split('.')

    transpose_chords = []
    pat = re.compile('([A-G](b|#)?)(.*)')
    for c in chords:
        if '/' in c:
            chord_top, bass_note = c.split('/')
            cn = map_enharmonic(chord_top)
            bn = map_enharmonic(bass_note)
            matches = re.search(pat, cn)
            r = matches[1]
            t = matches[3]
            transposed_top = transpose_array[orig_key_array.index(r)] + t
            matches = re.search(pat, bn)
            r = matches[1]
            t = matches[3]
            transposed_bass = transpose_array[orig_key_array.index(r)] + t
            transposed_chord = transposed_top + '/' + transposed_bass
            transpose_chords.append(transposed_chord)
        elif c != 'NC':
            cn = map_enharmonic(c)
            matches = re.search(pat, cn)
            r = matches[1]
            t = matches[3]
            transposed_chord = transpose_array[orig_key_array.index(r)] + t
            transpose_chords.append(transposed_chord)
        else:
            transpose_chords.append(c)

    transposed_progression = inject_bars(progression, transpose_chords)

    return transposed_progression


            
