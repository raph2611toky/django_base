from dotenv import load_dotenv
from datetime import timedelta
from django.utils import timezone as django_timezone

import os
import requests
import pyttsx3
import json

load_dotenv()

def get_timezone():
    tz = os.getenv("TIMEZONE_HOURS")
    if '-' in tz:
        return django_timezone.now() - timedelta(hours=int(tz.strip()[1:]))
    return django_timezone.now()+timedelta(hours=int(tz))

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    
def helloworld():
    RASA = os.getenv('RASA')
    response = requests.request("GET", RASA)
    return response.text

def messageChatRASA(message, sender="Anonymous", debug=0):
    RASA_API = os.getenv('RASA_URL')
    
    data = {
        "sender": sender,
        "message": str(message)
    }

    headers = {
        'Content-Type': "application/json",
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }

    try:
        response = requests.post(RASA_API, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Unexpected response", "status_code": response.status_code}
    except Exception as e:
        return {"error": "ERROR 1", "details": str(e)}
        