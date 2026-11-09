import story_functions as sf
import short_cut as cut
import audio

def load(call):
    global visited,tree_chapter,tree_state

    with open("save.tns", "r") as f:
            chapter_line = f.readline().strip()
            listeitem = f.readline().strip()
            listeevent = f.readline().strip()
            all_states_line = f.readline().strip()

    if call == "game_load":

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

        sf.state = state
        sf.chapter = chapter

        sf.redraw(sf.state)

        cut_funtion = getattr(cut, sf.state, None)
        if cut_funtion:
            cut_funtion()

    if call == "choice_tree":

        if ":" in chapter_line:
            chapter, tree_state = chapter_line.split(":")
            tree_chapter = int(chapter)
        else:
            return None
        
        visited = {}
        if all_states_line.startswith("all:"):
            raw = all_states_line[4:]
            for chunk in raw.split("."):
                if "/" in chunk:
                    ch, states_raw = chunk.split("/")
                    visited[int(ch)] = states_raw.strip("()").split(",")



        return visited,tree_chapter,tree_state
  
def get_max_chapter():
    with open("save.tns", "r") as f:
        f.readline()
        f.readline()
        f.readline()
        all_states_line = f.readline().strip()

    if not all_states_line.startswith("all:"):
        return 0

    raw = all_states_line[4:]
    chapters = [int(chunk.split("/")[0]) for chunk in raw.split(".") if "/" in chunk]
    return max(chapters) if chapters else 0

no_load_state = ["running","quit","settings","screen","credits","music","choice","skip"]
saveing = False

def save(chapter,state):

    saveing = True
    for no_load in no_load_state:
        if no_load == state:
            saveing = False

    if saveing == True:
        with open("save.tns", "r") as f:
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


        with open("save.tns", "w") as f:
            f.write(chapter_line + "\n")
            f.write(listeitem + "\n")
            f.write(listeevent + "\n")
            f.write(all_states + "\n")

        all_states = None
        saveing = False

#       ▄▄▄▄                                     ██                                  
#     ▄█▀▀▀▀█               ██        ██         ▀▀                                  
#     ██▄        ▄████▄   ███████   ███████    ████     ██▄████▄   ▄███▄██  ▄▄█████▄ 
#      ▀████▄   ██▄▄▄▄██    ██        ██         ██     ██▀   ██  ██▀  ▀██  ██▄▄▄▄ ▀ 
#          ▀██  ██▀▀▀▀▀▀    ██        ██         ██     ██    ██  ██    ██   ▀▀▀▀██▄ 
#     █▄▄▄▄▄█▀  ▀██▄▄▄▄█    ██▄▄▄     ██▄▄▄   ▄▄▄██▄▄▄  ██    ██  ▀██▄▄███  █▄▄▄▄▄██ 
#      ▀▀▀▀▀      ▀▀▀▀▀      ▀▀▀▀      ▀▀▀▀   ▀▀▀▀▀▀▀▀  ▀▀    ▀▀   ▄▀▀▀ ██   ▀▀▀▀▀▀  
#                                                                  ▀████▀▀           

def load_settings():

    with open("player.tnp", "r") as f:
        lines = f.readlines()

    musicvolume, soundfxvolume = map(int,lines[0].strip().split(":"))

    sf.shader_on = lines[1].strip()

    if lines[2].strip() == "fullscreen":
        sf.scale = 3
        sf.fullscreen = True
    else:
        sf.scale = float(lines[2].strip())
        sf.fullscreen = False


    audio.music.set_volume(musicvolume)
    audio.soundfx.set_volume(soundfxvolume)

    
def save_settings():

    lines = [
        f"{audio.music.volume}:{audio.soundfx.volume}\n",
        f"{sf.shader_on}\n",
        "fullscreen\n" if sf.fullscreen else f"{sf.scale}\n",
    ]

    with open("player.tnp", "w") as f:
        f.writelines(lines)


#   default files, used when a save file is missing or broken
default_save = ["0:menu", "item:[]", "plot:[]", "all:0/(menu)"]
default_settings = ["100:100", "ON", "3.0"]

def save_ok(lines):
    return (len(lines) >= 4
            and ":" in lines[0]
            and lines[1].startswith("item:")
            and lines[2].startswith("plot:")
            and lines[3].startswith("all:"))

def settings_ok(lines):
    if len(lines) < 3:
        return False
    try:
        music, soundfx = lines[0].split(":")
        int(music), int(soundfx)
        if lines[2] != "fullscreen":
            float(lines[2])
    except ValueError:
        return False
    return lines[1] in ("ON", "OFF")

def make_saves():
    for file, check, default in (("save.tns", save_ok, default_save),
                                 ("player.tnp", settings_ok, default_settings)):
        try:
            with open(file, "r") as f:
                lines = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            lines = []

        if not check(lines):
            with open(file, "w") as f:
                f.write("\n".join(default) + "\n")