# Import libraries
import RPi.GPIO as GPIO
import time

# Set GPIO numbering mode
GPIO.setmode(GPIO.BOARD)

VERTICAL_PIN = 11
HORIZONTAL_PIN = 12



class Angles:
    _instance = None

    @classmethod
    def instance(cls):
        if Angles._instance is None:
            Angles._instance = Angles()
        return Angles._instance

    def __init__(self):
        # Set pins 11 & 12 as outputs, and define as PWM servo1 & servo2
        GPIO.setup(VERTICAL_PIN, GPIO.OUT)
        self.vertical = GPIO.PWM(VERTICAL_PIN, 50)
        GPIO.setup(HORIZONTAL_PIN, GPIO.OUT)
        self.horizontal = GPIO.PWM(HORIZONTAL_PIN, 50)
        # Start PWM running on both servos, value of 0 (pulse off)
        self.vertical.start(0)
        self.horizontal.start(0) #TODO check what 0 means, mybe the next 3 lines are redundent
        self.vertical.ChangeDutyCycle(2)
        self.horizontal.ChangeDutyCycle(2)
        self.rest()
        self.v = 0
        self.h = 0

    def __del__(self):
        # Clean things up at the end
        self.vertical.stop()
        self.horizontal.stop()
        GPIO.cleanup() # TODO: it could cause problems, maybe this should be called only in the end of everything
        print("servos shutdown sucsessfuly")


    """
    makes the servos rest at the current angle, might prevent jitter.
    will cause problems only if to much torque is applied on the servo.
    """
    def rest(self):
        self.vertical.ChangeDutyCycle(0)
        self.horizontal.ChangeDutyCycle(0)

    def set(self, point):
        vertical_angle, horizontal_angle = point
        self.vertical.ChangeDutyCycle(2 + vertical_angle/180)
        self.horizontal.ChangeDutyCycle(2 + horizontal_angle/180)
        self.v = vertical_angle
        self.h = horizontal_angle

    def move(self, point, travel_time=0.5, resolution=10, smooth=True):
        vertical_angle, horizontal_angle = point
        dv = (vertical_angle - self.v)/resolution
        dh = (horizontal_angle - self.h)/resolution
        dt = travel_time/resolution  # delay between individual moves
        for i in range(resolution):
            self.set((self.v + dv, self.h + dh))
            if smooth:  #TODO check tolorances and ratios that prevents jitter. if needed.
                time.sleep(dt/2)
                self.rest()
                time.sleep(dt/2)
            else:
                time.sleep(dt)
