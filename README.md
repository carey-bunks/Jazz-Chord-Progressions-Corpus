# Jazz Chord Progressions Corpus
This repository contains a corpus of symbolic chord progressions similar to those found in jazz fake books such as the *Real Book*. The progressions are mainly from jazz 
standards, but also include some blues, jazz-blues, modal jazz, traditional songs, and pop tunes. At the moment, the corpus contains 2,612 songs, consisting of 134,182 chords, of 
which there are 1,542 unique symbols.  The database contains a handful of duplicate songs, differentiated by alternate harmonizations. This is the largest digital collection of jazz chord progressions the maintainer knows of, and will hopefully be of use to others working in the fields of music information retrieval, music informatics, and musicology.

The corpus is derived from a collection of files called the *Imaginary Book*, distributed with the open-source music notation program, *Impro-Visor* (see 
https://www.cs.hmc.edu/~keller/jazz/improvisor/). The Imaginary Book files were modified to retain music-specific content, removing control information needed only by the Impro-Visor application.  However, there are now significant differences between the Impro-Visor collection and this repository.  Many errors have been corrected, and missing information has been added. Moreover, a number of songs not in the Imaginary Book collection have been added by the maintainer of this repository -- contributions and corrections from others are welcome.

## Database Description
The SongDB directory contains all the songs in the corpus, one file per song.  Each song is contained in an ASCII formatted file whose name is derived from the title of the song.  To facilitate alphabetical search, articles such as *The* and *A* at the beginning of a song's title are not included in the filename.  Due to GitHub limitations, to allow each song in the database to be viewed through a browser, it was necessary limit the number of files in each subdirectory to less than 1,000.  For this reason, the database is partitioned into three collections of roughly 900 songs each.  The subdirectory Songs[#,A-G] contains songs whose titles begin with a number or the letters A-G; Songs[H-O] has the songs beginning with the letters H-O, and Songs[P-Z] contains those beginning with P-Z. 

## Content Description
Each chord progression is contained in its own file.  The first several lines of 
each file contain metadata consisting of the title, the name of the composer(s), the song's key and time signatures, and the total number of bars.  

The metadata is followed by the chord progression in symbolic form.  The progressions are fully written out, unwrapping any lead sheet abbreviations such as repeat symbols or multiple endings.  The progression is provided as four bars (or measures) per line, and each bar is terminated by a vertical "pipe" symbol (|).  The last bar of the song is also terminated in this way.  

The beats available in a bar are shared equally by the chords it contains. For example, a song with a 4/4 time signature gets four quarter notes per bar, and a bar containing *G7 CM7* would assign two quarter note beats to each chord.  Rhythmic variations are specified through the use of repeated chords and the no-chord symbol, *NC*, for example, a bar with *NC G7 CM7 CM7* would specify a beat of silence followed by a beat of G7 and two beats of CM7.

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
 
In addition to the song's title, Richard Rogers is identified as the composer, the key signature is F, the time signature is 4/4, and the completely written out song consists of 32 bars.  Each bar is terminated by the | symbol, including the last one.  Chords and pipes are separated from each other by a space.
