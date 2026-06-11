import pygame

#       ▄▄▄▄                                           
#     ▄█▀▀▀▀█     ██                            ██     
#     ██▄       ███████    ▄█████▄   ██▄████  ███████  
#      ▀████▄     ██       ▀ ▄▄▄██   ██▀        ██     
#          ▀██    ██      ▄██▀▀▀██   ██         ██     
#     █▄▄▄▄▄█▀    ██▄▄▄   ██▄▄▄███   ██         ██▄▄▄  
#      ▀▀▀▀▀       ▀▀▀▀    ▀▀▀▀ ▀▀   ▀▀          ▀▀▀▀  
startup_sequence = [
    (0,(0,"Opening", "The_Night", "Made By MaxiBonng", 1000)),
    (0,(1,"Running simulation", "-", "Made By MaxiBonng", 1000)),
    (0,(2,"Running simulation", "December 12th", "-", 1000)),
    (0,(3,"Running simulation", "December 12th", "Case #19981112", 500)),
    (0,(4,"Loading", "-", "-", 500)),
    (0,(5,"Running", "log.py", "---------- 0%", None)),
    (0,(5,None, "short_cut.py", "##-------- 20%", None)),
    (0,(6,None, "save_load.py", "####------ 40%", None)),
    (0,(6,None, "choice_tree.py", "######---- 60%", None)),
    (0,(7,None, "story_functions.py", "#######--- 70%", None)),
    (0,(7,"Loading", "logo.png", "#######--- 71%", None)),
    (0,(7,None, "start_cut_sceen.png", "#######--- 72%", None)),
    (0,(7,None, "start_screen.png", "#######--- 73%", None)),
    (0,(7,None, "glitch_1.png", "#######--- 74%", None)),
    (0,(7,None, "glitch_2.png", "#######--- 74%", None)),
    (0,(7,None, "glitch_3.png", "#######--- 75%", None)),
    (0,(7,None, "glitch_4.png", "#######--- 75%", None)),
    (0,(7,None, "glitch_5.png", "#######--- 76%", None)),
    (0,(7,None, "glitch_6.png", "#######--- 77%", None)),
    (0,(7,None, "glitch_7.png", "#######--- 77%", None)),
    (0,(7,None, "glitch_8.png", "#######--- 78%", None)),
    (0,(7,None, "glitch_9.png", "#######--- 79%", None)),
    (0,(8,None, "opening_cutsceen_1.png", "########-- 80%", None)),
    (0,(8,None, "opening_cutsceen_2.png", "########-- 80%", None)),
    (0,(8,None, "opening_cutsceen_3.png", "########-- 80%", None)),
    (0,(8,None, "opening_cutsceen_4.png", "########-- 81%", None)),
    (0,(8,None, "opening_cutsceen_5.png", "########-- 81%", None)),
    (0,(8,None, "opening_cutsceen_6.png", "########-- 81%", None)),
    (0,(8,None, "opening_cutsceen_7.png", "########-- 82%", None)),
    (0,(8,None, "opening_cutsceen_8.png", "########-- 82%", None)),
    (0,(8,None, "opening_cutsceen_9.png", "########-- 82%", None)),
    (0,(8,None, "opening_cutsceen_10.png", "########-- 83%", None)),
    (0,(8,None, "opening_cutsceen_11.png", "########-- 83%", None)),
    (0,(8,None, "opening_cutsceen_12.png", "########-- 83%", None)),
    (0,(8,None, "opening_cutsceen_13.png", "########-- 84%", None)),
    (0,(8,None, "opening_cutsceen_14.png", "########-- 84%", None)),
    (0,(8,None, "opening_cutsceen_15.png", "########-- 84%", None)),
    (0,(8,None, "opening_cutsceen_16.png", "########-- 85%", None)),
    (0,(8,None, "opening_cutsceen_17.png", "########-- 85%", None)),
    (0,(8,None, "opening_cutsceen_18.png", "########-- 85%", None)),
    (0,(8,None, "opening_cutsceen_19.png", "########-- 86%", None)),
    (0,(8,None, "opening_cutsceen_20.png", "########-- 86%", None)),
    (0,(8,None, "opening_cutsceen_21.png", "########-- 86%", None)),
    (0,(8,None, "opening_cutsceen_22.png", "########-- 87%", None)),
    (0,(8,None, "opening_cutsceen_23.png", "########-- 87%", None)),
    (0,(8,None, "opening_cutsceen_24.png", "########-- 87%", None)),
    (0,(8,None, "opening_cutsceen_25.png", "########-- 88%", None)),
    (0,(8,None, "opening_cutsceen_26.png", "########-- 88%", None)),
    (0,(8,None, "opening_cutsceen_27.png", "########-- 88%", None)),
    (0,(8,None, "opening_cutsceen_28.png", "########-- 89%", None)),
    (0,(8,None, "opening_cutsceen_29.png", "########-- 89%", None)),
    (0,(8,None, "opening_cutsceen_30.png", "########-- 89%", None)),
    (0,(8,"Running", "The_Night.py", "#########- 90%", 400)),
    (0,(9,"Welcome", "Mr.############", "-", 1000)),
    (0,(9,"-","-","-", 1500))
]

