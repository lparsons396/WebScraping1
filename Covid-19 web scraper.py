from tkinter import END
import requests
import json
import pyttsx3 
import re
import speech_recognition as sr


API_KEY = "tJjdb7RxUssq"
PROJECT_TOKEN = "t1KeXM30a9XJ"
RUN_TOKEN = "tAUGyegVOHOi"

class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key": self.api_key
        }
        self.get_data()

    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data', params={"api_key": API_KEY})
        self.data = json.loads(response.text)

    def get_total_cases(self):
        data = self.data['total']

        for content in data:
            if content['name'] == "Coronavirus Cases:":
                return content['value']

    def get_total_deaths(self):
        data = self.data['total']

        for content in data:
            if content['name'] == "Deaths:":
                return content['value']
    

    def get_country(self, country):
        data = self.data["country"]

        for content in data:
            if content['name'].lower() == country.lower(): #this means we don't care about capitalisation
                return content

data = Data(API_KEY, PROJECT_TOKEN)
print(data.get_country("UK"))



def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio) #this processes our speech as text, it doens't always work perfecly, hence try except

        except Exception as e:
            print("Exception:", str(e))

    return said.lower()

def main():
    print("Starting Program")

    END_PHRASE = "stop" #if we hear stop, it'll end program - see below

    while True:
        print("Listening...")
        text = get_audio()

        if text.find(END_PHRASE): #stop loop
            break