# Import libraries
from numpy import linspace
import RPi.GPIO as GPIO
import time
import math


# Set GPIO numbering mode
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)



VERTICAL_PIN = 40
HORIZONTAL_PIN =36 
LASER_PIN = 18
FOOD_PIN = 11
BUZZER_PIN = 7

    
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
        iters = 8
        for i in range(iters):
            self.change_frequency(frequencies[i % 2])
            self.on()
            time.sleep(2 * self.duration/iters)
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
        self.horizontal.start(0)
        time.sleep(0.5)
     
        self.sett((0,0),0.5)
        self.rest()
        print("done init")

    
    @staticmethod
    def angleToDuty(angle):
        return 7.5-(float(angle)/18.0)

    """
    makes the servos rest at the current angle, might prevent jitter.
    will cause problems only if to much torque is applied on the servo.
    """
    def rest(self):
        self.vertical.ChangeDutyCycle(0)
        self.horizontal.ChangeDutyCycle(0)

    def sett(self, point, delay = 0.03):
        
        vertical_angle, horizontal_angle = point
        v_duty = self.angleToDuty(vertical_angle)
        h_duty = self.angleToDuty(horizontal_angle)
        

        self.horizontal.ChangeDutyCycle(h_duty)
        time.sleep(delay)
        self.horizontal.ChangeDutyCycle(0)
            
        self.vertical.ChangeDutyCycle(v_duty)
        time.sleep(delay)
        self.vertical.ChangeDutyCycle(0)
        
        self.v = vertical_angle
        self.h = horizontal_angle
    
        
    def move(self, point):
        vertical_angle, horizontal_angle = point
        vertical_angle = int(vertical_angle)
        horizontal_angle = int(horizontal_angle)
        self.v = int(self.v)
        self.h = int(self.h)
        dv = self.v - vertical_angle
        dh = self.h - horizontal_angle
        
        if abs(dv) < abs(dh):
            if dh > 0:
                step = -1
            else:
                step = 1
            v_vals = linspace(self.v, vertical_angle, abs(dh))
            h_vals = list(range(self.h, horizontal_angle,step))
            
            for v, h in zip(linspace(self.v, vertical_angle, abs(dh)),list(range(self.h, horizontal_angle,step))):
                self.sett((v,h))
        else:          
            if dv > 0:
                step = -1
            else:
                step = 1

            for v, h in zip(list(range(self.v, vertical_angle, step)),linspace(self.h, horizontal_angle, abs(dv))):
                self.sett((v,h))
                
            
            
        
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
        self.servo.start(0)
        # Start PWM running on servo, value of 0 (pulse off)
        
        
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
        
