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

block_type = 0

chapter = 1



def load_choice_tree():
    with open("choice_tree.json", "r") as f:
        data = json.load(f)

    chapter = data["chapters"][0]

    for box in chapter["box_list"]:
        location = box["box_location"]        # e.g. "0:0"
        box_type = box["box_type"]            # "cutsceen" / "normal"
        hint = box["box_hint"]                # "look around"
        arrows = box["arrow_to_boxs"]         # ["-1:1", "0:1", "2:1"]
        box_state = box["box_state"]          # "H_livingroom"

    