import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from time import sleep
import threading
import asyncio

from Shapes import Square, Star, Circle, YumYum
from ControlServo import Buzzer

#from streaming import offer

DEVICE_NAME = 'prototype'
MAX_ITERATIONS = 10

FOOD = "FOOD"
SHAPE = "SHAPE"
OFFER = "OFFER"
ANSWER = "ANSWER"
shapes = {"SQUARE":Square(),
          "STAR": Star(),
          "CIRCLE": Circle(),
          }

# Use a service account
cred = credentials.Certificate('/home/pi/Documents/Laser-cat/firestore-sdk.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
doc_ref = db.collection('users').document(DEVICE_NAME)


f = open("/home/pi/Documents/Laser-cat/ip.txt", "r")
IP = f.read()
f.close()
data = doc_ref.get().to_dict()
data["ip"] = IP
doc_ref.set(data)    

# Create an Event for notifying main thread.


callback_done = threading.Event()


async def message_handler(message_type, message, play_time):
    if message_type == SHAPE:
        shapes[message].run(play_time)
        return
    if message_type == FOOD:
        YumYum().run()
        return
    
#     if message_type == OFFER:
#         print("offering")
#         ans = await offer(message,play_time)
#         print("answer is", ans)
#         send_message(ANSWER, ans)
    
    print("unsupported message")
    print("type: %s" % message_type)
    print("message: %s" % message)

# Create a callback on_snapshot function to capture changes
def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:

        data = doc.to_dict()
        if data['device_unread']:
            data['device_unread'] = False
            doc_ref.set(data)
            asyncio.run(message_handler( data['message_to_device_type'],data['message_to_device'], data['play_time']))
          
        
    callback_done.set()
    


doc_watch = doc_ref.on_snapshot(on_snapshot)




def send_message(message_type, message):
    for i in range(MAX_ITERATIONS):
        data = doc_ref.get().to_dict()
        if not data['app_unread']:
            data['app_unread'] = True
            data['message_to_app_type'] = message_type
            data['message_to_app'] = message
            doc_ref.set(data)        
            return
        sleep(3)
    print("send_message failed. timed out")



while True:
    sleep(1)
    pass


# def wait_for_message():
#     while True:
#         sleep(1)
#         ref = db.collection('users').document(DEVICE_NAME)
#         data = ref.get().to_dict()
#         if data['device_unread']:
#             data['device_unread'] = False
#             ref.set(data)
#             return {'message_type': data['message_to_device_type'],
#                     'message': data['message_to_device']}
#

