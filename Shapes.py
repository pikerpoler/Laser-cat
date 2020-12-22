import random
import time
from ControlServo import Angles

angles = Angles.instance()

class Square:
    def __init__(self, points: list[tuple[float]]):
        self.points = points

    def run(self, duration=10, travel_time=0.5, delay=0.5):
        start = time.time()
        while time.time() - start < duration:
            new_point = self.points[random.randrange(len(self.points))]
            angles.move(new_point, travel_time)
            time.sleep(delay)


class Star:
    def __init__(self, center: tuple[float], edges: list[tuple[float]]):
        self.centet = center
        self.edges = edges





class Circle:
    pass


class Trail: #might become infinity
    pass