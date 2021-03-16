import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from time import sleep
import threading
import asyncio

DEVICE_NAME = 'prototype'
MAX_ITERATIONS = 10


# Use a service account
cred = credentials.Certificate('firestore-sdk.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
doc_ref = db.collection('users').document(DEVICE_NAME)




def wait_for_message():
    while True:
        sleep(1)
        ref = db.collection('users').document(DEVICE_NAME)
        data = ref.get().to_dict()
        if data['device_unread']:
            data['device_unread'] = False
            ref.set(data)
            return {'message_type': data['message_to_device_type'],
                    'message': data['message_to_device']}


def send_message(message_type, message):
    for i in range(MAX_ITERATIONS):
        data = doc_ref.get().to_dict()
        if not data['app_unread']:
            data['app_unread'] = True
            data['message_to_app_type'] = message_type
            data['message_to_app'] = message
            doc_ref.set(data)
            return
        sleep(10)
    print("send_message failed. timed out")

