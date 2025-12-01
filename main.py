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

# -----------------------------------------
# STATUSKONTROL-VARIABLER (Flags)
# Disse bruges til at holde styr på tilstande og aktiveringer i spillet
# -----------------------------------------
started = False  # Indikerer, om spillet er startet
start_front_selected = False  # Om startmenu/front er valgt
enter_pressed = False  # Om enter-knappen er blevet trykket
text_set = False  # Om teksten er indsat
selected = False  # Om noget er valgt
text_print_on = False  # Om tekstudskrivning er aktiv
story_visible = False  # Om historietekst er synlig
music_playing = False  # Om musikken spiller i baggrunden

# Cutscene-status
state = "-"

# Genstandsstatus
gren_I = False  # Status for, om spilleren har fået/fundet grenen
campfire_I = True  # Aktivt lejrbål - angiver om lejrbålet er tændt
nøgle_I = False


# -----------------------------------------
# TIDSRELATEREDE VARIABLER
# Disse bruges til at holde styr på tidspunkter og tidsintervaller
# -----------------------------------------
blink_interval = 500  # Intervallet mellem tekstblink i millisekunder
last_blink_time = 0  # Det tidspunkt, hvor den sidste blinkning opstod
show_story_timer = 0  # Tidspunktet, hvor historieteksten blev startet
show_story_duration = 1000  # Hvor længe historieteksten skal vises (i ms)
valg_cooldown = 1000
last_enter_time = 0  # Tidspunkt for sidste ENTER

# -----------------------------------------
# GAMEPLAY-RELATEREDE VARIABLER
# Disse bruges til at holde styr på gameplay og animation
# -----------------------------------------
game = False  # Om spillet kører
cutsceen_y = 0  # Y-positionen af en cutscene (til animation)
cutsceen_speed = 5  # Hastigheden på cutscene-animationens bevægelse


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

# Indlæs musikfilen og afspil
music_files = {
    "intro": "music/intro.WAV",
    "campfire": "music/campfire.WAV",

}
current_music = "campfire"


# Lav det primære canvas
canvas = pygame.Surface((screen_width, screen_height))

main_canvas_width = 314
main_canvas_height = 114
main_canvas = pygame.Surface((main_canvas_width, main_canvas_height))  # Nyt canvas
main_canvas.fill(black)  # Fyld med sort

story_canvas_width = 314
story_canvas_height = 58
story_canvas = pygame.Surface((story_canvas_width, story_canvas_height))  # Nyt canvas
story_canvas.fill(black)  # Fyld med sort

text_canvas_width = 314
text_canvas_height = 58
text_canvas = pygame.Surface((text_canvas_width, text_canvas_height))  # Nyt canvas
text_canvas.fill(black)  # Fyld med sort

# START TEXT
text = "Welcome to THE NIGHT "  # Tekst til visning
text_green = font.render(text, True, green)
text_black = font.render(text, True, black)
text_x = (text_canvas_width - text_green.get_width()) // 2  # Centrer teksten horisontalt
text_y = (text_canvas_height - text_green.get_height()) // 2  # Centrer teksten vertikalt


#x og y for valg text
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

valg_5 = "test"

text_selected = 1
selected_valg = valg_5


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


def valg_update():
    global valg_1 ,valg_2, valg_3, valg_4 
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

def story_update(text1, text2):
    global text_story, text_story_2
    text_story = font.render(text1, True, green)
    text_story_2 = font.render(text2, True, green)


