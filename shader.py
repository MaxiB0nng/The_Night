import pygame
import numpy as np
import random

buzz_y = 0
buzz = True


black = (15, 25, 15) #0F190E
green = (10, 142, 10) #0A8E0A
red = (162,8, 0) #A20800


def noise(plan, noise):
    global buzz , buzz_y
    w, h = plan.get_size()
    shader = np.random.randint(-noise, noise, (w, h, 3)).astype(np.int16)


    if buzz:
        random_y = random.randint(h // 18, h // 14)

        if random.randint(0, 10) == 0:
            buzz_y -= (random_y * 3)
        else:
            buzz_y += random_y

        if buzz_y < 0:
            buzz_y = 0
        
        buzz_x = 0
        while buzz_x < w:
        
            random_buzz = random.randint(h // 18, h // 12)

            min_buzz = int(max(0, buzz_y - random_buzz))
            max_buzz = int(min(h, buzz_y + random_buzz))

            slice_h = max_buzz - min_buzz
            if slice_h > 0:
                shader[buzz_x, min_buzz:max_buzz] = np.random.randint(20, 60, (slice_h, 3)).astype(np.int16)


            random_buzz = random.randint(h // 22, h // 18)
            

            min_buzz = int(max(0, buzz_y - random_buzz))
            max_buzz = int(min(h, buzz_y + random_buzz))

            slice_h = max_buzz - min_buzz
            if slice_h > 0:
                shader[buzz_x, min_buzz:max_buzz] = np.random.randint(60, 80, (slice_h, 3)).astype(np.int16)

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

