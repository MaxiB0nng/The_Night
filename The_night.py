import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import pygame
import log
import story_functions as sf
import short_cut as cut
import choice_tree as tree
import save_load as sl
import key

pygame.init()
pygame.mixer.init()
sf.setup()

import cutsceen as sceen
import audio

#alle flag variabler
need_redraw = True #hvis den er sand så opdatere den skærmen 
choice = False
left_right = True

# Spil-loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        # Lukning af spillet
        if event.type == pygame.QUIT:
            log.close = True
            log.log(None,None,None)
            running = False

        # Håndter KEYDOWN tastetryk
        if event.type == pygame.KEYDOWN:
            if key.controls(event):
                need_redraw = True

#     ▄▄▄  ▄▄▄                               
#     ███  ███                               
#     ████████   ▄████▄   ██▄████▄  ██    ██ 
#     ██ ██ ██  ██▄▄▄▄██  ██▀   ██  ██    ██ 
#     ██ ▀▀ ██  ██▀▀▀▀▀▀  ██    ██  ██    ██ 
#     ██    ██  ▀██▄▄▄▄█  ██    ██  ██▄▄▄███ 
#     ▀▀    ▀▀    ▀▀▀▀▀   ▀▀    ▀▀   ▀▀▀▀ ▀▀ 
    if sf.state == "skip":
        sf.cutsceen(sf.skip_sequence, None, sf.skip_target_state, sf.skip_target_cut)

    elif sf.chapter == 0:
        if sf.state == "running":
            sf.cutsceen(sceen.startup_sequence,sceen.glitch,"menu",cut.menu)

        elif sf.state == "menu":
            cut.menu()
            sf.choice_select("opening_cutsceen",None,
                            "settings",cut.settings,
                            "choice",cut.choice,
                            "quit",None)

        elif sf.state == "settings":
            cut.settings()
            sf.choice_select("screen",cut.screen,
                            "music",cut.music,
                            "credits",cut.credits,
                            "menu",cut.menu)

        elif sf.state == "screen":

            cut.screen()

            if sf.selected_valg_2:
                if sf.shader_on == "ON":
                    sf.shader_on = "OFF"
                
                elif sf.shader_on == "OFF":
                    sf.shader_on = "ON"

            sf.choice_select(None,None,
                            None,cut.screen,
                            None,None,
                            "settings",cut.settings)

        elif sf.state == "credits":
            sf.choice_select(None,None,
                            None,None,
                            None,None,
                            "settings",cut.settings)

        elif sf.state == "music":
            cut.music()
    
            sf.choice_select(None,None,
                            None,None,
                            None,None,
                            "settings",cut.settings)
        
        elif sf.state == "choice":
            cut.choice()
            if tree.is_load == False:
                tree.load()

            if sf.selected_valg_1:
                tree.move_selceted =  not tree.move_selceted

            sf.choice_select(None,cut.choice,
                            None,None,
                            None,None,
                            "menu",cut.menu)
            
        elif sf.state == "opening_cutsceen":
            sf.cutsceen(sceen.opening_cutsceen_list,sceen.opening_cutsceen,"H_continue",cut.H_continue)

