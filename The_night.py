import pygame
import random

pygame.init()
pygame.mixer.init()

# Opløsninger for det lavopløselige "canvas"
screen_width = 320
screen_height = 240
scale = 3

# Farver (RGB)
black = (15, 25, 15) #0F190E
green = (10, 142, 10) #0A8E0A


#player variabler
state = "running" #den statien som spiler er på 
#start på "running"
valg = int(1) #de valg som spiler har max 4


# TIDSRELATEREDE VARIABLER

last_blink_time = 0  # Det tidspunkt, hvor den sidste blinkning opstod
show_story_timer = 0  # Tidspunktet, hvor historieteksten blev startet
show_story_duration = 1000  # Hvor længe historieteksten skal vises (i ms)

startup_timer = int(0)
startup_duration = int(1000)


#alle flag variabler
need_redraw = True #hvis den er sand så opdatere den skærmen 
story_visible = False  #bestemer om text 3 vises eller ej
startup_show = False #bruger til startup animation 
story_visible = False

selected_valg_1 = False
selected_valg_2 = False
selected_valg_3 = False
selected_valg_4 = False


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

# Index and timer for non-blocking startup sequence
startup_index = 0
startup_next_time = 0

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
    font = pygame.font.Font(font_path, 11)  # Font på 24-punktsstørrelse

    # Lav det primære canvas
    canvas = pygame.Surface((screen_width, screen_height))
    canvas.fill(black)
    pygame.draw.rect(canvas, green, (1, 1, 318, 238))  # Grøn kant

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

canvas_making()

#laver valg til playerene

valg_x = 4

valg_1_y = 2
valg_1 = "1"
text_valg_1 = font.render(valg_1, True, green)
text_valg_b_1 = font.render(valg_1, True, black)

valg_2_y = valg_1_y + 14
valg_2 = "2"
text_valg_2 = font.render(valg_2, True, green)
text_valg_b_2 = font.render(valg_2, True, black)

valg_3_y = valg_2_y + 14
valg_3 = "3"
text_valg_3 = font.render(valg_3, True, green)
text_valg_b_3 = font.render(valg_3, True, black)

valg_4_y = valg_3_y + 14
valg_4 = "4"
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

glitch = [pygame.image.load(f"img/start_up/glitch_{i}.png")
          for i in range(1, 10)]

# Indlæs billede
start_front = pygame.image.load("img/start_screen.png")
start_cutsceen = pygame.image.load("img/start_cut_sceen.png")
skove_1_img = pygame.image.load("img/skove_1.png")
skove_2_img = pygame.image.load("img/skove_2_0.png")
skove_2_1_img = pygame.image.load("img/skove_2_1.png")
skove_camp_img = pygame.image.load("img/skove_camp.png")
skove_camp_2_img = pygame.image.load("img/skove_camp_2.png")
camp_fire_img = pygame.image.load("img/camp_fire.png")
camp_fire_img_2 = pygame.image.load("img/camp_fire_2.png")
foran_telt_img = pygame.image.load("img/foran_telt.png")

image_x = 0
image_y = 0


def valg_update(valg_1 ,valg_2, valg_3, valg_4):
    global text_valg_1, text_valg_2, text_valg_3, text_valg_4
    global text_valg_b_1, text_valg_b_2, text_valg_b_3, text_valg_b_4

    text_valg_1 = font.render(valg_1, True, green)
    text_valg_b_1 = font.render(valg_1, True, black)

    text_valg_2 = font.render(valg_2, True, green)
    text_valg_b_2 = font.render(valg_2, True, black)

    text_valg_3 = font.render(valg_3, True, green)
    text_valg_b_3 = font.render(valg_3, True, black)

    text_valg_4 = font.render(valg_4, True, green)
    text_valg_b_4 = font.render(valg_4, True, black)


def story_update(text1, text2, text3):
    global text_story, text_story_2
    story_canvas.fill(black)
    text_story = font.render(text1, True, green)
    text_story_2 = font.render(text2, True, green)
    text_story_3 = font.render(text3, True, green)
    story_canvas.blit(text_story, (valg_x, story_y))
    story_canvas.blit(text_story_2, (valg_x, story_y_2))
    story_canvas.blit(text_story_3, (valg_x, story_y_3))


