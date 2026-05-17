import pygame
import random
import log as log
import short_cut as cut

black = (15, 25, 15) #0F190E
green = (10, 142, 10) #0A8E0A
red = (162,8, 0) #A20800

screen_width = 320
screen_height = 240
scale = int(3)


selected_valg_1 = False
selected_valg_2 = False
selected_valg_3 = False
selected_valg_4 = False

prev_story1 = "-"
prev_story2 = "-"
prev_story3 = "-"

image_x = 0
image_y = 0

log.first_log = True

fullscreen = False

cutsceen_index = 0
cutsceen_next_time = 0

cutsceen_img_index = 0

#player variabler
state = "running"
# state = "menu" #den statien som spiler er på 
#start på "running"
valg = int(1) #de valg som spiler har max 4

#        ▄▄▄▄                                                                        
#      ██▀▀▀▀█              ██                                                       
#     ██▀       ██    ██  ███████   ▄▄█████▄   ▄█████▄   ▄████▄    ▄████▄   ██▄████▄ 
#     ██        ██    ██    ██      ██▄▄▄▄ ▀  ██▀    ▀  ██▄▄▄▄██  ██▄▄▄▄██  ██▀   ██ 
#     ██▄       ██    ██    ██       ▀▀▀▀██▄  ██        ██▀▀▀▀▀▀  ██▀▀▀▀▀▀  ██    ██ 
#      ██▄▄▄▄█  ██▄▄▄███    ██▄▄▄   █▄▄▄▄▄██  ▀██▄▄▄▄█  ▀██▄▄▄▄█  ▀██▄▄▄▄█  ██    ██ 
#        ▀▀▀▀    ▀▀▀▀ ▀▀     ▀▀▀▀    ▀▀▀▀▀▀     ▀▀▀▀▀     ▀▀▀▀▀     ▀▀▀▀▀   ▀▀    ▀▀ 


startup_sequence = [
    (0,(0,"Opening", "The_Night", "Made By MaxiBonng", 1000)),
    (0,(1,"Running simulation", "-", "Made By MaxiBonng", 1000)),
    (0,(2,"Running simulation", "December 12th", "-", 1000)),
    (0,(3,"Running simulation", "December 12th", "Case #19981112", 500)),
    (0,(4,"Loading", "-", "-", 500)),
    (0,(5,"Running", "log.py", "---------- 0%", None)),
    (0,(5,None, "short_cut.py", "##-------- 20%", None)),
    (0,(6,None, "save_load.py", "####------ 40%", None)),
    (0,(6,None, "choice_tree.py", "######---- 60%", None)),
    (0,(7,None, "story_functions.py", "#######--- 70%", None)),
    (0,(7,None, "logo.png", "#######--- 71%", None)),
    (0,(7,None, "start_cut_sceen.png", "#######--- 72%", None)),
    (0,(7,None, "start_screen.png", "#######--- 73%", None)),
    (0,(7,None, "glitch_1.png", "#######--- 74%", None)),
    (0,(7,None, "glitch_2.png", "#######--- 74%", None)),
    (0,(7,None, "glitch_3.png", "#######--- 75%", None)),
    (0,(7,None, "glitch_4.png", "#######--- 75%", None)),
    (0,(7,None, "glitch_5.png", "#######--- 76%", None)),
    (0,(7,None, "glitch_6.png", "#######--- 77%", None)),
    (0,(7,None, "glitch_7.png", "#######--- 77%", None)),
    (0,(7,None, "glitch_8.png", "#######--- 78%", None)),
    (0,(7,None, "glitch_9.png", "#######--- 79%", None)),
    (0,(8,None, "opening_cutsceen_1.png", "########-- 80%", None)),
    (0,(8,None, "opening_cutsceen_2.png", "########-- 80%", None)),
    (0,(8,None, "opening_cutsceen_3.png", "########-- 80%", None)),
    (0,(8,None, "opening_cutsceen_4.png", "########-- 81%", None)),
    (0,(8,None, "opening_cutsceen_5.png", "########-- 81%", None)),
    (0,(8,None, "opening_cutsceen_6.png", "########-- 81%", None)),
    (0,(8,None, "opening_cutsceen_7.png", "########-- 82%", None)),
    (0,(8,None, "opening_cutsceen_8.png", "########-- 82%", None)),
    (0,(8,None, "opening_cutsceen_9.png", "########-- 82%", None)),
    (0,(8,None, "opening_cutsceen_10.png", "########-- 83%", None)),
    (0,(8,None, "opening_cutsceen_11.png", "########-- 83%", None)),
    (0,(8,None, "opening_cutsceen_12.png", "########-- 83%", None)),
    (0,(8,None, "opening_cutsceen_13.png", "########-- 84%", None)),
    (0,(8,None, "opening_cutsceen_14.png", "########-- 84%", None)),
    (0,(8,None, "opening_cutsceen_15.png", "########-- 84%", None)),
    (0,(8,None, "opening_cutsceen_16.png", "########-- 85%", None)),
    (0,(8,None, "opening_cutsceen_17.png", "########-- 85%", None)),
    (0,(8,None, "opening_cutsceen_18.png", "########-- 85%", None)),
    (0,(8,None, "opening_cutsceen_19.png", "########-- 86%", None)),
    (0,(8,None, "opening_cutsceen_20.png", "########-- 86%", None)),
    (0,(8,None, "opening_cutsceen_21.png", "########-- 86%", None)),
    (0,(8,None, "opening_cutsceen_22.png", "########-- 87%", None)),
    (0,(8,None, "opening_cutsceen_23.png", "########-- 87%", None)),
    (0,(8,None, "opening_cutsceen_24.png", "########-- 87%", None)),
    (0,(8,None, "opening_cutsceen_25.png", "########-- 88%", None)),
    (0,(8,None, "opening_cutsceen_26.png", "########-- 88%", None)),
    (0,(8,None, "opening_cutsceen_27.png", "########-- 88%", None)),
    (0,(8,None, "opening_cutsceen_28.png", "########-- 89%", None)),
    (0,(8,None, "opening_cutsceen_29.png", "########-- 89%", None)),
    (0,(8,None, "opening_cutsceen_30.png", "########-- 89%", None)),
    (0,(8,"Running", "The_Night.py", "#########- 90%", 400)),
    (0,(9,"Welcome", "Mr.############", "-", 1000)),
    (0,(9,"-","-","-", 1500))
]



