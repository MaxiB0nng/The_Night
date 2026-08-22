import pygame

img = pygame.image.load


#       ▄▄▄▄                                           
#     ▄█▀▀▀▀█     ██                            ██     
#     ██▄       ███████    ▄█████▄   ██▄████  ███████  
#      ▀████▄     ██       ▀ ▄▄▄██   ██▀        ██     
#          ▀██    ██      ▄██▀▀▀██   ██         ██     
#     █▄▄▄▄▄█▀    ██▄▄▄   ██▄▄▄███   ██         ██▄▄▄  
#      ▀▀▀▀▀       ▀▀▀▀    ▀▀▀▀ ▀▀   ▀▀          ▀▀▀▀  
startup_sequence = [
    ("frame",(0,"-","-","-",15000)),
    ("frame",(0,"Opening", "The_Night", "Made By MaxiBonng", 1000)),
    ("frame",(1,"Running simulation", "-", "Made By MaxiBonng", 1000)),
    ("frame",(2,"Running simulation", "December 12th", "-", 1000)),
    ("frame",(3,"Running simulation", "December 12th", "Case #19981112", 500)),
    ("frame",(4,"Loading", "-", "-", 500)),
    ("frame",(5,"Running", "log.py", "---------- 0%", None)),
    ("frame",(5,None, "short_cut.py", "##-------- 20%", None)),
    ("frame",(6,None, "save_load.py", "####------ 40%", None)),
    ("frame",(6,None, "choice_tree.py", "######---- 60%", None)),
    ("frame",(7,None, "story_functions.py", "#######--- 70%", None)),
    ("frame",(7,"Loading", "logo.png", "#######--- 71%", None)),
    ("frame",(7,None, "start_cut_sceen.png", "#######--- 72%", None)),
    ("frame",(7,None, "start_screen.png", "#######--- 73%", None)),
    ("frame",(7,None, "glitch_1.png", "#######--- 74%", None)),
    ("frame",(7,None, "glitch_2.png", "#######--- 74%", None)),
    ("frame",(7,None, "glitch_3.png", "#######--- 75%", None)),
    ("frame",(7,None, "glitch_4.png", "#######--- 75%", None)),
    ("frame",(7,None, "glitch_5.png", "#######--- 76%", None)),
    ("frame",(7,None, "glitch_6.png", "#######--- 77%", None)),
    ("frame",(7,None, "glitch_7.png", "#######--- 77%", None)),
    ("frame",(7,None, "glitch_8.png", "#######--- 78%", None)),
    ("frame",(7,None, "glitch_9.png", "#######--- 79%", None)),
    ("frame",(8,None, "opening_cutsceen_1.png", "########-- 80%", None)),
    ("frame",(8,None, "opening_cutsceen_2.png", "########-- 80%", None)),
    ("frame",(8,None, "opening_cutsceen_3.png", "########-- 80%", None)),
    ("frame",(8,None, "opening_cutsceen_4.png", "########-- 81%", None)),
    ("frame",(8,None, "opening_cutsceen_5.png", "########-- 81%", None)),
    ("frame",(8,None, "opening_cutsceen_6.png", "########-- 81%", None)),
    ("frame",(8,None, "opening_cutsceen_7.png", "########-- 82%", None)),
    ("frame",(8,None, "opening_cutsceen_8.png", "########-- 82%", None)),
    ("frame",(8,None, "opening_cutsceen_9.png", "########-- 82%", None)),
    ("frame",(8,None, "opening_cutsceen_10.png", "########-- 83%", None)),
    ("frame",(8,None, "opening_cutsceen_11.png", "########-- 83%", None)),
    ("frame",(8,None, "opening_cutsceen_12.png", "########-- 83%", None)),
    ("frame",(8,None, "opening_cutsceen_13.png", "########-- 84%", None)),
    ("frame",(8,None, "opening_cutsceen_14.png", "########-- 84%", None)),
    ("frame",(8,None, "opening_cutsceen_15.png", "########-- 84%", None)),
    ("frame",(8,None, "opening_cutsceen_16.png", "########-- 85%", None)),
    ("frame",(8,None, "opening_cutsceen_17.png", "########-- 85%", None)),
    ("frame",(8,None, "opening_cutsceen_18.png", "########-- 85%", None)),
    ("frame",(8,None, "opening_cutsceen_19.png", "########-- 86%", None)),
    ("frame",(8,None, "opening_cutsceen_20.png", "########-- 86%", None)),
    ("frame",(8,None, "opening_cutsceen_21.png", "########-- 86%", None)),
    ("frame",(8,None, "opening_cutsceen_22.png", "########-- 87%", None)),
    ("frame",(8,None, "opening_cutsceen_23.png", "########-- 87%", None)),
    ("frame",(8,None, "opening_cutsceen_24.png", "########-- 87%", None)),
    ("frame",(8,None, "opening_cutsceen_25.png", "########-- 88%", None)),
    ("frame",(8,None, "opening_cutsceen_26.png", "########-- 88%", None)),
    ("frame",(8,None, "opening_cutsceen_27.png", "########-- 88%", None)),
    ("frame",(8,None, "opening_cutsceen_28.png", "########-- 89%", None)),
    ("frame",(8,None, "opening_cutsceen_29.png", "########-- 89%", None)),
    ("frame",(8,None, "opening_cutsceen_30.png", "########-- 89%", None)),
    ("frame",(8,"Running", "The_Night.py", "#########- 90%", 400)),
    ("frame",(9,"Welcome", "Mr.############", "-", 1000)),
    ("frame",(9,"-","-","-", 1500))
]

