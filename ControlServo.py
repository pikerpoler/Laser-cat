# Import libraries
from numpy import linspace
import RPi.GPIO as GPIO
import time


# Set GPIO numbering mode
GPIO.setmode(GPIO.BOARD)

VERTICAL_PIN = 11
HORIZONTAL_PIN = 12
LASER_PIN = 18
FOOD_PIN = 15
BUZZER_PIN = 16

class Laser:
    _instance = None
    
    @classmethod
    def instance(cls):
        if Laser._instance is None:
            Laser._instance = Laser()
        return Laser._instance

    def __init__(self):
        GPIO.setup(LASER_PIN, GPIO.OUT)
        GPIO.output(LASER_PIN, False)
    def __del__(self):
        GPIO.output(LASER_PIN, False)
    def on(self):
        GPIO.output(LASER_PIN, True)
    def off(self):
        GPIO.output(LASER_PIN, False)

class Buzzer:
    _instance = None
    
    @classmethod
    def instance(cls):
        if Buzzer._instance is None:
            Buzzer._instance = Buzzer()
        return Buzzer._instance

    def __init__(self):
        self.frequency = 500 # in hertz
        self.duration = 1 # in seconds
        GPIO.setup(BUZZER_PIN, GPIO.OUT)
        self.pwm = GPIO.PWM(BUZZER_PIN, self.frequency)
        
    def __del__(self):
        self.pwm.stop()
        
    def on(self):
        self.pwm.start(50)
        
    def off(self):
        self.pwm.stop()
        
    def buzz(self):
        self.on()
        time.sleep(self.duration)
        self.off()
        
    def change_frequency(self,new_requency):
        self.pwm.ChangeFrequency(new_requency)
        
    def alarm(self):
        orig_frequency = self.frequency
        frequencies = [500 , 2000]
        iters = 10
        for i in range(iters):
            self.change_frequency(frequencies[i % 2])
            self.on()
            time.sleep(self.duration/iters)
            self.off()
        self.change_frequency(orig_frequency) 
            
    def raise_and_fall(self):
        orig_frequency = self.frequency
        for frequency in range(50, 5000, 50):
            self.change_frequency(frequency)
            self.on()
            time.sleep(self.duration / 10)
        
        self.off()    
        self.change_frequency(orig_frequency)

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
        self.set((0,0))
        time.sleep(0.5)
        self.rest()
        self.v = 0
        self.h = 0

    
    def __del__(self):
        # Clean things up at the end
        self.move((0,0))
        time.sleep(0.5)
        self.vertical.stop()
        self.horizontal.stop()
        GPIO.cleanup() # TODO: it could cause problems, maybe this should be called only in the end of everything
        print("servos shutdown sucsessful (GPIO cleaned)")


    """
    makes the servos rest at the current angle, might prevent jitter.
    will cause problems only if to much torque is applied on the servo.
    """
    def rest(self):
        self.vertical.ChangeDutyCycle(0)
        self.horizontal.ChangeDutyCycle(0)

    def set(self, point):
        vertical_angle, horizontal_angle = point
        v_duty = 7 - vertical_angle/18
        h_duty = 7 - horizontal_angle/18
        
        #print(v_duty, h_duty)
        self.vertical.ChangeDutyCycle(v_duty)
        self.horizontal.ChangeDutyCycle(h_duty)
        self.v = vertical_angle
        self.h = horizontal_angle

        
    def move(self, point, delay=0.03, resolution=10):
        #print("moving to ", point)
        vertical_angle, horizontal_angle = point
        for v, h in zip (linspace(self.v, vertical_angle, resolution),
                                   linspace(self.h, horizontal_angle, resolution)):
            #print("v,h = ", v,h)
            self.set((v,h))
            time.sleep(delay)
        self.rest()
            
    def calibrate(self):
        while True:
            print(1)
            self.move((-20,20))
            time.sleep(2)
            print(2)
            self.move((20,20))
            time.sleep(2)
            print(3)
            self.move((-20,20))
            time.sleep(2)
            print(4)
            self.move((-20,-20))
            time.sleep(2)
            
        
class Food:
    _instance = None
    
    @classmethod
    def instance(cls):
        if Food._instance is None:
            Food._instance = Food()
        return Food._instance

    def __init__(self):
        GPIO.setup(FOOD_PIN, GPIO.OUT)
        self.servo = GPIO.PWM(FOOD_PIN, 50)
        # Start PWM running on servo, value of 0 (pulse off)
        self.servo.start(0)
        
    def give(self, angle = 180):

        self.servo.ChangeDutyCycle(2+ angle/18)
        time.sleep(1)
        
        self.servo.ChangeDutyCycle(2)
        time.sleep(2)
        
        self.servo.ChangeDutyCycle(2+ angle/18)
        time.sleep(1)        
        
        self.servo.ChangeDutyCycle(0)

    def flip(self):
        self.servo.ChangeDutyCycle(2)
        time.sleep(2)        
        
        self.servo.ChangeDutyCycle(0)
        
