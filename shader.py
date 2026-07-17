import pygame
import numpy as np
import random

buzz_y = 0
buzz = True


black = (15, 25, 15) #0F190E
green = (10, 142, 10) #0A8E0A
red = (162,8, 0) #A20800




def noise(plan, noise):
    global buzz , buzz_y,lines_y
    w, h = plan.get_size()
    shader = np.zeros((w, h, 3), dtype=np.int16)


    lines_height = int(2)
    actual_lines_height = 0
    dark_noise = int(noise - (noise*3) )
    
    make_line = True
    


    lines_y = 0
    while lines_y < h:


        if actual_lines_height == lines_height:
            make_line = not make_line
            actual_lines_height = 0

        if  make_line:
            shader[:, lines_y] = np.random.randint(dark_noise*2, dark_noise, (w, 3)).astype(np.int16)
            actual_lines_height += 1
        else:
            shader[:, lines_y] = np.random.randint(-noise, noise, (w, 3)).astype(np.int16)
            actual_lines_height += 1
            
        lines_y += 1


    if buzz:
        random_y = random.randint(h // 18, h // 14)

        if random.randint(0, 10) == 0:
            buzz_y -= (random_y * 2)
        else:
            buzz_y += random_y

        if buzz_y < 0:
            buzz_y = 0
        
        buzz_x = 0
        while buzz_x < w:
        
            random_buzz = random.randint(9, 15)

            min_buzz = int(max(0, buzz_y - random_buzz))
            max_buzz = int(min(h, buzz_y + random_buzz))

            slice_h = max_buzz - min_buzz
            if slice_h > 0:
                shader[buzz_x, min_buzz:max_buzz] = np.random.randint(30, 80, (slice_h, 3)).astype(np.int16)


            random_buzz = random.randint(4,9)
            

            min_buzz = int(max(0, buzz_y - random_buzz))
            max_buzz = int(min(h, buzz_y + random_buzz))

            slice_h = max_buzz - min_buzz
            if slice_h > 0:
                shader[buzz_x, min_buzz:max_buzz] = np.random.randint(80, 100, (slice_h, 3)).astype(np.int16)

            buzz_x += 1

        if buzz_y >= h:
            buzz_y = 0
            buzz = False


    arr = pygame.surfarray.array3d(plan).astype(np.int16)
    arr += shader
    np.clip(arr, 0, 255, out=arr)
    pygame.surfarray.blit_array(plan, arr.astype(np.uint8))


def crtv_bulge(plan):
    w, h = plan.get_size()
    pixels = pygame.surfarray.array3d(plan)


    pygame.surfarray.blit_array(plan, pixels)