glitch = [pygame.image.load(f"img/start_up/glitch_{i}.png")
        for i in range(1, 10)]

opening_cutsceen_list = [
    (0,(0,"Opening","Opening_cutsceen","Loading .", 1000)),
    (0,(0,"Running","Opening_cutsceen","Loading ..", 1000)),
    (0,(1,None,None,"Loading ...", 500)),
    (0,(1 ,None,"Its night","-", 500)),
    (0,(2 ,None,"Its night",None, 500)),
    (1,(3,7,500)),
    (0,(8 ,None,"Your driving home",None, 500)),
    (1,(9,13,500)),
    (1,(10,13,500)),
    (1,(10,13,500)),
    (0,(10,None,"You just got back from work",None, 500)),
    (1,(11,22,500)),
    (0,(23,None,"-",None, 500)),
    (1,(24,29,500)),
    (0,(30,None,"STARTING GAME","HAVE FUN.", 1000)),
    (0,(0,None,"STARTING GAME","HAVE FUN..", 500)),
    (0,(0,None,None,"HAVE FUN...", 2000)),
]

opening_cutsceen = [pygame.image.load(f"img\opening_cutsceen/opening_cutsceen_{i}.png")
                    for i in range(1, 31)]

def cutsceen(text_list, img_list, state_to, cut_to):
    global state, cutsceen_index, cutsceen_next_time, cutsceen_img_index

    now = pygame.time.get_ticks()

    if cutsceen_index < len(text_list):
        if now >= cutsceen_next_time:
            sceen_type, sceen_info = text_list[cutsceen_index]

            if sceen_type == 0:
                img_index, text1, text2, text3, delay = sceen_info
            
                if img_index == 0:
                    main_canvas.fill(green)
                else:
                    main_canvas.blit(img_list[img_index - 1], (image_x, image_y))
                if delay is None:
                    if state == "running":
                        delay_ms = random.randint(50, 150)
                else:
                    delay_ms = delay
                story_update(text1, text2, text3)
                redraw(state)
            if sceen_type == 1:
                img_index_start, img_index_to, delay = sceen_info

                current_img = img_index_start + cutsceen_img_index

                main_canvas.blit(img_list[current_img - 1], (image_x, image_y))

                delay_ms = delay

                story_update(None, None, None)
                redraw(state)
                
                if current_img < img_index_to:
                    cutsceen_img_index += 1
                    cutsceen_next_time = now + delay_ms
                    return
                else:
                    cutsceen_img_index = 0

            cutsceen_next_time = now + delay_ms
            cutsceen_index += 1

    else:
        cutsceen_index = 0
        cutsceen_next_time = 0
        cutsceen_img_index = 0
        state = state_to
        cut_to()
        redraw(state)


