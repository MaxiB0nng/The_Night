import musicpy as mp


def the_night_theme():

    def make_rythem():
        global rythem

        main_3 = mp.chord(['G2', 'B2', 'F#3', 'B2'],
                    duration=1/8, interval=1/8)

        main_0 = mp.chord(['E2', 'B2', 'F#3', 'B2'],
                    duration=1/8, interval=1/8)

        rythem = main_3 * 4 | main_0 * 4
    def make_bass():
        global bass

        bass = mp.chord(["G2",'D2','E2','B2'],
                    duration=1, interval=1)
    def make_melody():
        global melody, melody_harmony

        d_phrase = mp.chord(
            ['E4', 'D4',   'F#4', 'E4'],
            duration= [3/8, 9/8, 2/8,  2/8,],
            interval= [3/8, 9/8, 2/8, 2/8,]
        )

        a_phrase = mp.chord(
            ['C#4', 'B3',   'D4',  'C#4'],
            duration= [3/8,  6/8, 2/4,  3/8],
            interval= [3/8,  6/8, 2/4,  3/8]
        )

        silence = mp.chord([mp.rest(4)], duration=1, interval=1)

        melody = (d_phrase | a_phrase) | silence
        melody_harmony = (d_phrase | a_phrase) - 12 - 7 | silence


    make_rythem()
    make_bass()
    make_melody()

    rythem_actuel = rythem * 4
    rythem_actuel.set_volume(100)

    bass_actuel = bass * 4
    bass_actuel.set_volume(100)

    melody_actuel = melody * 2
    melody_harmony_actuel = melody_harmony * 2

    melody_actuel.set_volume(80)
    melody_harmony_actuel.set_volume(60)

    song = mp.build(
        mp.track(rythem_actuel,         instrument=5, start_time=0),
        mp.track(bass_actuel,           instrument=35, start_time=0),
        mp.track(melody_actuel,         instrument=81, start_time=4),
        mp.track(melody_harmony_actuel, instrument=81, start_time=4),
        bpm=100
    )

    mp.write(song, name='music\The_night_theme.mid')
the_night_theme()


def home_theme():


    def make_guitar():
        global guitar_actuel
        def strum(notes, dur, vol):
            c = mp.chord(notes, duration=dur, interval=[0, 0, dur])
            c.set_volume(vol)
            return c

        def pattern(notes):
            s = strum
            return (s(notes, 1/4,  50) |
                    s(notes, 1/8,  50) |
                    s(notes, 1/16, 40) |
                    s(notes, 1/8,  50) |
                    s(notes, 1/16, 40) |
                    s(notes, 1/8,  50) |
                    s(notes, 1/8,  60)|
                    s(notes, 1/16, 40) |
                    s(notes, 1/8,  50) |
                    s(notes, 1/16, 40) |
                    s(notes, 1/8,  50) |
                    s(notes, 1/8,  60)|
                    s(notes, 1/16, 40) |
                    s(notes, 1/8,  50) |
                    s(notes, 1/16, 40) |
                    s(notes, 1/8,  50) |
                    s(notes, 1/8,  60)|
                    s(notes, 1/16, 40) |
                    s(notes, 1/16, 50))

        G_major = pattern(['G3', 'B3', 'D4'])   # G  B  D
        D_minor = pattern(['D3', 'F3', 'A3'])   # D  F  A  (form 2)
        A_major = pattern(['A3', 'C#4', 'E3'])  # A  C# E  (form 3)

        guitar_actuel = G_major | D_minor | A_major
    make_guitar()

    def make_bass():
        global bass_actuel

        bass_g = mp.chord(['G2'] * 12 + ['A2', 'G2'],
                        duration=[1/8] * 12 + [1/4, 1/4],
                        interval=[1/8] * 12 + [1/4, 1/4])
        
        bass_d = mp.chord(['D2'] * 12 + ['E2', 'D2'],
                        duration=[1/8] * 12 + [1/4, 1/4],
                        interval=[1/8] * 12 + [1/4, 1/4])
        
        bass_a = mp.chord(['A2'] * 12 + ['B2', 'A2'],
                        duration=[1/8] * 12 + [1/4, 1/4],
                        interval=[1/8] * 12 + [1/4, 1/4])



        bass_actuel = bass_g | bass_d |bass_a 
        bass_actuel.set_volume(120)

    make_bass()

    def make_syns():
        global syns_actuel

        G_major = mp.chord(['G4', 'B4', 'D5'],duration=1,interval=0)
        D_minor = mp.chord(['D4', 'F4', 'A4'],duration=1,interval=0)
        A_major = mp.chord(['A4', 'C#5', 'E5'],duration=1,interval=0)


        syns_actuel = G_major * 2 | D_minor * 2 | A_major * 2
        syns_actuel.set_volume(30)

    make_syns()
        

    
    song = mp.build(
        mp.track(guitar_actuel * 4,instrument=26, start_time=0),
        mp.track(bass_actuel * 4, instrument=34,start_time=0),
        mp.track(syns_actuel * 4, instrument=81, start_time=0),
        bpm=115
    )

    mp.write(song, name='music\Home_theme.mid')
home_theme()


