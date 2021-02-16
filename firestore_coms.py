import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


DEVICE_NAME = 'prototype'

# Use a service account
cred = credentials.Certificate('firestore-sdk.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

data = {
    u'name': u'Los Angeles',
    u'state': u'CA',
    u'country': u'USA'
}

# Add a new doc in collection 'cities' with ID 'LA'
db.collection(u'devices').document(u'LA').set(data)