glitch = [pygame.image.load(f"img/start_up/glitch_{i}.png").convert()
        for i in range(1, 10)]
  

#                                                ██                        
#                                                ▀▀                        
#      ▄████▄   ██▄███▄    ▄████▄   ██▄████▄   ████     ██▄████▄   ▄███▄██ 
#     ██▀  ▀██  ██▀  ▀██  ██▄▄▄▄██  ██▀   ██     ██     ██▀   ██  ██▀  ▀██ 
#     ██    ██  ██    ██  ██▀▀▀▀▀▀  ██    ██     ██     ██    ██  ██    ██ 
#     ▀██▄▄██▀  ███▄▄██▀  ▀██▄▄▄▄█  ██    ██  ▄▄▄██▄▄▄  ██    ██  ▀██▄▄███ 
#       ▀▀▀▀    ██ ▀▀▀      ▀▀▀▀▀   ▀▀    ▀▀  ▀▀▀▀▀▀▀▀  ▀▀    ▀▀   ▄▀▀▀ ██ 
#               ██                                                 ▀████▀▀ 
opening_cutsceen_list = [
    (0,(0,"Opening","Opening_cutsceen","Loading .", 1000)),
    (0,(0,"Running","Opening_cutsceen","Loading ..", 1000)),
    (0,(1,None,None,"Loading ...", 500)),
    (0,(1 ,None,"Its night","-", 500)),
    (0,(2 ,None,"Its night",None, 500)),
    (1,(3,7,500)),
    (0,(8 ,None,"Your driving home",None, 500)),
    (1,(9,13,500)),
    (1,(10,13,500)),
    (1,(10,13,500)),
    (0,(10,None,"You just got back from work",None, 500)),
    (1,(11,22,500)),
    (0,(23,None,"-",None, 500)),
    (1,(24,29,500)),
    (0,(30,None,"STARTING GAME","HAVE FUN.", 1000)),
    (0,(0,None,None,"HAVE FUN..", 500)),
    (0,(0,None,None,"HAVE FUN...", 2000)),
]

opening_cutsceen = [pygame.image.load(f"img/opening_cutsceen/opening_cutsceen_{i}.png").convert()
                    for i in range(1, 31)]

#     ▄▄    ▄▄                               
#     ██    ██                               
#     ██    ██   ▄████▄   ████▄██▄   ▄████▄  
#     ████████  ██▀  ▀██  ██ ██ ██  ██▄▄▄▄██ 
#     ██    ██  ██    ██  ██ ██ ██  ██▀▀▀▀▀▀ 
#     ██    ██  ▀██▄▄██▀  ██ ██ ██  ▀██▄▄▄▄█ 
#     ▀▀    ▀▀    ▀▀▀▀    ▀▀ ▀▀ ▀▀    ▀▀▀▀▀  

H_look_for_food_cutsceen = [
    (0,(1,"You look around","-","-",1500)),
    (0,(1,"You find a bun","-","-",1500)),
]

H_look_for_food_img = [
    pygame.image.load(f"img/start_screen.png").convert()
]


H_search_your_kitchen_cutsceen = [
    (0,(1,"You look around","-","-",2500)),
    (0,(1,"Its all empty...","-","-",2500)),
    (0,(1,"You finde a knife","Carefull you can stab people whit that","-",5000)),
]

H_search_your_kitchen_img = [
    pygame.image.load(f"img/start_screen.png").convert()
]


