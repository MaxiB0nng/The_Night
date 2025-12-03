import pygame

pygame.init()
pygame.mixer.init()

# Opløsninger for det lavopløselige "canvas"
screen_width = 320
screen_height = 240
scale = 3

# Farver (RGB)
black = (15, 25, 15)
green = (10, 142, 10)



valg = int(1) #de valg som spiler har max 4 
need_redraw = True #hvis den er sand så opdatere den skærmen 



# Endelig skærmstørrelse beregnes
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


#laver valg til playerene

valg_x = 4

valg_1_y = 2
valg_1 = "gå henned til en skove"
text_valg_1 = font.render(valg_1, True, green)
text_valg_b_1 = font.render(valg_1, True, black)

valg_2_y = valg_1_y + 14
valg_2 = "gå vidre igennem skoven"
text_valg_2 = font.render(valg_2, True, green)
text_valg_b_2 = font.render(valg_2, True, black)

valg_3_y = valg_2_y + 14
valg_3 = "_"
text_valg_3 = font.render(valg_3, True, green)
text_valg_b_3 = font.render(valg_3, True, black)

valg_4_y = valg_3_y + 14
valg_4 = "_"
text_valg_4 = font.render(valg_4, True, green)
text_valg_b_4 = font.render(valg_4, True, black)

text_selected = 1
selected_valg = None

#laver story text 
story_y = 3
story = "Du er i en skov."
text_story = font.render(story, True, green)

story_y_2 = 19
story_2 =  "Det er nat."
text_story_2 = font.render(story_2, True, green)

story_y_3 = 36
story_3 =  "test"
text_story_3 = font.render(story_3, True, black)


# Indlæs billede
start_front = pygame.image.load("img/start_screen.png").convert_alpha()
start_cutsceen = pygame.image.load("img/start_cut_sceen.png").convert_alpha()
skove_2_img = pygame.image.load("img/skove_2_0.png").convert_alpha()
skove_2_1_img = pygame.image.load("img/skove_2_1.png").convert_alpha()
skove_camp_img = pygame.image.load("img/skove_camp.png").convert_alpha()
skove_camp_2_img = pygame.image.load("img/skove_camp_2.png").convert_alpha()
camp_fire_img = pygame.image.load("img/camp_fire.png").convert_alpha()
camp_fire_img_2 = pygame.image.load("img/camp_fire_2.png").convert_alpha()
foran_telt_img = pygame.image.load("img/foran_telt.png").convert_alpha()


image_x = 0
image_y = 0


def text_redraw():

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

def redraw():
    print("drawing")

    text_redraw()
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
                    need_redraw = True
                    print("enter pressed")

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

    if need_redraw:
        redraw()
        need_redraw = False

pygame.quit()