#     ▄▄▄▄                                
#   ██▀▀▀▀█                               
#  ██         ▄█████▄  ████▄██▄   ▄████▄  
#  ██  ▄▄▄▄   ▀ ▄▄▄██  ██ ██ ██  ██▄▄▄▄██ 
#  ██  ▀▀██  ▄██▀▀▀██  ██ ██ ██  ██▀▀▀▀▀▀ 
#   ██▄▄▄██  ██▄▄▄███  ██ ██ ██  ▀██▄▄▄▄█ 
#     ▀▀▀▀    ▀▀▀▀ ▀▀  ▀▀ ▀▀ ▀▀    ▀▀▀▀▀  
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

    elif sf.chapter == 1:

        if sf.state == "H_continue":
            sf.state = "H_livingroom"

        elif sf.state == "H_kitchen":
            if sf.get_plot("item", "knife") or sf.get_plot("item", "bun"):
                sf.choice_select(None,None,
                                None,None,
                                "H_livingroom",cut.H_livingroom,
                                None,None)
            else:
                sf.choice_select("H_look_for_food",None,
                                "H_search_your_kitchen",None,
                                "H_livingroom",cut.H_livingroom,
                                None,None)
                
        elif sf.state == "H_look_for_food":
            if not sf.get_plot("item", "bun"):
                sf.plot_write("item", "bun", True)
            sf.cutsceen(sceen.H_look_for_food_cutsceen, sceen.H_look_for_food_img, "H_kitchen", cut.H_kitchen)

        elif sf.state == "H_search_your_kitchen":
            if not sf.get_plot("item", "knife"):
                sf.plot_write("item", "knife", True)
            sf.cutsceen(sceen.H_search_your_kitchen_cutsceen, sceen.H_search_your_kitchen_img, "H_kitchen", cut.H_kitchen)

        elif sf.state == "H_livingroom":
            sf.choice_select("H_sit_down",cut.H_sit_down,
                            "H_kitchen",cut.H_kitchen,
                            "H_room",cut.H_room,
                            None,None)

        elif sf.state == "H_sit_down":
            sf.choice_select("H_livingroom",cut.H_livingroom,
                            "H_tv",None,
                            None,None,
                            None,None)

        elif sf.state == "H_tv":
            sf.cutsceen(sceen.H_watch_tv_cutseen, sceen.H_watch_tv_img, "menu", cut.menu)
            if not sf.get_plot("plot", "alseep tv"):
                sf.plot_write("plot", "alseep tv", True)

        elif sf.state == "H_room":
            sf.choice_select("H_look_around",cut.H_look_around,
                            "H_lay_down",cut.H_lay_down,
                            None,None,
                            "H_livingroom",cut.H_livingroom)

        elif sf.state == "H_look_around":
            if not sf.get_plot("item", "letter"):
                sf.cutsceen(sceen.H_look_around_cutsceen,sceen.H_look_around_img, "H_room", cut.H_room)
                sf.plot_write("item", "letter", True)
            sf.choice_select("H_room",cut.H_room,
                            None,None,
                            None,None,  
                            None,None,)

        elif sf.state == "H_lay_down":
            sf.choice_select("H_room",cut.H_room,
                            "H_fall_asleep",None,
                            None,None,
                            None,None,)

        elif sf.state == "H_fall_asleep":
            sf.cutsceen(sceen.H_fall_asleep_cutsceen, sceen.H_fall_asleep_img, "menu", cut.menu)
            if not sf.get_plot("plot", "alseep tv"): 
                sf.plot_write("plot", "alseep tv", True)

#     ▄▄▄▄▄▄    ▄▄▄▄▄▄▄▄  ▄▄▄▄▄     ▄▄▄▄▄▄       ▄▄    ▄▄      ▄▄
#     ██▀▀▀▀██  ██▀▀▀▀▀▀  ██▀▀▀██   ██▀▀▀▀██    ████   ██      ██
#     ██    ██  ██        ██    ██  ██    ██    ████   ▀█▄ ██ ▄█▀
#     ███████   ███████   ██    ██  ███████    ██  ██   ██ ██ ██ 
#     ██  ▀██▄  ██        ██    ██  ██  ▀██▄   ██████   ███▀▀███ 
#     ██    ██  ██▄▄▄▄▄▄  ██▄▄▄██   ██    ██  ▄██  ██▄  ███  ███ 
#     ▀▀    ▀▀▀ ▀▀▀▀▀▀▀▀  ▀▀▀▀▀     ▀▀    ▀▀▀ ▀▀    ▀▀  ▀▀▀  ▀▀▀ 

    if need_redraw:
        if sf.state == "choice":
            tree.draw()
        elif sf.state != "choice":
            tree.is_load == False
        if sf.state == "quit":
            running = False
        sf.redraw(sf.state)
        need_redraw = False

    if sf.shader_on == "ON":
        sf.shader_tick += 1
        if sf.shader_tick >= sf.shader_rate:
            sf.shader_redraw()
            sf.shader_tick = 0

    clock.tick(30)
    
pygame.quit()