#        ▄▄▄▄                                                    
#      ██▀▀▀▀█                                                   
#     ██▀        ▄█████▄  ██▄████▄  ██▄  ▄██   ▄█████▄  ▄▄█████▄ 
#     ██         ▀ ▄▄▄██  ██▀   ██   ██  ██    ▀ ▄▄▄██  ██▄▄▄▄ ▀ 
#     ██▄       ▄██▀▀▀██  ██    ██   ▀█▄▄█▀   ▄██▀▀▀██   ▀▀▀▀██▄ 
#      ██▄▄▄▄█  ██▄▄▄███  ██    ██    ████    ██▄▄▄███  █▄▄▄▄▄██ 
#        ▀▀▀▀    ▀▀▀▀ ▀▀  ▀▀    ▀▀     ▀▀      ▀▀▀▀ ▀▀   ▀▀▀▀▀▀  
                                                         
# Indlæs billede
def image_make():
    global start_front, start_cutsceen
    start_front = pygame.image.load("img/start_screen.png")
    start_cutsceen = pygame.image.load("img/start_cut_sceen.png")

def make_canvas():
    global valg_1,valg_2,valg_3,valg_4
    global main_canvas, story_canvas, text_canvas
    global valg_x, valg_1_y, valg_2_y, valg_3_y, valg_4_y
    global text_valg_1, text_valg_b_1, text_valg_2, text_valg_b_2
    global text_valg_3, text_valg_b_3, text_valg_4, text_valg_b_4
    global story_y, story_y_2, story_y_3, text_story, text_story_2, text_story_3

    #main_canvas det der kommer bilder på
    main_canvas_width = 314
    main_canvas_height = 114
    main_canvas = pygame.Surface((main_canvas_width, main_canvas_height))
    main_canvas.fill(black)

    #story_canvas det der komer text omkring story
    story_canvas_width = 314
    story_canvas_height = 58
    story_canvas = pygame.Surface((story_canvas_width, story_canvas_height))  # Nyt canvas
    story_canvas.fill(black)

    #valg
    text_canvas_width = 314
    text_canvas_height = 58
    text_canvas = pygame.Surface((text_canvas_width, text_canvas_height))  # Nyt canvas
    text_canvas.fill(black)

    #laver valg til playerene
    valg_x = 4

    valg_1_y = 2
    valg_1 = str("1")
    text_valg_1 = font.render(valg_1, True, green)
    text_valg_b_1 = font.render(valg_1, True, black)

    valg_2_y = valg_1_y + 14
    valg_2 = str("2")
    text_valg_2 = font.render(valg_2, True, green)
    text_valg_b_2 = font.render(valg_2, True, black)

    valg_3_y = valg_2_y + 14
    valg_3 = str("3")
    text_valg_3 = font.render(valg_3, True, green)
    text_valg_b_3 = font.render(valg_3, True, black)

    valg_4_y = valg_3_y + 14
    valg_4 = str("4")
    text_valg_4 = font.render(valg_4, True, green)
    text_valg_b_4 = font.render(valg_4, True, black)

    #laver story text
    story_y = 3
    story = "-"
    text_story = font.render(story, True, green)

    story_y_2 = 19
    story_2 =  "-"
    text_story_2 = font.render(story_2, True, green)

    story_y_3 = 36
    story_3 =  "-"
    text_story_3 = font.render(story_3, True, black)

def make_screen():
    global font, story_canvas, text_canvas, main_canvas, canvas, scaled_width, scaled_height, SCREEN, scale, fullscreen, width_offset,height_offset,monitor_width, monitor_height

    if fullscreen:
        SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        monitor_height = SCREEN.get_height()
        monitor_width = SCREEN.get_width()

        if monitor_height >= monitor_width:
            scale = monitor_width/screen_width
        if monitor_width >= monitor_height:
            scale = monitor_height/screen_height

        scaled_width = screen_width * scale
        scaled_height = screen_height * scale

        width_offset = (monitor_width - scaled_width )/2
        height_offset = (monitor_height - scaled_height)/2
        
    else:
        scaled_width = screen_width * scale
        scaled_height = screen_height * scale

        # Skab skærm og indstil ikon
        SCREEN = pygame.display.set_mode((scaled_width, scaled_height))  # Endelig skærmstørrelse

    pygame.display.set_caption("The Night")
    the_night_logo = pygame.image.load("img/logo.png").convert_alpha()  # Indlæs dit ikonbillede
    pygame.display.set_icon(the_night_logo)  # Sæt ikonet for vinduet

    # Opret skrifttype (angiv skrifttype og størrelse)
    #https://befonts.com/author/studioaktype
    font_path = "Pixel.ttf"  # font made by studioaktype
    pygame.font.init()
    font = pygame.font.FontType(font_path, 11)

    # Lav det primære canvas
    print(scale)
    canvas = pygame.Surface((screen_width, screen_height))
    canvas.fill(black)
    pygame.draw.rect(canvas, green, (1, 1, 318, 238))  # Grøn kant

