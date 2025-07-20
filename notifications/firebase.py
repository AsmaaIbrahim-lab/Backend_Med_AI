# notifications/firebase.py

import os
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

# Initialize Firebase 
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIAL_PATH)
    firebase_admin.initialize_app(cred)



# Push Notification Sender
def send_push_notification(token, title, body, data=None):
    message = messaging.Message(
        token=token,
        notification=messaging.Notification(title=title, body=body),
        data=data or {},
    )
    response = messaging.send(message)
    return response