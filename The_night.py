import pygame
import random
import log
import story_functions as sf
import short_cut as cut
import choice_tree as tree

pygame.init()
pygame.mixer.init()

#alle flag variabler
need_redraw = True #hvis den er sand så opdatere den skærmen 
choice = False


sf.image_make()
sf.make_canvas()
sf.redraw(sf.state)

# Spil-loop
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
                
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:  # Space/enter tast blev trykke
                    if not sf.state == "running":
                        sf.text_valg()
                    need_redraw = True

                elif event.key == pygame.K_F11:
                    sf.fullscreen = not sf.fullscreen
                    if not sf.fullscreen:
                        sf.scale = 3
                    sf.make_screen()
                    need_redraw = True

                elif event.key == pygame.K_DOWN:
                    if tree.move_selceted:
                        tree.moveing("s")
                    else:
                        sf.valg += 1
                        if sf.valg  == 5:
                            sf.valg = 1
                        print(sf.valg) 
                    need_redraw = True

                elif event.key == pygame.K_UP:
                    if tree.move_selceted:
                        tree.moveing("w")
                    else:
                        sf.valg -= 1
                        if sf.valg == 0:
                            sf.valg = 4
                        print(sf.valg)
                    need_redraw = True

                elif event.key == pygame.K_LEFT:
                    if tree.move_selceted:
                        tree.moveing("a")
                        need_redraw = True

                elif event.key == pygame.K_RIGHT:
                    if tree.move_selceted:
                        tree.moveing("d")
                        need_redraw = True
                        
                elif event.key == pygame.K_q:
                    sf.state = "menu"
                    print("pressed q")
                    sf.redraw(sf.state)
                elif event.key == pygame.K_m:
                    running = False

#     ▄▄▄  ▄▄▄                               
#     ███  ███                               
#     ████████   ▄████▄   ██▄████▄  ██    ██ 
#     ██ ██ ██  ██▄▄▄▄██  ██▀   ██  ██    ██ 
#     ██ ▀▀ ██  ██▀▀▀▀▀▀  ██    ██  ██    ██ 
#     ██    ██  ▀██▄▄▄▄█  ██    ██  ██▄▄▄███ 
#     ▀▀    ▀▀    ▀▀▀▀▀   ▀▀    ▀▀   ▀▀▀▀ ▀▀ 

    if sf.state == "running":
        sf.cutsceen(sf.startup_sequence,sf.glitch,"menu",cut.menu)

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
        
        sf.choice_select(None,cut.choice,
                        None,None,
                        None,None,
                        "menu",cut.menu)
#        ▄▄▄▄                                
#      ██▀▀▀▀█                               
#     ██         ▄█████▄  ████▄██▄   ▄████▄  
#     ██  ▄▄▄▄   ▀ ▄▄▄██  ██ ██ ██  ██▄▄▄▄██ 
#     ██  ▀▀██  ▄██▀▀▀██  ██ ██ ██  ██▀▀▀▀▀▀ 
#      ██▄▄▄██  ██▄▄▄███  ██ ██ ██  ▀██▄▄▄▄█ 
#        ▀▀▀▀    ▀▀▀▀ ▀▀  ▀▀ ▀▀ ▀▀    ▀▀▀▀▀  


    if sf.state == "opening_cutsceen":
        sf.cutsceen(sf.opening_cutsceen_list,sf.opening_cutsceen,"home_continue",cut.home_continue)

    if need_redraw:
        if sf.state == "choice":
            tree.choice_tree()
        if sf.state == "quit":
            running = False
        sf.redraw(sf.state)
        need_redraw = False

pygame.quit()