def text_valg():
    global selected_valg, selected_valg_1, selected_valg_2,selected_valg_3 , selected_valg_4
    
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
    global need_redraw, story_visible
    text_canvas.fill(black)
    if valg == 1:
        pygame.draw.rect(text_canvas, green, (0, valg_1_y, 318, 13))
        text_canvas.blit(text_valg_b_1, (valg_x, valg_1_y))
        text_canvas.blit(text_valg_2, (valg_x, valg_2_y))
        text_canvas.blit(text_valg_3, (valg_x, valg_3_y))
        text_canvas.blit(text_valg_4, (valg_x, valg_4_y))
    elif valg == 2:
        pygame.draw.rect(text_canvas, green, (0, valg_2_y, 318, 13))
        text_canvas.blit(text_valg_1, (valg_x, valg_1_y))
        text_canvas.blit(text_valg_b_2, (valg_x, valg_2_y))
        text_canvas.blit(text_valg_3, (valg_x, valg_3_y))
        text_canvas.blit(text_valg_4, (valg_x, valg_4_y))
    elif valg == 3:
        pygame.draw.rect(text_canvas, green, (0, valg_3_y, 318, 13))
        text_canvas.blit(text_valg_1, (valg_x, valg_1_y))
        text_canvas.blit(text_valg_2, (valg_x, valg_2_y))
        text_canvas.blit(text_valg_b_3, (valg_x, valg_3_y))
        text_canvas.blit(text_valg_4, (valg_x, valg_4_y))
    elif valg == 4:
        pygame.draw.rect(text_canvas, green, (0, valg_4_y, 318, 13))
        text_canvas.blit(text_valg_1, (valg_x, valg_1_y))
        text_canvas.blit(text_valg_2, (valg_x, valg_2_y))
        text_canvas.blit(text_valg_3, (valg_x, valg_3_y))
        text_canvas.blit(text_valg_b_4, (valg_x, valg_4_y))
    elif valg == 6:
        pygame.draw.rect(text_canvas, green, (0, valg_1_y, 318, 13))
        pygame.draw.rect(text_canvas, green, (0, valg_2_y, 318, 13))
        pygame.draw.rect(text_canvas, green, (0, valg_3_y, 318, 13))
        pygame.draw.rect(text_canvas, green, (0, valg_4_y, 318, 13))
        text_canvas.blit(text_valg_b_1, (valg_x, valg_1_y))
        text_canvas.blit(text_valg_b_2, (valg_x, valg_2_y))
        text_canvas.blit(text_valg_b_3, (valg_x, valg_3_y))
        text_canvas.blit(text_valg_b_4, (valg_x, valg_4_y))


def redraw():
    global need_redraw
    print("drawing")
    
    text_redraw()

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


