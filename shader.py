import pygame
import numpy as np
import random

buzz_y = 0
buzz = True

black = (15, 25, 15) #0F190E
green = (10, 142, 10) #0A8E0A
red = (162,8, 0) #A20800

rng = np.random.default_rng()

def noise(plan, noise):
    global buzz , buzz_y,lines_y
    w, h = plan.get_size()
    dark_noise = int(noise - (noise*3))

    shader = rng.integers(-noise, noise, (w, h, 3), dtype=np.int16)
    dark_rows = (np.arange(h) // 2) % 2 == 0 
    n_dark = int(dark_rows.sum())
    shader[:, dark_rows] = rng.integers(dark_noise * 2, dark_noise, (w, n_dark, 3), dtype=np.int16)

    if buzz:
            random_y = random.randint(h // 18, h // 14)
            if random.randint(0, 10) == 0:
                buzz_y -= (random_y * 2)
            else:
                buzz_y += random_y
            if buzz_y < 0:
                buzz_y = 0

            row_numbers = np.arange(h)[None, :]                  
            random_buzz1 = rng.integers(9, 15, (w, 1))           
            random_buzz2 = rng.integers(4, 9,  (w, 1))
            buzz1 = (row_numbers >= buzz_y - random_buzz1) & (row_numbers < buzz_y + random_buzz1)  
            buzz2 = (row_numbers >= buzz_y - random_buzz2) & (row_numbers < buzz_y + random_buzz2)
            shader[buzz1] = rng.integers(30, 80,  (int(buzz1.sum()), 3), dtype=np.int16)
            shader[buzz2] = rng.integers(80, 100, (int(buzz2.sum()), 3), dtype=np.int16)

            if buzz_y >= h:
                buzz_y = 0
                buzz = False

    lines_y = h 

    arr = pygame.surfarray.array3d(plan).astype(np.int16)
    arr += shader
    np.clip(arr, 0, 255, out=arr)
    pygame.surfarray.blit_array(plan, arr.astype(np.uint8))

def crtv_bulge(plan):
    w, h = plan.get_size()
    pixels = pygame.surfarray.array3d(plan)

    pygame.surfarray.blit_array(plan, pixels)

