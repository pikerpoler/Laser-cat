#!/usr/bin/python

from flask import request
from flask_api import FlaskAPI
import RPi.GPIO as GPIO
from Shapes import Square, Star

LEDS = {"green": 16, "red": 18}
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LEDS["green"], GPIO.OUT)
GPIO.setup(LEDS["red"], GPIO.OUT)

app = FlaskAPI(__name__)

@app.route('/', methods=["GET"])
def api_root():
    return {
           "led_url": request.url + "led/(green | red)/",
             "led_url_POST": {"state": "(0 | 1)"}
                 }
  
@app.route('/led/<color>/', methods=["GET", "POST"])
def api_leds_control(color):
    if request.method == "POST":
        if color in LEDS:
            GPIO.output(LEDS[color], int(request.data.get("state")))
    return {color: GPIO.input(LEDS[color])}
    
@app.route('/play/', methods=["GET","POST"])
def api_play(shape):
    if request.method == "POST":
        if shape == "STAR":
            Star().run()
        if shape == "SQUARE":
            Square().run()
    return {"url" : request.url}
		
if __name__ == "__main__":
    app.run()
