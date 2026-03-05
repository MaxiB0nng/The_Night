import pygame
import log

black = (15, 25, 15) #0F190E
green = (10, 142, 10) #0A8E0A
red = (162,8, 0) #A20800

screen_width = 320
screen_height = 240
scale = 3



# Index and timer for non-blocking startup sequence
startup_index = 0
startup_next_time = 0

selected_valg_1 = False
selected_valg_2 = False
selected_valg_3 = False
selected_valg_4 = False


image_x = 0
image_y = 0

log.first_log = True

#player variabler
state = "menu"
# state = "menu" #den statien som spiler er på 
#start på "running"
valg = int(1) #de valg som spiler har max 4

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


def canvas_making():
    global font, story_canvas, text_canvas, main_canvas, canvas, scaled_width, scaled_height, SCREEN
    scaled_width = screen_width * scale
    scaled_height = screen_height * scale

    # Skab skærm og indstil ikon
    SCREEN = pygame.display.set_mode((scaled_width, scaled_height))  # Endelig skærmstørrelse

    pygame.display.set_caption("The Night")
    the_night_logo = pygame.image.load("img/logo.png").convert_alpha()  # Indlæs dit ikonbillede
    pygame.display.set_icon(the_night_logo)  # Sæt ikonet for vinduet

    # Opret skrifttype (angiv skrifttype og størrelse)
    font_path = "Pixelon-OGALo.ttf"  # Sti til din skrifttype-fil
    pygame.font.init()
    font = pygame.font.FontType(font_path, 11)

    # Lav det primære canvas
    canvas = pygame.Surface((screen_width, screen_height))
    canvas.fill(black)
    pygame.draw.rect(canvas, green, (1, 1, 318, 238))  # Grøn kant

canvas_making()

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

def story_update(text1, text2, text3):
    global text_story, text_story_2, text_story_3
    story_canvas.fill(black)
    
    text_story = font.render(text1, True, green)
    text_story_2 = font.render(text2, True, green)
    text_story_3 = font.render(text3, True, green)

    story_canvas.blit(text_story, (valg_x, story_y))
    story_canvas.blit(text_story_2, (valg_x, story_y_2))
    story_canvas.blit(text_story_3, (valg_x, story_y_3))

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
        pygame.draw.rect(text_canvas, green, (0, valg_1_y, 318, 13))
        pygame.draw.rect(text_canvas, green, (0, valg_2_y, 318, 13))
        pygame.draw.rect(text_canvas, green, (0, valg_3_y, 318, 13))
        pygame.draw.rect(text_canvas, green, (0, valg_4_y, 318, 13))
        text_canvas.blit(text_valg_b_1, (valg_x, valg_1_y))
        text_canvas.blit(text_valg_b_2, (valg_x, valg_2_y))
        text_canvas.blit(text_valg_b_3, (valg_x, valg_3_y))
        text_canvas.blit(text_valg_b_4, (valg_x, valg_4_y))

def redraw(state):
    global startup_sequence, startup_index,startup_next_time
    text_redraw()
    
    print(state)
    log.log(state ,valg, valg_log)
    log.first_log = False



    # Endelig skærmstørrelse beregnes
    startup_sequence = [
        ("Opening", "The_Night", "Made By MaxiBonng", 1000),
        ("Running simulation", "-", "Made By MaxiBonng", 1000),
        ("Running simulation", "December 12th", "-", 1000),
        ("Running simulation", "December 12th", "case #19981112", 500),
        ("Loading", "-", "-", 500),
        ("Loading", "camp_fire_2.png", "---------- 0%", None),
        ("Loading", "camp_fire.png", "#--------- 10%", None),
        ("Loading", "front_tent.png", "##-------- 20%", None),
        ("Loading", "forest_1.png", "###------- 30%", None),
        ("Loading", "forest_2.png", "###------ 30%", None),
        ("Loading", "forest_2_1.png", "####------ 40%", None),
        ("Loading", "forest_camp.png", "#####----- 50%", None),
        ("Loading", "forest_camp_2.png", "######---- 60%", None),
        ("Loading", "start_cut_sceen.png", "#######--- 70%", None),
        ("Loading", "logo.png", "########-- 80%", None),
        ("Loading", "The_Night.py", "#########- 90%", 400),
        ("Opening", "-", "########## 100%", 1000),
        ("Welcome", "Mr.############", "-", 1000),
        ("-","-","-", 1500)
    ]


    glitch = [pygame.image.load(f"img/start_up/glitch_{i}.png")
            for i in range(1, 10)]


    if state == "running":
        if startup_index == 1:
            main_canvas.blit(glitch[0], (image_x, image_y))
        elif startup_index == 2:
            main_canvas.blit(glitch[1], (image_x, image_y))
        elif startup_index == 3:
            main_canvas.blit(glitch[2], (image_x, image_y))
        elif startup_index == 5:
            main_canvas.blit(glitch[3], (image_x, image_y))
        elif startup_index == 7:
            main_canvas.blit(glitch[4], (image_x, image_y))
        elif startup_index == 10:
            main_canvas.blit(glitch[5], (image_x, image_y))
        elif startup_index == 13:
            main_canvas.blit(glitch[6], (image_x, image_y))
        elif startup_index == 15:
            main_canvas.blit(glitch[7], (image_x, image_y))
        elif startup_index == 17:
            main_canvas.blit(glitch[8], (image_x, image_y))
        text_canvas.fill(green)

    
    if state == "menu" or state == "settings" or state == "screen":
        main_canvas.blit(start_front, (image_x, image_y))


    canvas.blit(main_canvas, (3, 3))  # Tegn hoved-canvas på det primære canvas
    canvas.blit(story_canvas, (3, 119))  # Tegn tekst-canvas nederst i det primære canvas
    canvas.blit(text_canvas, (3, 179))  # Tegn tekst-canvas nederst i det primære canvas

    # Skalér det samled e canvas og tegn det på skærmen
    scaled_canvas = pygame.transform.scale(canvas, (scaled_width, scaled_height))
    SCREEN.blit(scaled_canvas, (0, 0))

    # Opdater skærmen
    pygame.display.flip()