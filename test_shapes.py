from Shapes import Square, Star

points = [(70, 120), (70, 80), (100, 120), (100, 80)]

print("creating first squrare")
program = Square(points)
print("running first square")
program.run()
print("program 1 sucssesful, running again")
program.run()
print("second run sucsessful, creatin new instance")

program2 = Square(points)
print("running second square")
program2.run()
print("program 2 sucssesful")
