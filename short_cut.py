import story_functions as sf
import choice_tree as tree
import audio

def menu():
    sf.story_update("Welcome to The Night", "Case #19981112", "you can always press M to return to the main menu")
    sf.valg_update("Continue","Settings","Choice Tree - saves", "Quit")

def settings():
    sf.story_update("Settings", "-", "-")
    sf.valg_update("screen", "music", "credits", "back")

def music():

    sf.story_update("Music",f"Curently playing: {audio.music.current} ","-",)

    sf.valg_update("<- Change music ->",f"<- Volume {audio.music.volume} ->",f"<- Sound Fx {audio.soundfx.volume} ->","back",)

def credits():
    sf.story_update("Made by -Maxibonng"
                    ,"Special thanks: -Engineer_0001   -Likvik   -ArthurR2"
                    ,"-")
    sf.valg_update("-", "-", "-", "back")

def screen():
    if sf.valg == 1:
        sf.story_update("The screen is fixed at a 240x320 ratio",
                    f"the screen is  {sf.scaled_height}x{sf.scaled_width}", 
                    "-")
    elif sf.valg == 2:
        sf.story_update("Shaders is recomend ON","for better preformans turn OFF","-")
    else:
        sf.story_update("-","-","-")

    sf.valg_update(f"<- scale = {sf.scale} ->", f"shader {sf.shader_on}", "-", "back")


def choice():
    sf.story_update("Here you can see your progress in from of a tree", "-", f"Hint: {tree.hint}")
    if tree.move_selceted:
        sf.valg_update("Move On", "load","saves","Back")
    else:
        sf.valg_update("Move Off", "load","saves","Back")

#        ▄▄▄▄   ▄▄                                                                      ▄▄▄    
#      ██▀▀▀▀█  ██                              ██                                     █▀██    
#     ██▀       ██▄████▄   ▄█████▄  ██▄███▄   ███████    ▄████▄    ██▄████               ██    
#     ██        ██▀   ██   ▀ ▄▄▄██  ██▀  ▀██    ██      ██▄▄▄▄██   ██▀                   ██    
#     ██▄       ██    ██  ▄██▀▀▀██  ██    ██    ██      ██▀▀▀▀▀▀   ██                    ██    
#      ██▄▄▄▄█  ██    ██  ██▄▄▄███  ███▄▄██▀    ██▄▄▄   ▀██▄▄▄▄█   ██                 ▄▄▄██▄▄▄ 
#        ▀▀▀▀   ▀▀    ▀▀   ▀▀▀▀ ▀▀  ██ ▀▀▀       ▀▀▀▀     ▀▀▀▀▀    ▀▀                 ▀▀▀▀▀▀▀▀ 
#                                   ██                                                         
#                                ▄    ▄                     
#                                █    █  ▄▄▄   ▄▄▄▄▄   ▄▄▄  
#                                █▄▄▄▄█ █▀ ▀█  █ █ █  █▀  █ 
#                                █    █ █   █  █ █ █  █▀▀▀▀ 
#                                █    █ ▀█▄█▀  █ █ █  ▀█▄▄▀ 


def H_continue():
    sf.chapter = 1
    sf.story_update("You just got home","Your tired maybe get some sleep","-")
    sf.valg_update("Sit down in the couch","Go to your kitchen","Go to your room", "-")

def H_kitchen():
    if sf.get_plot("item", "knife") or sf.get_plot("item", "bun"):
        sf.story_update("The kitchen","-","-")
        sf.valg_update("-", "-", "Go to the living room", "-")   
    else:
        sf.story_update("The kitchen","You should probely eat",":IM NOT HUNGRY")
        sf.valg_update("Look for food", "Search your kitchen", "Go to the living room", "-")

def H_livingroom():
    sf.story_update("Home Sweet Home","Better then the office","-")
    sf.valg_update("Sit down in the couch","Go to your kitchen","Go to your room", "-")

def H_room():
    if sf.get_plot("item","letter"):
        sf.story_update("You walk into your room","Its a bit messy",":...")
        sf.valg_update("Look at letter","Lay down in your bed",
                       "-","Go to the living room")
    else:
        sf.story_update("You walk into your room","Its a bit messy",".")
        sf.valg_update("Look around your room","Lay down in your bed","-","Go to the living room")

def H_look_around():
    sf.story_update("It a letter from robbert", "-","-")
    sf.valg_update("put letter down","-","-","-")

def H_lay_down():
    sf.story_update("You lay in your bed", "-","-")
    sf.valg_update("Stand up","Go to sleep","-","-")

def H_sit_down():
    sf.story_update("Tired?","Maybe some TV can relax you?","-")
    sf.valg_update("Stand up","Watch som TV","-","-")

