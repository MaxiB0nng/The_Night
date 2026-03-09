

def load():
    with open("save.tnp", "r") as f:
        data = f.read().strip()
    
    chapter_str, boxes_str = data.split("b")
    chapter = int(chapter_str)

    box_strings = boxes_str.split(":")

    for box in box_strings:
        box_chapter, choice, max_optioins, option = box.split(".")
        print(box_chapter, choice, max_optioins, option)

load()