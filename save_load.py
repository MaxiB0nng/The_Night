import story_functions as sf
import short_cut as cut
import audio


def load():
    global visited

    with open("save.tnp", "r") as f:
        chapter_line = f.readline().strip()
        listeitem = f.readline().strip()
        listeevent = f.readline().strip()
        all_states_line = f.readline().strip()

    if ":" in chapter_line:
        chapter, state = chapter_line.split(":")
        chapter = int(chapter)
    else:
        return None

    if ":" in listeitem: 
        _, indexes_str = listeitem.split(":")
        indexes_str = indexes_str.strip("[] ")
        if indexes_str:
            for i in indexes_str.split(","):
                idx = int(i.strip())
                name, ending, _ = sf.item_list[idx]
                sf.item_list[idx] = (name, ending, True)

    if ":" in listeevent:
        _, indexes_str = listeevent.split(":")
        indexes_str = indexes_str.strip("[] ")
        if indexes_str:
            for i in indexes_str.split(","):
                idx = int(i.strip())
                name, ending, _ = sf.plot_list[idx]
                sf.plot_list[idx] = (name, ending, True)

    visited = []
    if all_states_line.startswith("all:"):
        raw = all_states_line[4:]
        for chunk in raw.split("."):
            if "/" in chunk:
                _, states_raw = chunk.split("/")
                visited.extend(states_raw.strip("()").split(","))

    print()

    sf.state = state
    sf.chapter = chapter

    sf.redraw(sf.state)

    cut_fn = getattr(cut, sf.state, None)
    if cut_fn:
        cut_fn()



def load_settings():

    with open("save.tnp", "r") as f:
        lines = f.readlines()

    musicvolume, soundfxvolume = lines[4].split(":")

    musicvolume = int(musicvolume)
    soundfxvolume = int(soundfxvolume)

    sf.shader_on = lines[5].strip()

    if lines[6] == "fullscreen":
        sf.scale = 3
        sf.fullscreen = True
    else:
        sf.scale = float(lines[6].strip())


    audio.music.set_volume(musicvolume)
    audio.soundfx.set_volume(soundfxvolume)

    

def save(chapter,state):

    if chapter != 0 and state != "quit":
        with open("save.tnp", "r") as f:
            chapter_line = f.readline().strip()
            listeitem = f.readline().strip()
            listeevent = f.readline().strip()
            all_states = f.readline().strip()


        if ":" in chapter_line:
            chapter_save, state_save = chapter_line.split(":")
        else:
            chapter_save, state_save = 0, "start"
        chapter_save = chapter
        state_save = state
        chapter_line = f"{chapter_save}:{state_save}"


        item_index_list = []
        for i, (_, _, happened) in enumerate(sf.item_list):
            if happened == True:
                item_index_list.append(i)
        listeitem = f"item:{item_index_list}"

        
        plot_index_list = []
        for i, (_, _, happened) in enumerate(sf.plot_list):
            if happened == True:
                plot_index_list.append(i)
        listeevent= f"plot:{plot_index_list}"


        visited = {}
        if all_states.startswith("all:"):
            raw = all_states[4:]         
            for chunk in raw.split("."):
                if "/" in chunk:
                    ch, states_raw = chunk.split("/")
                    visited[ch] = states_raw.strip("()").split(",")

        ch_key = str(chapter)
        if ch_key not in visited:
            visited[ch_key] = []           
        if state not in visited[ch_key]:   
            visited[ch_key].append(state)

        parts = []
        for ch, states in visited.items():
            parts.append(f"{ch}/({','.join(states)})")
        all_states = "all:" + ".".join(parts)


        with open("save.tnp", "w") as f:
            f.write(chapter_line + "\n")
            f.write(listeitem + "\n")
            f.write(listeevent + "\n")
            f.write(all_states + "\n")


    with open("save.tnp", "r") as f:
        lines = f.readlines()

    lines[4] = f"{audio.music.volume}:{audio.soundfx.volume}\n" 
    lines[5] = f"{sf.shader_on}\n"
    if sf.fullscreen:
        lines[6] = "fullscreen"
    else:
        lines[6] = f"{sf.scale}\n"

    with open("save.tnp", "w") as f:
        f.writelines(lines)
