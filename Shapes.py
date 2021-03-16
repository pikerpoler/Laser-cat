import random
import time
from ControlServo import Angles, Laser, Food, Buzzer
import math

angles = Angles.instance()
laser = Laser.instance()
food = Food.instance()
buzzer = Buzzer.instance()


buzzer.buzz()

# angles.calibrate()

POINTS = "points"
CENTER = "center"
default = {
    POINTS:[(5, 30), (5, -30), (-12, 40) ,(10, 0), (-10, -40)],
    CENTER: (0, 0)
}

class YumYum:
    def run(self, angle = 180):
        print("running yumyum")
        buzzer.alarm()
        food.give(angle)

class Star:
    def __init__(self, points = default[POINTS]):
        self.points = points
        self.index = 5
    
    def run(self, duration=20, resolution=50):
        laser.on()
        start = time.time()
        
        while True:
            self.index = (self.index + 1) %5
            angles.move(self.points[self.index])
            if time.time() - start > duration:
                        laser.off()
                        return
            
#             for p in self.points:
#                     angles.move(p)
#                     if time.time() - start > duration:
#                         laser.off()
#                         return
                    

class Square:
    def __init__(self, center=default[CENTER], edges=default[POINTS]):
        self.center = center
        self.edges = edges

    def run(self, duration=20,delay=0.6):
        laser.on()
        start = time.time()
        while time.time() - start < duration:
            angles.move(self.center)
            time.sleep(delay/2)
            new_point = self.edges[random.randrange(len(self.edges))]
            angles.move(new_point)
            time.sleep(delay)
        laser.off()

class Circle:
    def __init__(self, center=default[CENTER], radius=10):
        self.center = center
        self.radius = radius

    def run(self, duration=20, resolution=50):
        laser.on()
        start = time.time()
        while True:
            for p in [(self.center[0] + math.cos(2*math.pi/resolution*x)*self.radius,
                       self.center[1] + math.sin(2*math.pi/resolution*x)*self.radius*3) for x in range(0,resolution+1)]:
                    angles.sett(p,0.06)
                    if time.time() - start > duration:
                        laser.off()
                        return
        laser.off()
        

    


class Trail: #might become infinity
    def __init__(self, max_v=130, min_v=50, max_h=130, min_h=50):
        self.max_v = max_v
        self.min_v = min_v
        self.max_h = max_h
        self.min_h = min_h

    def run(self, duration=10, step_size=1):
        start = time.time()
        next = (random.uniform(self.min_v, self.max_v),
                random.uniform(self.min_h, self.max_h))
        velocity = (random.uniform(-5*step_size, 5*step_size),
                    random.uniform(-5*step_size, 5*step_size))
        while time.time() - start < duration:
            dv = (random.uniform(-step_size, step_size),
                    random.uniform(-step_size, step_size))
            velocity = velocity + dv
            next = next + velocity * step_size / math.sqrt(velocity[0]**2 + velocity[1]**2)
            angles.move(next)


    