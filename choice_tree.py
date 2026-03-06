import pygame
import story_functions as sf
import short_cut as sc
    
box_w = 50
box_h = box_w/2
margin = 5
r = box_h/2

move_selceted = False

middel_x = 314/2
middel_y = 114/2

x = 0
y = 0

block_type = 0
chapter = 0

#x y blocktype
box_list_1 = [    "0:0:1",
         "-1:1:0","0:1:0",        "2:1:0",
"-2:2:0","-1:2:0","0:2:0","1:2:0","2:2:0","3:2:0",
                  "0:3:0",        "2:3:0",
                  "0:4:1",        "2:4:1"]

arrow_list_1 = ["0:1","0:2","0:3","1:4","1:5","2:6","3:7","3:8","3:9",
                "6:10","8:11","10:12","11:13"]

hint_list = ["-","you have found this","Try starting the game!","look around","are you hungry?","looking for something?",
             "maybe take a rest?","be curious","those dam screens!","take a rest dude","dont you have better things to do","go to sleep",
             "arent you tired after work?"]
hint = None

place = f"{x}:{y}"

rx = int((middel_x-(box_w/2))+((box_w+margin)*x))
ry = int((middel_y-(box_h/2))+((box_h+margin)*y))

def choice_tree():   
    global rx , ry, box_list_1, hint,hint_list, block_type

    sf.main_canvas.fill(sf.black)
    pygame.draw.rect(sf.main_canvas, sf.green, (2,2,310,110)) 

    for arrow in arrow_list_1:
        a_from, a_to = map(int, arrow.split(":"))
        
        from_box = box_list_1[a_from]
        x_set_from, y_set_from, block_type = map(int, from_box.split(":"))

        to_box = box_list_1[a_to]
        x_set_to, y_set_to, block_type = map(int, to_box.split(":"))

        from_x = int(middel_x+((box_w+margin)*(x_set_from-x))-1)
        from_y = int(middel_y+((box_h+margin)*(y_set_from-y))-1)

        to_x = int(middel_x+((box_w+margin)*(x_set_to-x))-1)
        to_y = int(middel_y+((box_h+margin)*(y_set_to-y))-1)

        pygame.draw.lines(sf.main_canvas,sf.black,False,[(from_x,from_y),(to_x,from_y),(to_x,to_y)],4)

    for item in box_list_1:
        x_set, y_set, block_type = map(int, item.split(":"))
        rx = int((middel_x-(box_w/2))+((box_w+margin)*(x_set-x)))
        ry = int((middel_y-(box_h/2))+((box_h+margin)*(y_set-y)))
        if block_type == 0:
            pygame.draw.rect(sf.main_canvas, sf.black,(rx,ry,box_w,box_h),5 ,2)
            pygame.draw.rect(sf.main_canvas, sf.green,((rx+2),(ry+2),(box_w-4),(box_h-4)),0,2)
        elif block_type == 1:
           pygame.draw.ellipse(sf.main_canvas, sf.black,(rx,ry,box_w,box_h),4)
           pygame.draw.ellipse(sf.main_canvas,sf.green,((rx+2),(ry+2),(box_w-4),(box_h-4)) )
        if place == "0:0":  
            hint = hint_list[2]
            sc.choice()
        elif place == "-1:1" or place == "0:1" or place ==  "1:1":
            hint = hint_list[3]
            sc.choice()
        elif place == "-2:2":
            hint = hint_list[4]
            sc.choice()
        elif place == "-1:2":
            hint = hint_list[5]
            sc.choice()
        elif place == "0:2":
            hint = hint_list[6]
            sc.choice()
        elif place == "1:2":
            hint = hint_list[7]
            sc.choice()
        elif place == "2:2":
            hint = hint_list[9]
            sc.choice()
        elif place == "3:2":
            hint = hint_list[8]
            sc.choice()
        elif place == "0:3":
            hint = hint_list[10]
            sc.choice()
        elif place == "2:3":
            hint = hint_list[11]
            sc.choice()
        elif place == "0:4" or place == "2:4":
            hint = hint_list[12]
            sc.choice()

        else:
            hint = hint_list[0]
    pygame.draw.circle(sf.main_canvas, sf.red, (middel_x,middel_y), 3)

def check_out():
    global is_place
    for item in box_list_1:
        x_set, y_set, block_type = map(int, item.split(":"))
        check_place = f"{x_set}:{y_set}"
        if check_place == place:
            is_place = True
            break
        else:
            is_place = False
            continue

def moveing(move):
    global place, x,y

    if move == "a":
        x -= 1
    if move == "w":
        y -= 1
    if move == "d":
        x += 1
    if move == "s":
        y += 1

    place = f"{x}:{y}"

    check_out()

    if is_place == False:
        if move == "a":
            x += 1
        if move == "w":
            y += 1
        if move == "d":
            x -= 1
        if move == "s":
            y -= 1
        place = f"{x}:{y}"
        check_out()
        choice_tree()
        move = None