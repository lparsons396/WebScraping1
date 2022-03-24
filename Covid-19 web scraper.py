from dataclasses import dataclass
from hashlib import new
from tkinter import END
import requests
import json
import pyttsx3 
import re
import speech_recognition as sr
import threading
import time

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
        self.data = self.get_data()

    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data', params={"api_key": API_KEY})
        data = json.loads(response.text)
        return data


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
    

    def get_country_data(self, country):
        data = self.data["country"]

        for content in data:
            if content['name'].lower() == country.lower(): #this means we don't care about capitalisation
                return content


    def get_list_of_countries(self):
        countries = []
        for country in self.data['country']:
            countries.append(country['name'].lower()) #get list of countries, lower case
        return countries

    # we want the covid data to automatically update, rather than us having to start a new run on parsehub again
    def update_data(self):
        response = requests.post(f'https://parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params) #intitated new run on parsehub, akes a few seconds
        #we need to keep checking whether the request is done (last rueady run different than now), set up new thread

        def poll():
            time.sleep(0.1) #allow us to use other thread for 0.1 sec
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    print("Data updated")
                    break 
            time.sleep(5)

        t = threading.Thread(target=poll) #threads useful, can still interact with program while this runs
        t.start()
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

        # lambda is an anonymous function - it allows us to refer to a specific country and then look inside that country's data to get stats required
    COUNTRY_PATTERNS = {
        re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['total_cases'],
        re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths']
    }

    UPDATE_COMMAND = "update"

    while True:
        print("Listening...")
        text = get_audio()
        print(text)
        result = None

        country_list = data.get_list_of_countries()
        

        for pattern, func in COUNTRY_PATTERNS.items():
            if pattern.match(text):
                words = set(text.split(" ")) ## this makes it easier to search through, we don't need to iterate throuhg it, just one pass hence O(1) time not O(n)
                for country in country_list:
                    if country in words:
                        result = func(country)
                        break
                

        for pattern, func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                result = func()
                break
            ## this above says, we have a dictionary made up of pattern:func key value pairs.
            # search through them all and see if they match the text (regex re has a match function)
            # if so, we efine our result as this function, break loop an below we'll call it

        if text == UPDATE_COMMAND:
            result = "Data is being updated. Please wait."
            data.update_data() 


        if result:
            speak(result)

        #if text == UPDATE_COMMAND:
         #   result = "Data is being updated. Please wait."
           # data.update_data() 

        if text.find(END_PHRASE) != -1: #stop loop
            print("Exit")
            break

main()