def text_print():
    global selected_valg
    global text_selected
    global text_story_3
    global story_3
    global show_story_timer, story_visible, story_3, text_story_3, enter_pressed
    # Tøm canvas og skriv teksten
    text_canvas.fill(black)

    if text_selected == 1:
        pygame.draw.rect(text_canvas, green, (0, valg_1_y, 318, 13))
        text_canvas.blit(text_valg_b_1, (valg_x, valg_1_y))
        text_canvas.blit(text_valg_2, (valg_x, valg_2_y))
        text_canvas.blit(text_valg_3, (valg_x, valg_3_y))
        text_canvas.blit(text_valg_4, (valg_x, valg_4_y))
    elif text_selected == 2:
        pygame.draw.rect(text_canvas, green, (0, valg_2_y, 318, 13))
        text_canvas.blit(text_valg_1, (valg_x, valg_1_y))
        text_canvas.blit(text_valg_b_2, (valg_x, valg_2_y))
        text_canvas.blit(text_valg_3, (valg_x, valg_3_y))
        text_canvas.blit(text_valg_4, (valg_x, valg_4_y))
    elif text_selected == 3:
        pygame.draw.rect(text_canvas, green, (0, valg_3_y, 318, 13))
        text_canvas.blit(text_valg_1, (valg_x, valg_1_y))
        text_canvas.blit(text_valg_2, (valg_x, valg_2_y))
        text_canvas.blit(text_valg_b_3, (valg_x, valg_3_y))
        text_canvas.blit(text_valg_4, (valg_x, valg_4_y))
    elif text_selected == 4:
        pygame.draw.rect(text_canvas, green, (0, valg_4_y, 318, 13))
        text_canvas.blit(text_valg_1, (valg_x, valg_1_y))
        text_canvas.blit(text_valg_2, (valg_x, valg_2_y))
        text_canvas.blit(text_valg_3, (valg_x, valg_3_y))
        text_canvas.blit(text_valg_b_4, (valg_x, valg_4_y))

    if enter_pressed:

        # Opdater teksten baseret på valget
        if text_selected == 1:
            selected_valg = valg_1
        elif text_selected == 2:
            selected_valg = valg_2
        elif text_selected == 3:
            selected_valg = valg_3
        elif text_selected == 4:
            selected_valg = valg_4

        # Opdater historetekst (story_3) og indstil flag til at vise teksten
        story_3 = f"Du valgte {selected_valg}"
        text_story_3 = font.render(story_3, True, green)
        story_visible = True  # Aktiver visning af teksten
        show_story_timer = pygame.time.get_ticks()  # Start timeren

        # Stop enter_pressed for at undgå gentagelse
        enter_pressed = False

    if story_visible:
        current_time = pygame.time.get_ticks()  # Hent nuværende tidspunkt
        if current_time - show_story_timer < show_story_duration:
            # Viser den valgte tekst
            story_canvas.blit(text_story_3, (valg_x, story_y_3))
        else:
            # Skjul teksten efter tiden er gået
            story_visible = False



def redraw():

    if state == "skove_2":
        main_canvas.blit(skove_2_img, (image_x, image_y))


    if state == "skove_2_1":
        main_canvas.blit(skove_2_1_img, (image_x, image_y))

    if state == "skove_camp":
        if campfire_I:
            main_canvas.blit(skove_camp_img, (image_x, image_y))
        else:
            main_canvas.blit(skove_camp_2_img, (image_x, image_y))

    if state == "campfire":
        if campfire_I:
            main_canvas.blit(camp_fire_img, (image_x, image_y))
        else:
            main_canvas.blit(camp_fire_img_2, (image_x, image_y))

redraw()


