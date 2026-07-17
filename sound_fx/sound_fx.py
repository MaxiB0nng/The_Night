import musicpy as mp

def up():

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
        mp.track(note,instrument=82, start_time=0),
        mp.track(bass,instrument=35, start_time=0),
        bpm=100
    )
    
    mp.write(song, name='sound_fx/up.mid')

up()

def down():

    note = mp.chord(
            ['C#4',],
            duration=1/32,
            interval=1/32
        )
    
    bass = mp.chord(
            ['C#3',],
            duration=1/32,
            interval=1/32
        )

    song = mp.build(
        mp.track(note,instrument=82, start_time=0),
        mp.track(bass,instrument=35, start_time=0),
        bpm=100
    )
    
    mp.write(song, name='sound_fx/down.mid')

down()

def press():

    note = mp.chord(
            ['F#3',],
            duration=1/16,
            interval=1/16
        )
    
    bass = mp.chord(
            ['F#2',],
            duration=1/16,
            interval=1/16
        )

    song = mp.build(
        mp.track(note,instrument=82, start_time=0),
        mp.track(bass,instrument=35, start_time=0),
        bpm=100
    )
    
    mp.write(song, name='sound_fx/press.mid')

press()