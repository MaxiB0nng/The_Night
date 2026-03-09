import game


def load():
    with open("save.thp", "r") as f:
        data = f.read().strip()
    
    chapter_str, boxes_str = data.split("b")
    chapter = int(chapter_str)

    box_strings = boxes_str.split(":")