import musicpy as mp

def up():

    note = mp.chord(
            ['A4',],
            duration=1/32,
            interval=1/32
        )
    
    bass = mp.chord(
            ['A3',],
            duration=1/32,
            interval=1/32
        )

    song = mp.build(
        mp.track(note,instrument=81, start_time=0),
        mp.track(bass,instrument=35, start_time=0),
        bpm=100
    )
    
    mp.write(song, name='sound_fx/up.mid')

up()

def down():

    note = mp.chord(
            ['G#4',],
            duration=1/32,
            interval=1/32
        )
    
    bass = mp.chord(
            ['G#3',],
            duration=1/32,
            interval=1/32
        )

    song = mp.build(
        mp.track(note,instrument=81, start_time=0),
        mp.track(bass,instrument=35, start_time=0),
        bpm=100
    )
    
    mp.write(song, name='sound_fx/down.mid')

down()

def press():

    note = mp.chord(
            ['F#3',],
            duration=1/8,
            interval=1/8
        )
    
    bass = mp.chord(
            ['F#2',],
            duration=1/8,
            interval=1/8
        )

    song = mp.build(
        mp.track(note,instrument=81, start_time=0),
        mp.track(bass,instrument=35, start_time=0),
        bpm=100
    )
    
    mp.write(song, name='sound_fx/press.mid')

press()