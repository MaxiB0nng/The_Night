import pygame
import random
import log
import story_functions as sf
import short_cut as sc
from choice_tree import choice_tree

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
                    sf.text_valg()
                    need_redraw = True


                elif event.key == pygame.K_DOWN:
                    sf.valg += 1
                    if sf.valg  == 5:
                         sf.valg = 1
                    print(sf.valg) 
                    need_redraw = True
                elif event.key == pygame.K_UP:
                    sf.valg -= 1
                    if sf.valg == 0:
                         sf.valg = 4
                    print(sf.valg)
                    need_redraw = True
                elif event.key == pygame.K_q:
                    sf.state = "menu"
                    print("pressed q")
                    sf.redraw(sf.state)


    if sf.state == "running":
        # Non-blocking startup sequence using pygame.time.get_ticks()
        now = pygame.time.get_ticks()
        if sf.startup_index < len(sf.startup_sequence):
            text1, text2, text3, delay = sf.startup_sequence[sf.startup_index]
            # When it's time to show the next step
            if now >= sf.startup_next_time:
                sf.story_update(text1, text2, text3)
                sf.redraw(sf.state)
                if delay is None:
                    delay_ms = random.randint(50, 250)
                else:
                    delay_ms = delay
                sf.startup_next_time = now + delay_ms
                sf.startup_index += 1
            
        else:
            # Sequence finished — move to menu
            need_redraw = True
            sf.state = "menu"
            sc.menu()


#     ▄▄▄  ▄▄▄                               
#     ███  ███                               
#     ████████   ▄████▄   ██▄████▄  ██    ██ 
#     ██ ██ ██  ██▄▄▄▄██  ██▀   ██  ██    ██ 
#     ██ ▀▀ ██  ██▀▀▀▀▀▀  ██    ██  ██    ██ 
#     ██    ██  ▀██▄▄▄▄█  ██    ██  ██▄▄▄███ 
#     ▀▀    ▀▀    ▀▀▀▀▀   ▀▀    ▀▀   ▀▀▀▀ ▀▀ 


    if sf.state == "menu":
        sc.menu()

        if sf.selected_valg_2:
            sf.state = "settings"
            sc.settings()
            sf.selected_valg_2 = False

        
        if sf.selected_valg_3:
            sf.state = "choice"
            sc.choice()
            sf.selected_valg_3 = False

    if sf.state == "choice":
        choice = True

        if sf.selected_valg_4:
            sf.state = "menu"
            sc.menu()
            sf.selected_valg_4 = False
                                                                     

    if sf.state == "settings":
        sc.settings()

        if sf.selected_valg_1:
            sf.state = "screen"
            sc.screen()
            sf.selected_valg_1 = False

        if sf.selected_valg_2:
            sf.state = "music"
            sf.story_update("music","-","-",)
            sf.valg_update("-","-","-","back",)
            sf.selected_valg_2 = False

        if sf.selected_valg_3:
            sf.state = "credits"
            sf.story_update("Programer -MaxiBonng"
                        ,"Art -Maxibonng"
                        ,"Music -MaxiBonng")
            sf.valg_update("-", "-", "-", "back")
            sf.selected_valg_3 = False

        if sf.selected_valg_4:
            sf.state = "menu"
            sc.menu()
            sf.selected_valg_4 = False
    
    if sf.state == "screen":
        sc.screen()

        if sf.selected_valg_2:
            sf.scale += 0.5
            if sf.scale >= 6:
                sf.scale = 6
            sf.canvas_making()
            sc.screen()
            need_redraw = True
            sf.selected_valg_2 = False

        if sf.selected_valg_3:
            sf.scale -= 0.5
            if sf.scale <= 1:
                sf.scale = 1
            sf.canvas_making()
            sc.screen()
            sf.selected_valg_3 = False

        if sf.selected_valg_4:
            sf.state = "settings"
            sc.settings()
            sf.selected_valg_4 = False

    if sf.state == "credits":
        
        if sf.selected_valg_4:
            sf.state = "settings"
            sc.settings()
            sf.selected_valg_4 = False

    if sf.state == "music":
        sf.story_update("music","-","-",)
        sf.valg_update("-","-","-","back",)


        if sf.selected_valg_4:
            sf.state = "settings"
            sc.settings()
            sf.selected_valg_4 = False



#                                            
#        ▄▄▄▄                                
#      ██▀▀▀▀█                               
#     ██         ▄█████▄  ████▄██▄   ▄████▄  
#     ██  ▄▄▄▄   ▀ ▄▄▄██  ██ ██ ██  ██▄▄▄▄██ 
#     ██  ▀▀██  ▄██▀▀▀██  ██ ██ ██  ██▀▀▀▀▀▀ 
#      ██▄▄▄██  ██▄▄▄███  ██ ██ ██  ▀██▄▄▄▄█ 
#        ▀▀▀▀    ▀▀▀▀ ▀▀  ▀▀ ▀▀ ▀▀    ▀▀▀▀▀  
#                                            
#                                            



    if need_redraw:
        if choice:
            choice_tree()
            choice = False
        sf.redraw(sf.state)
        need_redraw = False


pygame.quit()