# Spil-loop
running = True
while running:
    for event in pygame.event.get():
        # Lukning af spillet
        if event.type == pygame.QUIT:
            running = False

        # Håndter KEYDOWN tastetryk
        if event.type == pygame.KEYDOWN:

            current_time = pygame.time.get_ticks()  # Hent nuværende tid
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:  # Space/enter tast blev trykket
                if current_time - last_enter_time > valg_cooldown:  # Tjek om cooldown er ovre
                    # Valget bliver foretaget
                    enter_pressed = True
                    print("pressed enter")


            elif event.key == pygame.K_DOWN:
                text_selected += 1
                if text_selected > 4:
                    text_selected = 1  # Wrap to the first option
            elif event.key == pygame.K_UP:
                text_selected -= 1
                if text_selected < 1:
                    text_selected = 4  # Wrap to the last option


        # Håndter KEYUP tastetryk
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:  # Space tasten blev sluppet
                    enter_pressed = False


    # ------story------

        # Tøm det primære canvas (grøn ramme + sort baggrund)

      # Fyld baggrunden sort
    story_canvas.fill(black)
    pygame.draw.rect(canvas, green, (1, 1, 318, 238))  # Grøn kant
    # Tøm det sorte hoved-canvas, og tegn noget indeni
    main_canvas.fill(black) # Ryd det sorte canvas
    main_canvas.blit(start_front, (image_x, image_y))

    if not start_front_selected:
        story_canvas.fill(black)
        pygame.draw.rect(story_canvas, green, (0, 22, 318, 13))
        story_canvas.blit(text_black, (text_x, text_y))  # Tegn teksten midt på tekst-canvas
    else:
        story_canvas.blit(text_green, (text_x, text_y))  # Tegn teksten midt på tekst-canvas

    if not started:
        # Opdater blinking af teksten mellem grøn og sort
        current_time = pygame.time.get_ticks()  # Hent den aktuelle tid
        if current_time - last_blink_time > blink_interval:  # Skift tekstfarve efter interval
            start_front_selected = not start_front_selected  # Skift mellem grøn (True) og sort (False)
            last_blink_time = current_time  # Opdatér sidste blinktid

    if started:
        main_canvas.fill(green)

    if game:
        main_canvas.blit(start_cutsceen, (image_x, cutsceen_y))

    if state == "cutsceen_1":
        story_canvas.blit(text_story, (valg_x, story_y))
        story_canvas.blit(text_story_2, (valg_x, story_y_2))
  


    if enter_pressed:
        started = True
    
    if started:
        story_canvas.fill(black)
        game = True

    if game:
        redraw()
        if cutsceen_y > -114:
            cutsceen_y -= cutsceen_speed
            pygame.time.delay(250)
        else:
            state = "cutsceen_1"


    if state == "cutsceen_1":
        text_print_on = True
        text_print()
        story_update("Du er i en skov", "det er nat")

        valg_1 = "gå henned til et træ"
        valg_2 = "gå vidre igennem skoven"
        valg_3 = "-"
        valg_update()

        if selected_valg == valg_1: #gå henfra start til et træ
            state = "skove_2"
            redraw()


        if selected_valg == valg_2: #gå virder igennem skoven
            state = "skove_camp"
            redraw()


    if state == "skove_2":
        story_update("du gå vider i gennem skoven." ,"du ser en gren")
        valg_1 = "gå vidre igennem skoven"
        if campfire_I == False or nøgle_I:
            valg_2 = "-"
        else:
            valg_2 = "knæk grenen af treet"
        valg_3 = "-"
        valg_4 = "-"
        valg_update()

        if selected_valg == valg_1:
            state = "skove_camp"
            redraw()

        if selected_valg == valg_2:
            if campfire_I or nøgle_I == False:
                state = "skove_2_1"
                gren_I = True
                redraw()
                

    if state == "skove_2_1":
        story_update("du toh en grenen af treet" , "du her nu en gren")

        valg_1 = "gå vidre igennem skoven"
        valg_2 = "-"
        valg_3 = "-"
        valg_4 = "-"
        valg_update()

        if selected_valg == valg_1:
            state = "skove_camp"
            redraw()
            

    if state == "skove_camp":
        story_update("du kommer til en lille lejersted" , "det er et bål som lyser klart")


        valg_1 = "gå tilbage til skoven"
        valg_2 = "gå vider i gennem skoven til en hytte"
        valg_3 = "gå hen til telt"
        valg_4 = "gå hen til bålet"
        valg_update()

        if selected_valg == valg_1:
            if gren_I or campfire_I == False or nøgle_I:
                state = "skove_2_1"
                redraw()
            else:
                state = "skove_2"
                redraw()



        if selected_valg == valg_3:
            state = "telt"
            redraw()


        if selected_valg == valg_4:
            state = "campfire"
            redraw()
  

    if state == "campfire":
        story_update("du gå tætter på ilden" , "den er varm")

        valg_1 = "gå tilbage til lejeren"

        if gren_I:
            valg_2 = "sluk bålet"
        else:
            valg_2 = "-"

        if campfire_I == False:
            if nøgle_I:
                valg_3 = "-"
            else:
                valg_3 = "tage nøglen"
        else:
            valg_3 = "-"
        valg_4 = "-"
        valg_update()

        if selected_valg == valg_1:
            state = "skove_camp"
            redraw()

        if selected_valg == valg_2:
            if gren_I:
                campfire_I = False
                gren_I = False
                redraw()

        if selected_valg == valg_3:
            if campfire_I == False:
                nøgle_I = True
                story_update("du har en en nøgle" , "-")

    #------mucik ----

   ## Musikvalg baseret på tilstand
   #if running and not cutsceen_1 and current_music != "intro":
   #    # Indlæs og spil "intro"-musikken
   #    pygame.mixer.music.stop()  # Stop nuværende musik
   #    pygame.mixer.music.load(music_files["intro"])  # Indlæs intro-musik
   #    pygame.mixer.music.play(-1)  # Spil musikken i loop
   #    current_music = "intro"  # Registrer, at "intro" spiller
   #    music_playing = True

   #elif cutsceen_1 and current_music != "campfire":
   #    # Indlæs og spil "campfire"-musikken
   #    pygame.mixer.music.stop()  # Stop nuværende musik
   #    pygame.mixer.music.load(music_files["campfire"])  # Indlæs campfire-musik
   #    pygame.mixer.music.play(-1)  # Spil musikken i loop
   #    current_music = "campfire"  # Registrer, at "campfire" spiller
   #    music_playing = True

    canvas.blit(main_canvas, (3, 3))  # Tegn hoved-canvas på det primære canvas
    canvas.blit(story_canvas, (3, 119))  # Tegn tekst-canvas nederst i det primære canvas
    canvas.blit(text_canvas, (3, 179))  # Tegn tekst-canvas nederst i det primære canvas

    # Skalér det samled e canvas og tegn det på skærmen
    scaled_canvas = pygame.transform.scale(canvas, (scaled_width, scaled_height))
    SCREEN.blit(scaled_canvas, (0, 0))

    # Opdater skærmen
    pygame.display.flip()

pygame.quit()