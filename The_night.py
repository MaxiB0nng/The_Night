import pygame
import log
import story_functions as sf
import short_cut as cut
import choice_tree as tree
import cutsceen as sceen
import save_load as sl
import audio


pygame.init()
pygame.mixer.init()

#alle flag variabler
need_redraw = True #hvis den er sand så opdatere den skærmen 
choice = False


sf.image_make()
sf.make_canvas()
sf.redraw(sf.state)


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
                
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN and sf.allow_input:  # Space/enter tast blev trykke
                    if not sf.state == "running":
                        sf.text_valg()
                    need_redraw = True

                elif event.key == pygame.K_F11:
                    sf.fullscreen = not sf.fullscreen
                    if not sf.fullscreen:
                        sf.scale = 3
                    sf.make_screen()
                    need_redraw = True

                elif event.key == pygame.K_DOWN and sf.allow_input:
                    if tree.move_selceted:
                        tree.moveing("s")
                    else:
                        sf.valg += 1
                        if sf.valg  == 5:
                            sf.valg = 1
                    need_redraw = True

                elif event.key == pygame.K_UP and sf.allow_input:
                    if tree.move_selceted:
                        tree.moveing("w")
                    else:
                        sf.valg -= 1
                        if sf.valg == 0:
                            sf.valg = 4
                    need_redraw = True

                elif event.key == pygame.K_LEFT and sf.allow_input:
                    if tree.move_selceted:
                        tree.moveing("a")
                        need_redraw = True

                elif event.key == pygame.K_RIGHT and sf.allow_input:
                    if tree.move_selceted:
                        tree.moveing("d")
                        need_redraw = True
                        
                elif event.key == pygame.K_m:
                    sf.state = "menu"
                    cut.menu()
                    sf.redraw(sf.state)


                elif event.key == pygame.K_q:
                    running = False

#     ▄▄▄  ▄▄▄                               
#     ███  ███                               
#     ████████   ▄████▄   ██▄████▄  ██    ██ 
#     ██ ██ ██  ██▄▄▄▄██  ██▀   ██  ██    ██ 
#     ██ ▀▀ ██  ██▀▀▀▀▀▀  ██    ██  ██    ██ 
#     ██    ██  ▀██▄▄▄▄█  ██    ██  ██▄▄▄███ 
#     ▀▀    ▀▀    ▀▀▀▀▀   ▀▀    ▀▀   ▀▀▀▀ ▀▀ 

    if sf.state == "running":
        sf.cutsceen(sceen.startup_sequence,sceen.glitch,"menu",cut.menu)

    if sf.state == "menu":
        cut.menu()
        sf.choice_select("opening_cutsceen",None,
                         "settings",cut.settings,
                         "choice",cut.choice,
                         "quit",None)

    if sf.state == "settings":
        cut.settings()
        sf.choice_select("screen",cut.screen,
                         "music",cut.musik,
                         "credits",cut.credits,
                         "menu",cut.menu)

    if sf.state == "screen":
        cut.screen()
        if sf.selected_valg_2:
            sf.scale += 0.5
            if sf.scale >= 6:
                sf.scale = 6
            sf.make_screen()

        if sf.selected_valg_3:
            sf.scale -= 0.5
            if sf.scale <= 1:
                sf.scale = 1
            sf.make_screen()

        sf.choice_select(None,None,
                         None,cut.screen,
                         None,cut.screen,
                         "settings",cut.settings)

    if sf.state == "credits":
        sf.choice_select(None,None,
                         None,None,
                         None,None,
                         "settings",cut.settings)

    if sf.state == "music":
        sf.choice_select(None,None,
                         None,None,
                         None,None,
                         "settings",cut.settings)
    
    if sf.state == "choice":
        if sf.selected_valg_1:
            if tree.move_selceted:
                tree.move_selceted = False
            else:
                tree.move_selceted = True

        if sf.selected_valg_2:
            result = sl.load()
            if result:
                sf.chapter, sf.state, sl.visited = result
                sf.selected_valg_2 = False
                # call the shortcut for the loaded state to set up text/choices
                state_cuts = {
                    "H_kitchen": cut.H_kitchen,
                    "H_livingroom": cut.H_livingroom,
                    "H_room": cut.H_room,
                }
                if sf.state in state_cuts:
                    state_cuts[sf.state]()
                need_redraw = True


        if not sf.selected_valg_2:
            sf.choice_select(None,cut.choice,
                            None,None,
                            None,None,
                            "menu",cut.menu)
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


    if sf.state == "opening_cutsceen":
        sf.cutsceen(sceen.opening_cutsceen_list,sceen.opening_cutsceen,"H_livingroom",cut.H_continue)

    if sf.state == "H_kitchen":
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
            
    if sf.state == "H_look_for_food":
        if not sf.get_plot("item", "bun"):
            sf.plot_write("item", "bun", True)
        sf.cutsceen(sceen.H_look_for_food_cutsceen, sceen.H_look_for_food_img, "H_kitchen", cut.H_kitchen)

    if sf.state == "H_search_your_kitchen":
        if not sf.get_plot("item", "knife"):
            sf.plot_write("item", "knife", True)
        sf.cutsceen(sceen.H_search_your_kitchen_cutsceen, sceen.H_search_your_kitchen_img, "H_kitchen", cut.H_kitchen)

    if sf.state == "H_livingroom":
        sf.choice_select("H_sit_down",cut.H_sit_down,
                         "H_kitchen",cut.H_kitchen,
                         "H_room",cut.H_room,
                         None,None)

    if sf.state == "H_sit_down":
        sf.choice_select("H_livingroom",cut.H_livingroom,
                         "H_tv",None,
                         None,None,
                         None,None)

    if sf.state == "H_tv":
        sf.cutsceen(sceen.H_watch_tv_cutseen, sceen.H_watch_tv_img, "menu", cut.menu)
        if not sf.get_plot("plot", "alseep tv"):
            sf.plot_write("plot", "alseep tv", True)

    if sf.state == "H_room":
        if sf.get_plot("item","letter"):
            sf.choice_select("H_look_around",cut.H_look_around,
                            "H_lay_down",cut.H_lay_down,
                            None,None,
                            "H_livingroom",cut.H_livingroom)
        else:
            sf.choice_select("H_look_around",cut.H_look_around,
                            "H_lay_down",cut.H_lay_down,
                            "-",None,
                            "H_livingroom",cut.H_livingroom)

    if sf.state == "H_look_around":
        if not sf.get_plot("item", "letter"):
            sf.plot_write("item", "letter", True)
        sf.choice_select("H_room",cut.H_room,
                         None,None,
                         None,None,
                         None,None,)

    if sf.state == "H_lay_down":
        sf.choice_select("H_room",cut.H_room,
                         "H_fall_asleep",None,
                         None,None,
                         None,None,)

    if sf.state == "H_fall_asleep":
        sf.cutsceen(sceen.H_fall_asleep_cutsceen, sceen.H_fall_asleep_img, "menu", cut.menu)
        if not sf.get_plot("plot", "alseep tv"):
            sf.plot_write("plot", "alseep tv", True)

    if need_redraw:
        if sf.state == "choice":
            tree.choice_tree()
        if sf.state == "quit":
            running = False
        sf.redraw(sf.state)
        need_redraw = False

    clock.tick(30)

pygame.quit()