make_screen()


#     ▄▄    ▄▄            ▄▄▄▄               
#     ▀██  ██▀            ▀▀██               
#      ██  ██    ▄█████▄    ██       ▄███▄██ 
#      ██  ██    ▀ ▄▄▄██    ██      ██▀  ▀██ 
#       ████    ▄██▀▀▀██    ██      ██    ██ 
#       ████    ██▄▄▄███    ██▄▄▄   ▀██▄▄███ 
#       ▀▀▀▀     ▀▀▀▀ ▀▀     ▀▀▀▀    ▄▀▀▀ ██ 
#                                    ▀████▀▀ 


def valg_update(v1 ,v2, v3, v4):

    global valg_1 ,valg_2, valg_3, valg_4
    global text_valg_1, text_valg_2, text_valg_3, text_valg_4
    global text_valg_b_1, text_valg_b_2, text_valg_b_3, text_valg_b_4

    valg_1 = v1
    valg_2 = v2
    valg_3 = v3
    valg_4 = v4
    
    text_valg_1 = font.render(valg_1, True, green)
    text_valg_b_1 = font.render(valg_1, True, black)

    text_valg_2 = font.render(valg_2, True, green)
    text_valg_b_2 = font.render(valg_2, True, black)

    text_valg_3 = font.render(valg_3, True, green)
    text_valg_b_3 = font.render(valg_3, True, black)

    text_valg_4 = font.render(valg_4, True, green)
    text_valg_b_4 = font.render(valg_4, True, black)

def choice_select(state_to1,cut_to1,
                  state_to2,cut_to2,
                  state_to3,cut_to3,
                  state_to4,cut_to4):
    global selected_valg_1,selected_valg_2,selected_valg_3,selected_valg_4,state

    if selected_valg_1:
        if state_to1 != None:
            state = state_to1
        if cut_to1 != None:
            cut_to1()
        selected_valg_1 = False

    elif selected_valg_2:
        if state_to2 != None:
            state = state_to2
        if cut_to2 != None:
            cut_to2()
        selected_valg_2 = False        
    
    elif selected_valg_3:
        if state_to3 != None:
            state = state_to3
        if cut_to3 != None:
            cut_to3()
        selected_valg_3 = False        
    
    elif selected_valg_4:
        if state_to4 != None:
            state = state_to4
        if cut_to4 != None:
            cut_to4()
        selected_valg_4 = False

def text_valg():
    global selected_valg_1, selected_valg_2,selected_valg_3 , selected_valg_4
    # Opdater teksten baseret på valget
    if valg == 1:
        selected_valg_1 = True
    elif valg == 2:
        selected_valg_2 = True 
    elif valg == 3:
        selected_valg_3 = True
    elif valg == 4:
        selected_valg_4 = True


#       ▄▄▄▄                                           
#     ▄█▀▀▀▀█     ██                                   
#     ██▄       ███████    ▄████▄    ██▄████  ▀██  ███ 
#      ▀████▄     ██      ██▀  ▀██   ██▀       ██▄ ██  
#          ▀██    ██      ██    ██   ██         ████▀  
#     █▄▄▄▄▄█▀    ██▄▄▄   ▀██▄▄██▀   ██          ███   
#      ▀▀▀▀▀       ▀▀▀▀     ▀▀▀▀     ▀▀          ██    
#                                              ███     
   
