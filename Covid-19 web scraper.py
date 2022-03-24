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


    def get_list_of_countries(self):
        countries = []
        for country in self.data['country']:
            countries.append(country['name'].lower()) #get list of countries, lower case
        return countries

#data = Data(API_KEY, PROJECT_TOKEN)
#print(data.get_list_of_countries())



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
            said = r.recognize_google(audio) #this processes our speech as text, it doesn't always work perfecly, hence try except

        except Exception as e:
            print("Exception:", str(e))

    return said.lower()

def main():
    print("Starting Program")
    data = Data(API_KEY, PROJECT_TOKEN)
    END_PHRASE = "stop" #if we hear stop, it'll end program - see below


    #recognise differnt things people could say, [\w\s] = any number of words
    TOTAL_PATTERNS = {
        
        re.compile("[\w\s]+ total [\w\s]+ cases"): data.get_total_cases,
        re.compile("[\w\s]+ total cases"): data.get_total_cases,
        re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total deaths"): data.get_total_deaths,

        re.compile("total [\w\s]+ cases"): data.get_total_cases,
        re.compile("total cases"): data.get_total_cases,
        re.compile("total [\w\s]+ deaths"): data.get_total_deaths,
        re.compile("total deaths"): data.get_total_deaths,
    }

    while True:
        print("Listening...")
        text = get_audio()
        print(text)
        result = None

        for pattern, func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                result = func()
                break
            ## this above says, we have a dictionary made up of pattern:func key value pairs.
            # search through them all and see if they match the text (regex re has a match function)
            # if so, we efine our result as this function, break loop an below we'll call it

        if result:
            speak(result)


        if text.find(END_PHRASE) != -1: #stop loop
            print("Exit")
            break

main()
