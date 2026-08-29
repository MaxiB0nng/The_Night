

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
    "H_sit_down",               # choice: sit down on couch, Livingroom / watch Tv
    "H_tv",                     # cutscene: watching tv, sets plot "alseep tv", goes to menu
    "H_room",                   # room: Look around / Lay down / Livingroom
    "H_look_around",            # cutscene (once, finds letter item), goes back to H_room
    "H_lay_down",               # choice: lay in bed, Room / fall asleep
    "H_fall_asleep",            # cutscene: falling asleep, sets plot "alseep tv", goes to menu
    "H_put_down",               # removed
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
H_continue (after opening cutscene) -> H_kitchen / H_livingroom / H_room

H_kitchen
  - Look for food      -> H_look_for_food (cutscene, sets item:bun)   -> back to H_kitchen
  - Search kitchen      -> H_search_your_kitchen (cutscene, sets item:knife) -> back to H_kitchen
  - Livingroom          -> H_livingroom
  (once bun or knife is found, the two search options are hidden - only Livingroom shows)

H_livingroom
  - Sit down    -> H_sit_down
  - Kitchen     -> H_kitchen
  - Room        -> H_room

H_sit_down
  - Livingroom  -> H_livingroom
  - Tv          -> H_tv (cutscene, sets plot:"alseep tv") -> menu

H_room
  - Look around -> H_look_around (cutscene, once only, sets item:letter) -> back to H_room
  - Lay down    -> H_lay_down
  - Livingroom  -> H_livingroom

H_lay_down
  - Room            -> H_room
  - Fall asleep     -> H_fall_asleep (cutscene, sets plot:"alseep tv") -> menu
"""


#                                                      
#     ▄▄▄▄▄               ▄▄                           
#     ██▀▀▀██             ██                           
#     ██    ██   ▄████▄   ██▄███▄   ██    ██   ▄███▄██ 
#     ██    ██  ██▄▄▄▄██  ██▀  ▀██  ██    ██  ██▀  ▀██ 
#     ██    ██  ██▀▀▀▀▀▀  ██    ██  ██    ██  ██    ██ 
#     ██▄▄▄██   ▀██▄▄▄▄█  ███▄▄██▀  ██▄▄▄███  ▀██▄▄███ 
#     ▀▀▀▀▀       ▀▀▀▀▀   ▀▀ ▀▀▀     ▀▀▀▀ ▀▀   ▄▀▀▀ ██ 
#                                              ▀████▀▀ 
#                                                      

"""


"""

#                                            
#     ▄▄▄▄▄▄▄▄                  ▄▄           
#     ▀▀▀██▀▀▀                  ██           
#        ██      ▄████▄    ▄███▄██   ▄████▄  
#        ██     ██▀  ▀██  ██▀  ▀██  ██▀  ▀██ 
#        ██     ██    ██  ██    ██  ██    ██ 
#        ██     ▀██▄▄██▀  ▀██▄▄███  ▀██▄▄██▀ 
#        ▀▀       ▀▀▀▀      ▀▀▀ ▀▀    ▀▀▀▀   
#                                            
#                                            

"""
1. lave soundfx V
2. menu V
3. save files V
4. choice_tree rework so it works whit save_file - in progress (choice_tree_v2.py, choice_tree.json)
5. crt tv shader
6. make shaders work on the gpu: no
"""