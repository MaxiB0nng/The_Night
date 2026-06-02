

"""Line 1 — current chapter and state


<chapter>:<state>
1:H_kitchen
Line 2 — indexes of item_list entries where happened == True


item:[<index>, <index>, ...]
item:[0, 2, 3]
Line 3 — indexes of plot_list entries where happened == True


plot:[<index>, <index>, ...]
plot:[]
Line 4 — all states visited, grouped by chapter


all:<chapter>/(<state>,<state>,...). <chapter>/(<state>,...)
all:1/(H_livingroom,H_kitchen,H_room).2/(H_room,H_kitchen)"""


#██████████████████████████████████████████████████████████████████████████████


state_list = [
    "running",                  # startup cutscene (boot sequence + glitch), goes to menu
    "menu",                     # main menu: Continue / Settings / Choice Tree / Quit
    "settings",                 # settings submenu: Screen / Music / Credits / Back
    "screen",                   # screen scale adjuster, back to settings
    "credits",                  # credits screen, back to settings
    "music",                    # music settings placeholder, back to settings
    "choice",                   # choice tree viewer, back to menu
    "opening_cutsceen",         # opening story cutscene (night drive), goes to H_continue
    "H_continue",               # after opening cutscene: Kitchen / Livingroom / Room
    "H_kitchen",                # kitchen: Look for food / Search kitchen / Livingroom
    "H_livingroom",             # livingroom: Sit down / Kitchen / Room
    "H_sit_down",               # cutscene: sitting down, goes back to H_livingroom
    "H_room",                   # room: Look around / Lay down / Put down / Livingroom
    "H_look_around",            # cutscene: looking around room, goes back to H_room
    "H_lay_down",               # cutscene: laying down, goes back to H_room
    "H_put_down",               # cutscene: putting down phone (needs phone item), goes back to H_room
    "H_look_for_food",          # cutscene: find bun item, goes back to H_kitchen
    "H_search_your_kitchen",    # cutscene: find knife item, goes back to H_kitchen
    "quit",                     # exits the game
]


#        ▄▄▄▄   ▄▄                                                                      ▄▄▄    
#      ██▀▀▀▀█  ██                              ██                                     █▀██    
#     ██▀       ██▄████▄   ▄█████▄  ██▄███▄   ███████    ▄████▄    ██▄████               ██    
#     ██        ██▀   ██   ▀ ▄▄▄██  ██▀  ▀██    ██      ██▄▄▄▄██   ██▀                   ██    
#     ██▄       ██    ██  ▄██▀▀▀██  ██    ██    ██      ██▀▀▀▀▀▀   ██                    ██    
#      ██▄▄▄▄█  ██    ██  ██▄▄▄███  ███▄▄██▀    ██▄▄▄   ▀██▄▄▄▄█   ██                 ▄▄▄██▄▄▄ 
#        ▀▀▀▀   ▀▀    ▀▀   ▀▀▀▀ ▀▀  ██ ▀▀▀       ▀▀▀▀     ▀▀▀▀▀    ▀▀                 ▀▀▀▀▀▀▀▀ 

"""
╔══════════════════════╗
║ H_livingroom         ║
║ continue             ║
║ try starting game!   ║
╚══════════════════════╝
           │
     ┌─────┼─────┐
     ▼     ▼     ▼
╔═══════════════════╗            ╔═══════════════════╗       ╔═══════════════════╗
║ H_kitchen         ║            ║ H_livingroom      ║       ║ H_room            ║
║ go to kitchen     ║            ║ go to living room ║       ║ go to your room   ║
║ look around       ║            ║ look around       ║       ║ look around       ║
╚═══════════════════╝            ╚═══════════════════╝       ╚═══════════════════╝
   │               │                      │                   │         │        │
   ▼               ▼                      ▼                   ▼         ▼        ▼
╔══════════════╗ ╔══════════════╗  ╔══════════════╗  ╔══════════╗╔══════════╗╔══════════╗
║ H_look_for   ║ ║ H_search_    ║  ║ H_sit_down   ║  ║H_look_   ║║H_put_    ║║H_lay_    ║
║ _food        ║ ║ your_kitchen ║  ║ sit down     ║  ║around    ║║down      ║║down      ║
║ look for bun ║ ║ find knife   ║  ║ couch        ║  ║letter    ║║phone     ║║in bed    ║
╚══════════════╝ ╚══════════════╝  ╚══════════════╝  ╚══════════╝╚══════════╝╚══════════╝
                                          │                                   │
                                          ▼                                   ▼
                                  ╔══════════════╗                   ╔══════════════╗
                                  ║ H_tv         ║                   ║ H_lay_down   ║
                                  ║ watch tv     ║                   ║ do to sleep  ║
                                  ╚══════════════╝                   ╚══════════════╝
                                          │                                   │
                                          ▼                                   ▼
                                  ╔══════════════╗                   ╔══════════════╗
                                  ║ asleep couch ║                   ║ asleep bed   ║
                                  ║ C.0-1.1.0    ║                   ║ C.0-1.1.1    ║
                                  ╚══════════════╝                   ╚══════════════╝
"""