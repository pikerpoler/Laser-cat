
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("/home/pi/Documents/Laser-cat/serviceAccountKey.json")
firebase_admin.initialize_app(cred)


