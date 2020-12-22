from Shapes import Square, Star, Circle, Trail
import time

points = [(70, 120), (70, 70), (120, 120), (120, 120)]
center = (90, 90)

print("running Square")
start_t = time.time()
Square(points).run()
print("Square successful, run took ", time.time() - start_t, " seconds")

print("running Star")
start_t = time.time()
Star(center, points).run()
print("Star run successful, run took ", time.time() - start_t, " seconds")

print("running Circle")
start_t = time.time()
Circle(center, 30).run()
print("Circle successful, run took ", time.time() - start_t, " seconds")

print("running Trail")
start_t = time.time()
Trail().run()
print("Circle successful, run took ", time.time() - start_t, " seconds")
