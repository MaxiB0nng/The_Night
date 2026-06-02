import pygame
import random
import log as log
import save_load as sl

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

allow_input = True

#player variabler
state = "running"
chapter = 0

# state = "menu" 
#den statien som spiler er på 
#start på "running"
valg = int(1) #de valg som spiler har max 4


#        ▄▄▄▄                                                                        
#      ██▀▀▀▀█              ██                                                       
#     ██▀       ██    ██  ███████   ▄▄█████▄   ▄█████▄   ▄████▄    ▄████▄   ██▄████▄ 
#     ██        ██    ██    ██      ██▄▄▄▄ ▀  ██▀    ▀  ██▄▄▄▄██  ██▄▄▄▄██  ██▀   ██ 
#     ██▄       ██    ██    ██       ▀▀▀▀██▄  ██        ██▀▀▀▀▀▀  ██▀▀▀▀▀▀  ██    ██ 
#      ██▄▄▄▄█  ██▄▄▄███    ██▄▄▄   █▄▄▄▄▄██  ▀██▄▄▄▄█  ▀██▄▄▄▄█  ▀██▄▄▄▄█  ██    ██ 
#        ▀▀▀▀    ▀▀▀▀ ▀▀     ▀▀▀▀    ▀▀▀▀▀▀     ▀▀▀▀▀     ▀▀▀▀▀     ▀▀▀▀▀   ▀▀    ▀▀ 

def cutsceen(text_list, img_list, state_to, cut_to):
    global state, cutsceen_index, cutsceen_next_time, cutsceen_img_index, allow_input
    allow_input = False

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
        if now >= cutsceen_next_time:
            cutsceen_index = 0
            cutsceen_next_time = 0
            cutsceen_img_index = 0
            allow_input = True
            state = state_to
            cut_to()
            redraw(state)


#     ▄▄▄▄▄▄    ▄▄▄▄                         
#     ██▀▀▀▀█▄  ▀▀██                  ██     
#     ██    ██    ██       ▄████▄   ███████  
#     ██████▀     ██      ██▀  ▀██    ██     
#     ██          ██      ██    ██    ██     
#     ██          ██▄▄▄   ▀██▄▄██▀    ██▄▄▄  
#     ▀▀           ▀▀▀▀     ▀▀▀▀       ▀▀▀▀  

item_list= [
    ("bun",0,False),
    ("knife",6,False),
    ("letter",6,False),
    ("phone",4, True),
]

plot_list = [
    ("alseep couch",(3,6),False),
    ("asleep bed",1,False)
]

def get_plot(list_choice, event_item):
    global item_list, plot_list

    if list_choice == "item":
        for item, _, happened in item_list:
            if item == event_item:
                return happened

    elif list_choice == "plot":
        for event, _, happened in plot_list:
            if event == event_item:
                return happened


def plot_write(list_choice,event_item,bolang: bool):
    global item_list, plot_list

    if list_choice == "item":
        for i, (item, ending, happened) in enumerate(item_list):
            if item == event_item:
                happened = bolang
                item_list[i] = (item, ending, happened)

    
    elif list_choice == "plot":
        for i, (event, ending, happened) in enumerate(plot_list):
            if event == event_item:
                happened = bolang
                plot_list[i] = (event, ending, happened)


#        ▄▄▄▄                                                    
#      ██▀▀▀▀█                                                   
#     ██▀        ▄█████▄  ██▄████▄  ██▄  ▄██   ▄█████▄  ▄▄█████▄ 
#     ██         ▀ ▄▄▄██  ██▀   ██   ██  ██    ▀ ▄▄▄██  ██▄▄▄▄ ▀ 
#     ██▄       ▄██▀▀▀██  ██    ██   ▀█▄▄█▀   ▄██▀▀▀██   ▀▀▀▀██▄ 
#      ██▄▄▄▄█  ██▄▄▄███  ██    ██    ████    ██▄▄▄███  █▄▄▄▄▄██ 
#        ▀▀▀▀    ▀▀▀▀ ▀▀  ▀▀    ▀▀     ▀▀      ▀▀▀▀ ▀▀   ▀▀▀▀▀▀  
                                                         
# Indlæs billede
def image_make():
    global start_front
    start_front = pygame.image.load("img/start_screen.png").convert()

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
    global startup_sequence, startup_index,startup_next_time,  scaled_width, scaled_height, chapter
    text_redraw()
    
    log.log(state ,valg, valg_log)
    log.first_log = False

    if allow_input == False:
        text_canvas.fill(green)

    elif state == "menu" or state == "settings" or state == "screen":
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
    sl.save(chapter,state)

    pygame.display.flip()