# Spil-loop
running = True
while running:
    for event in pygame.event.get():
        # Lukning af spillet
        if event.type == pygame.QUIT:
            running = False

        # Håndter KEYDOWN tastetryk
        if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:  # Space/enter tast blev trykke
                    enter_pressed = True
                    text_valg()
                    need_redraw = True


                elif event.key == pygame.K_DOWN:
                    valg += 1
                    if valg  == 5:
                         valg = 1
                    print(valg) 
                    need_redraw = True
                elif event.key == pygame.K_UP:
                    valg -= 1
                    if valg == 0:
                         valg = 4
                    print(valg)
                    need_redraw = True
                elif event.key == pygame.K_q:
                    state = "menu"
                    print("pressed q")
                    need_redraw = True


    if state == "running":
        # Non-blocking startup sequence using pygame.time.get_ticks()
        now = pygame.time.get_ticks()
        if startup_index < len(startup_sequence):
            text1, text2, text3, delay = startup_sequence[startup_index]
            # When it's time to show the next step
            if now >= startup_next_time:
                story_update(text1, text2, text3)
                redraw()
                if delay is None:
                    delay_ms = random.randint(50, 250)
                else:
                    delay_ms = delay
                startup_next_time = now + delay_ms
                startup_index += 1
        else:
            # Sequence finished — move to menu
            need_redraw = True
            state = "menu"
            story_update("Welcome to The Night Of", "December 12", "press enter to continue")
            valg_update("Continue","Settings","-", "-")
            

    if state == "menu":
        story_update("Welcome to The Night", "Case #19981112", "you can always press Q to return to the main menu")
        valg_update("Continue","Settings","-", "-")

        if selected_valg_2:
            state = "settings"
            story_update("Settings", "-", "-")
            valg_update("screen", "music", "credits", "back")
            selected_valg_2 = False

    #       _____      _   _   _                 
    #      / ____|    | | | | (_)                
    #     | (___   ___| |_| |_ _ _ __   __ _ ___ 
    #      \___ \ / _ \ __| __| | '_ \ / _` / __|
    #      ____) |  __/ |_| |_| | | | | (_| \__ \
    #     |_____/ \___|\__|\__|_|_| |_|\__, |___/
    #                                   __/ |    
    #                                  |___/     


    if state == "settings":
        #story_update("Settings", "-", "-")
        #valg_update("screen", "music", "credits", "back")

        if selected_valg_1:
            state = "screen"
            story_update("The screen is fixed at a 320x240 ratio", f"the screen is  {scaled_height}x{scaled_width}", "-")
            valg_update(f"scale = {scale}", "scale +", "scale -", "back")
            selected_valg_1 = False

        if selected_valg_2:
            state = "music"
            story_update("music","-","-",)
            valg_update("-","-","-","back",)
            selected_valg_2 = False

        if selected_valg_3:
            state = "credits"
            story_update("Programer -MaxiBonng"
                        ,"Art -Maxibonng"
                        ,"Music -MaxiBonng")
            valg_update("-", "-", "-", "back")
            selected_valg_3 = False

        if selected_valg_4:
            state = "menu"
            story_update("Welcome to The Night Of", "December 12", "press enter to continue")
            valg_update("Continue","Settings","-", "-")
            selected_valg_4 = False
    
    if state == "screen":
        #story_update("The screen is fixed at a 320x240 ratio", f"the screen is  {scaled_height}x{scaled_width}", "-")
        #valg_update(f"scale = {scale}", "scale +", "scale -", "back")

        if selected_valg_2:
            scale += 0.5
            if scale >= 6:
                scale = 6
            canvas_making()
            story_update("The screen is fixed at a 320x240 ratio", f"the screen is  {scaled_height}x{scaled_width}", "-")
            valg_update(f"scale = {scale}", "scale +", "scale -", "back")
            need_redraw = True
            selected_valg_2 = False

        if selected_valg_3:
            scale -= 0.5
            if scale <= 1:
                scale = 1
            canvas_making()
            story_update("The screen is fixed at a 320x240 ratio", f"the screen is  {scaled_height}x{scaled_width}", "-")
            valg_update(f"scale = {scale}", "scale +", "scale -", "back")
            need_redraw = True
            selected_valg_3 = False

        if selected_valg_4:
            state = "settings"
            story_update("Settings", "-", "-")
            valg_update("screen", "music", "credits", "back")
            need_redraw = True
            selected_valg_4 = False

    if state == "credits":
        
        if selected_valg_4:
            state = "settings"
            story_update("Settings", "-", "-")
            valg_update("screen", "music", "credits", "back")
            need_redraw = True
            selected_valg_4 = False

    if state == "music":
        #story_update("music","-","-",)
        #valg_update("-","-","-","back",)


        if selected_valg_4:
            state = "settings"
            story_update("Settings", "-", "-")
            valg_update("screen", "music", "credits", "back")
            need_redraw = True
            selected_valg_4 = False
#       _____                      
#      / ____|                     
#     | |  __  __ _ _ __ ___   ___ 
#     | | |_ |/ _` | '_ ` _ \ / _ \
#     | |__| | (_| | | | | | |  __/
#      \_____|\__,_|_| |_| |_|\___|





    if need_redraw:
        redraw()
        need_redraw = False


pygame.quit()