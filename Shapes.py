import random
import time
from ControlServo import Angles
import math

angles = Angles.instance()

class Square:
    def __init__(self, angles: list[tuple[float]]):
        self.points = angles

    def run(self, duration=10, travel_time=0.5, delay=0.5):
        start = time.time()
        while time.time() - start < duration:
            new_point = self.points[random.randrange(len(self.points))]
            angles.move(new_point, travel_time)
            time.sleep(delay)


class Star:
    def __init__(self, center: tuple[float], edges: list[tuple[float]]):
        self.center = center
        self.edges = edges

    def run(self, duration=10, travel_time=0.5, delay=0.5):
        start = time.time()
        while time.time() - start < duration:
            angles.move(self.center, travel_time)
            time.sleep(delay)
            new_point = self.edges[random.randrange(len(self.edges))]
            angles.move(new_point, travel_time)
            time.sleep(delay)

class Circle:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def run(self, duration=10, resolution=180):
        start = time.time()
        theta = 0
        dtheta= 2*math.pi/resolution
        while time.time() - start < duration:
            next = self.center + (self.radius * math.cos(theta), self.radius * math.sin(theta))
            theta += dtheta
            angles.move(next)
    pass


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


    pass