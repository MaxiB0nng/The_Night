import pygame
import story_functions as sf
import short_cut as cut
import choice_tree as tree
import save_load as sl
import audio


def controls(event):
    need_redraw = False

    if event.key in (pygame.K_SPACE, pygame.K_RETURN) and sf.allow_input: 
        audio.soundfx.play("press")
        if not sf.state == "running":
            sf.text_valg()
        need_redraw = True

    elif event.key == pygame.K_DOWN and sf.allow_input:
        audio.soundfx.play("down")
        if tree.move_selceted:
            tree.move("down")
            print("down")
        else:
            sf.valg += 1
            if sf.valg  == 5:
                sf.valg = 1
        need_redraw = True

    elif event.key == pygame.K_UP and sf.allow_input:
        audio.soundfx.play("up")
        if tree.move_selceted:
            tree.move("up")
            print("up")
        else:
            sf.valg -= 1
            if sf.valg == 0:
                sf.valg = 4
        need_redraw = True

    elif event.key == pygame.K_LEFT and sf.allow_input:
        audio.soundfx.play("down")
        if tree.move_selceted:
            tree.move("left")
            print("left")
        elif sf.state == "choice" and sf.valg == 2:
            tree.chapter_load -= 1
            if tree.chapter_load <= -1:
                tree.chapter_load = 0
            tree.on_chapter = False
            tree.x = 0
            tree.y = 0
            tree.place = (tree.x,tree.y)
            tree.load()
        elif sf.state == "music" and sf.valg == 1:
            audio.music.next(-1)
        elif sf.state == "music" and sf.valg == 2:
            audio.music.set_volume(audio.music.volume - 5)
        elif sf.state == "music" and sf.valg == 3:
            audio.soundfx.set_volume(audio.soundfx.volume - 5)
        elif sf.state == "screen" and sf.valg == 1:
            sf.scale -= 0.5
            if sf.scale <= 1:
                sf.scale = 1
            sf.make_screen()
            cut.screen
        need_redraw = True

    elif event.key == pygame.K_RIGHT and sf.allow_input:
        audio.soundfx.play("up")
        if tree.move_selceted:
            tree.move("right")
            print("right")
        elif sf.state == "choice" and sf.valg == 2:
            tree.chapter_load += 1
            max_chapter = sl.get_max_chapter()
            if tree.chapter_load >= max_chapter:
                tree.chapter_load = max_chapter
            tree.on_chapter = False
            tree.x = 0
            tree.y = 0
            tree.place = (tree.x,tree.y)
            tree.load()
        elif sf.state == "music" and sf.valg == 1:
            audio.music.next(1)
        elif sf.state == "music" and sf.valg == 2:
            audio.music.set_volume(audio.music.volume + 5)
        elif sf.state == "music" and sf.valg == 3:
            audio.soundfx.set_volume(audio.soundfx.volume + 5)
        elif sf.state == "screen" and sf.valg == 1:
            sf.scale += 0.5
            if sf.scale >= 6:
                sf.scale = 6
            sf.make_screen()
            cut.screen
        need_redraw = True

    elif event.key == pygame.K_f:
        sf.fullscreen = not sf.fullscreen
        if not sf.fullscreen:
            sf.scale = 3
        sf.make_screen()
        need_redraw = True
        
    elif event.key == pygame.K_m:
        sf.state = "menu"
        tree.is_load = False
        cut.menu()
        sf.redraw(sf.state)

    elif event.key == pygame.K_q:
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    elif event.key == pygame.K_s:
        if not sf.allow_input:
            sf.skip_cutsceen = True
        need_redraw = True

    return need_redraw
