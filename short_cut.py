import story_functions as sf


def menu():
    sf.story_update("Welcome to The Night", "Case #19981112", "you can always press Q to return to the main menu")
    sf.valg_update("Continue","Settings","Choice Tree", "-")

def settings():
    sf.story_update("Settings", "-", "-")
    sf.valg_update("screen", "music", "credits", "back")

def screen():
    sf.story_update("The screen is fixed at a 320x240 ratio", f"the screen is  {sf.scaled_height}x{sf.scaled_width}", "-")
    sf.valg_update(f"scale = {sf.scale}", "scale +", "scale -", "back")

def choice():
    sf.story_update("Here you can see your progress in from of a tree", "-", "-")
    sf.valg_update("Up", "Down","Left","Back")


