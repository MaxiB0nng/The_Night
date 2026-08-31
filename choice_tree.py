import pygame
import story_functions as sf
import short_cut as cut
import save_load as sl
import json

box_w = 50
box_h = box_w/2
margin = 5
r = box_h/2

move_selceted = False

middel_x = 314/2
middel_y = 114/2

x = 0
y = 0



is_load = False

def load():
    global  location_list, box_type_list, hint_list, arrows_list, box_state_list, is_load, chapter_load
    sl.load("choice_tree")

    with open("choice_tree.json", "r") as f:
        data = json.load(f)

    chapter_needet = []
    
    for number in data["chapters"]:
        chapter_needet.append(number["chapter_value"])

    for number in chapter_needet:
        if sl.tree_chapter == number:
            chapter_load_index = number - 1
            chapter_load = number
            continue

    chapter_data = data["chapters"][chapter_load_index]

    location_list = []
    box_type_list = []
    hint_list = []
    arrows_list = []
    box_state_list = []

    for box in chapter_data["box_list"]:
        location_list.append(box["box_location"])        # e.g. "0:0"
        box_type_list.append(box["box_type"])            # "cutsceen" / "normal"
        hint_list.append(box["box_hint"])                # "look around"
        arrows_list.append(box["arrow_to_boxs"])          # ["-1:1", "0:1", "2:1"]
        box_state_list.append(box["box_state"])           # "H_livingroom"
    is_load = True

    draw()


def draw():
    sf.main_canvas.fill(sf.black)
    pygame.draw.rect(sf.main_canvas, sf.green, (2,2,310,110)) 

    rx = int((middel_x-(box_w/2))+((box_w+margin)*x))
    ry = int((middel_y-(box_h/2))+((box_h+margin)*y))

    for item,box_type,hint,arrows,box_state in zip(location_list,box_type_list,hint_list,arrows_list,box_state_list): 

        visted_list = sl.visited[chapter_load]

        for states in visted_list:
