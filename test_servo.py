from ControlServo import Angles, Laser, Food, Buzzer
from time import sleep

angles = Angles.instance()

#food = Food.instance()
#food.flip() 

POINTS = [(5, 30),(10, 0), (5, -30), (-10, -40), (-12, 40)]
#POINTS = [(8, 0),(0, 20), (-20, 0),(0, -20)]
CENTER = (0,0)

angles.move(CENTER)
angles.sett(CENTER)
sleep(2)

for point in POINTS:
    #angles.move(CENTER)
    
    angles.move(point)
    print(point)
    sleep(2)