glitch = [img(f"img/start_up/glitch_{i}.png").convert()
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
    ("frame",(0,"Opening","Opening_cutsceen","Loading .", 1000)),
    ("frame",(0,"Running","Opening_cutsceen","Loading ..", 1000)),
    ("frame",(1,None,None,"Loading ...", 500)),
    ("frame",(1 ,None,"Its night","-", 500)),
    ("frame",(2 ,None,"Its night",None, 500)),
    ("from_to",(3,7,500)),
    ("frame",(8 ,None,"Your driving home",None, 500)),
    ("from_to",(9,13,500)),
    ("from_to",(10,13,500)),
    ("from_to",(10,13,500)),
    ("frame",(10,None,"You just got back from work",None, 500)),
    ("from_to",(11,22,500)),
    ("frame",(23,None,"-",None, 500)),
    ("from_to",(24,29,500)),
    ("frame",(30,None,"STARTING GAME","HAVE FUN.", 1000)),
    ("frame",(0,None,None,"HAVE FUN..", 500)),
    ("frame",(0,None,None,"HAVE FUN...", 2000)),
]

opening_cutsceen = [img(f"img/opening_cutsceen/opening_cutsceen_{i}.png").convert()
                    for i in range(1, 31)]

#     ▄▄    ▄▄                               
#     ██    ██                               
#     ██    ██   ▄████▄   ████▄██▄   ▄████▄  
#     ████████  ██▀  ▀██  ██ ██ ██  ██▄▄▄▄██ 
#     ██    ██  ██    ██  ██ ██ ██  ██▀▀▀▀▀▀ 
#     ██    ██  ▀██▄▄██▀  ██ ██ ██  ▀██▄▄▄▄█ 
#     ▀▀    ▀▀    ▀▀▀▀    ▀▀ ▀▀ ▀▀    ▀▀▀▀▀  

H_look_for_food_cutsceen = [
    ("frame",(1,"You look around","-","-",500)),
    ("from_to",(2,4,500)),
    ("frame",(5,"You find a bun","-","-",1000)),

]

H_look_for_food_img = [   
   img(f"img/Home/H_look_for_food1.png").convert(),
   img(f"img/Home/H_look_for_food2.png").convert(),
   img(f"img/Home/H_look_for_food3.png").convert(),
   img(f"img/Home/H_look_for_food4.png").convert(),
   img(f"img/Home/H_look_for_food5.png").convert()
]

H_search_your_kitchen_cutsceen = [
    ("frame",(1,"You look around","-","-",2500)),
    ("frame",(2,"Its all empty...","-","-",2500)),
    ("frame",(3,"You finde a knife","Carefull you can stab people whit that","-",5000))
]

H_search_your_kitchen_img = [
    img(f"img/Home/H_search1.png").convert(),
    img(f"img/Home/H_search2.png").convert(),
    img(f"img/Home/H_search3.png").convert()
]

H_watch_tv_cutseen = [
    ("frame",(1,"You watch som tv","-","-",1000)),
    ("frame",(2,"You are starting to become tired","-","-",1000)),
    ("frame",(3,"-","-","-",1000)),
    ("frame",(4,"-","-","-",1000))
]

H_watch_tv_img = [
    img(f"img/Home/H_tv1.png").convert(),
    img(f"img/Home/H_tv2.png").convert(),
    img(f"img/Home/H_tv3.png").convert(),
    img(f"img/Home/H_tv4.png").convert()
]

H_fall_asleep_cutsceen = [
    ("frame",(1,"You lay down","-","-",1000)),
    ("frame",(2,"-","-","-",1000)),
    ("frame",(3,"-","-","-",1000)),
    ("frame",(4,"You are starting to become tired","-","-",1000)),
    ("frame",(5,"-","-","-",1000)),
    ("frame",(6,"-","-","-",1000))
]

H_fall_asleep_img = [
    img(f"img/Home/H_lay_down1.png").convert(),
    img(f"img/Home/H_lay_down2.png").convert(),
    img(f"img/Home/H_lay_down3.png").convert(),
    img(f"img/Home/H_lay_down4.png").convert(),
    img(f"img/Home/H_lay_down5.png").convert(),
    img(f"img/Home/H_lay_down6.png").convert()
]


H_look_around_cutsceen = [
    ("frame",(1,"You look around","-","-",1000)),
    ("frame",(2,"You find something","-","-",1000)),
    ("frame",(3,"Its a letter","-","-",1000)),
    ("frame",(4,"-","-","-",1000)),
]

H_look_around_img = [
    img(f"img/Home/H_look_around_letter1.png").convert(),
    img(f"img/Home/H_look_around_letter2.png").convert(),
    img(f"img/Home/H_look_around_letter3.png").convert(),
    img(f"img/Home/H_letter.png").convert()
]