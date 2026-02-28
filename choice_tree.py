import pygame
import story_functions as sf

#main_canvas_width = 314
#main_canvas_height = 114

def choice_tree():    
    print("choice update")
    sf.main_canvas.fill(sf.black)
    pygame.draw.rect(sf.main_canvas, sf.green, (2,2,310,110))
    
    
    text = "hello"
    box_w = 60
    box_h = box_w/2



    pygame.draw.rect(sf.main_canvas, sf.black,(((314-box_w)/2),10,box_w,box_h),5 ,2)

    pygame.draw.rect(sf.main_canvas, sf.black,(((314-box_w)/2),10,box_w,box_h),0 ,2)




    box_list = [("0.0.0.0","None","try starting the game"),
                ("0.1.2.0","0.0.0.0","look around"),
                ("0.1.2.1","0.0.0.0","look around"),
                ("0.1.2.2","0.0.0.0","look around")]
    



