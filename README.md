# Corpus of Jazz Chord Progressions
This repository contains a corpus of symbolic chord progressions similar to those found in jazz fake books, such as the Real Book. The progressions are mainly jazz 
standards, but also include some blues, jazz-blues, modal jazz, traditional, and pop tunes. At the moment, the corpus contains 2,612 songs, consisting of 134,182 chords, of 
which there are 1,542 unique symbols.  This is the largest collection of jazz chord progressions that we know of.  

The corpus is derived from a collection distributed with *Impro-Visor*, an open-source music notation program intended to help musicians learn improvisation (see 
https://www.cs.hmc.edu/~keller/jazz/improvisor/). Our modifications remove control information used by the Impro-Visor application, retaining the musical content, 
however, there are now significant differences between the Impro-Visor collection and this repository.  Many errors have been corrected, and missing information added. Morever, a number of songs not in the Impro-Visor collection have been added by the maintainer of this repository -- contributions from others are welcome (please take care to follow the format below).

## Content Description
Each chord progression is contained in its own file, the file name being derived from the song's title.  The data is in ASCII format, and the first several lines of 
each file contain meta-data, including the title, the name of the composer(s), the song's key and time signatures, and the total number of bars.  

The meta data is followed by the chord progression in symbolic form.  The progressions are fully written out, unwrapping any lead sheet abbreviations such as repeat 
symbols or multiple endings.  The progression is provided as four bars (or measures) per line, and each bar is terminated by a vertical "pipe" symbol (|).  The last bar of the song is also terminated in this way.  A bar can contain multiple chords.  A chord gets a beat value according to the time signature, and the number of other chords in the same bar.  For example, for a time signature 3 4 (three quarter notes per bar), a single chord in the bar would get three beats, and three chords in a bar would each get a single beat.  

An example of the contents for the song "Have You Met Miss Jones?" is illustrated here:

    Title = Have You Met Miss Jones
    ComposedBy = Richard Rodgers
    DBKeySig = F
    TimeSig = 4 4
    Bars = 32
    FM7 | F#o | Gm7 | C7 |
    Am7 | Dm7 | Gm7 | C7 |
    FM7 | F#o | Gm7 | C7 |
    Am7 | Dm7 | Cm7 | F7 |
    BbM7 | Abm7 Db7 | GbM7 | Em7 A7 |
    DM7 | Abm7 Db7 | GbM7 | Gm7 C7 |
    FM7 | F#o | Gm7 | C7 |
    Am7 D7 | Gm7 C7 | FM7 | FM7 |
 
In addition to the song's title, Richard Rogers is identified as the composer, the key signature is F, the time signature is 4/4, and the completely written out song consists of 32 bars.  Each bar is terminiated by the "|" symbol, including the last one.