def story_update(text1, text2, text3):
    global text_story, text_story_2, text_story_3
    global prev_story1 ,prev_story2 ,prev_story3
    story_canvas.fill(black)
    
    if text1 == None:
        text_story = font.render(prev_story1, True, green)
    else:    
        text_story = font.render(text1, True, green)
        prev_story1 = text1
    
    if text2 == None:
        text_story_2 = font.render(prev_story2, True, green)
    else:
        text_story_2 = font.render(text2, True, green)
        prev_story2 = text2
    
    if text3 == None:
        text_story_3 = font.render(prev_story3, True, green)
    else:
        text_story_3 = font.render(text3, True, green)
        prev_story3 = text3

    story_canvas.blit(text_story, (valg_x, story_y))
    story_canvas.blit(text_story_2, (valg_x, story_y_2))
    story_canvas.blit(text_story_3, (valg_x, story_y_3))


def text_redraw():
    global valg_log
    
    text_canvas.fill(black)
    if valg == 1:
        pygame.draw.rect(text_canvas, green, (0, valg_1_y, 318, 13))
        text_canvas.blit(text_valg_b_1, (valg_x, valg_1_y))
        text_canvas.blit(text_valg_2, (valg_x, valg_2_y))
        text_canvas.blit(text_valg_3, (valg_x, valg_3_y))
        text_canvas.blit(text_valg_4, (valg_x, valg_4_y))
        valg_log = valg_1
    elif valg == 2:
        pygame.draw.rect(text_canvas, green, (0, valg_2_y, 318, 13))
        text_canvas.blit(text_valg_1, (valg_x, valg_1_y))
        text_canvas.blit(text_valg_b_2, (valg_x, valg_2_y))
        text_canvas.blit(text_valg_3, (valg_x, valg_3_y))
        text_canvas.blit(text_valg_4, (valg_x, valg_4_y))
        valg_log = valg_2
    elif valg == 3:
        pygame.draw.rect(text_canvas, green, (0, valg_3_y, 318, 13))
        text_canvas.blit(text_valg_1, (valg_x, valg_1_y))
        text_canvas.blit(text_valg_2, (valg_x, valg_2_y))
        text_canvas.blit(text_valg_b_3, (valg_x, valg_3_y))
        text_canvas.blit(text_valg_4, (valg_x, valg_4_y))
        valg_log = valg_3
    elif valg == 4:
        pygame.draw.rect(text_canvas, green, (0, valg_4_y, 318, 13))
        text_canvas.blit(text_valg_1, (valg_x, valg_1_y))
        text_canvas.blit(text_valg_2, (valg_x, valg_2_y))
        text_canvas.blit(text_valg_3, (valg_x, valg_3_y))
        text_canvas.blit(text_valg_b_4, (valg_x, valg_4_y))
        valg_log = valg_4
    elif valg == 6:
        text_canvas.fill(green)

#     ▄▄▄▄▄▄                    ▄▄                               
#     ██▀▀▀▀██                  ██                               
#     ██    ██   ▄████▄    ▄███▄██   ██▄████   ▄█████▄ ██      ██
#     ███████   ██▄▄▄▄██  ██▀  ▀██   ██▀       ▀ ▄▄▄██ ▀█  ██  █▀
#     ██  ▀██▄  ██▀▀▀▀▀▀  ██    ██   ██       ▄██▀▀▀██  ██▄██▄██ 
#     ██    ██  ▀██▄▄▄▄█  ▀██▄▄███   ██       ██▄▄▄███  ▀██  ██▀ 
#     ▀▀    ▀▀▀   ▀▀▀▀▀     ▀▀▀ ▀▀   ▀▀        ▀▀▀▀ ▀▀   ▀▀  ▀▀  

def redraw(state):
    global startup_sequence, startup_index,startup_next_time,  scaled_width, scaled_height 
    text_redraw()
    
    print(state)
    log.log(state ,valg, valg_log)
    log.first_log = False

    if state == "running" or state == "opening_cutsceen":
        text_canvas.fill(green)

    if state == "menu" or state == "settings" or state == "screen":
        main_canvas.blit(start_front, (image_x, image_y))


    canvas.blit(main_canvas, (3, 3))
    canvas.blit(story_canvas,(3, 119))
    canvas.blit(text_canvas, (3, 179)) 

    # Skalér det samled e canvas og tegn det på skærmen
    scaled_canvas = pygame.transform.scale(canvas, (scaled_width, scaled_height))
    if fullscreen:
        if monitor_height >= monitor_width:
           SCREEN.blit(scaled_canvas, (0, height_offset))
        if monitor_width >= monitor_height:
            SCREEN.blit(scaled_canvas, (width_offset, 0))       
    else:
        SCREEN.blit(scaled_canvas, (0, 0))

    # Opdater skærmen
    pygame.display.flip()