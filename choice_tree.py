import pygame
import story_functions as sf
import short_cut as sc
    
box_w = 50
box_h = box_w/2
margin = 5

x_selceted = False

middel_x = 314/2
middel_y = 114/2

x = 0
y = 0

box_list =["0:0","-1:1","0:1","1:1","0:2","-1:2","1:2","-2:2","2:2"]

hint_list = ["-","you have found this","Try starting the game","look around"]
hint = None

is_place = True
place = f"{x}:{y}"


rx = int((middel_x-(box_w/2))+((box_w+margin)*x))
ry = int((middel_y-(box_h/2))+((box_h+margin)*y))

def choice_tree():   
    global rx , ry , x , y, box_list, hint,hint_list
    
    sf.main_canvas.fill(sf.black)
    pygame.draw.rect(sf.main_canvas, sf.green, (2,2,310,110)) 

 
    for item in box_list:
        x_set, y_set = map(int, item.split(":"))
        rx = int((middel_x-(box_w/2))+((box_w+margin)*(x_set-x)))
        ry = int((middel_y-(box_h/2))+((box_h+margin)*(y_set-y)))
        pygame.draw.rect(sf.main_canvas, sf.black,(rx,ry,box_w,box_h),5 ,2)
        if place == "0:0":  
            hint = hint_list[2]
            sc.choice()
        elif place == "-1:1" or place == "0:1" or place ==  "1:1":
            hint = hint_list[3]
            sc.choice()
        else:
            hint = hint_list[0]
        
    pygame.draw.circle(sf.main_canvas, sf.black, (middel_x,middel_y), 2)

def moveing(move):
    global y,x, is_place, place

    if move == 1:
        x -= 1
    if move == 2:
        y -= 1
    if move == 3:
        x += 1
    if move == 4:
        y += 1

    place = f"{x}:{y}"

    if place in box_list:
        is_place = True
    else:
        is_place = False


    if not is_place:
        if move == 1:
            x += 1
        if move == 2:
            y += 1
        if move == 3:
            x -= 1
        if move == 4:
            y -= 1
        is_place = True
        place = f"{x}:{y}"
        choice_tree()
    move = 0