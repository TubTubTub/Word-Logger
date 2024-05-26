import json
import requests
import os
from dotenv import find_dotenv, load_dotenv

env_path = find_dotenv()
load_dotenv(env_path)
API_KEY = os.getenv("API_KEY")
basedir = os.path.dirname(__file__)

class Dict():
    def __init__(self):
        pass
    
    def get_definition(self, entry):
        if entry == 'quit':
            self.process_entries()
            print('Manual exit detected!')
            raise SystemExit
        else:
            try:
                response = requests.get(f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{entry}?key={API_KEY}')
            except Exception as e:
                print('Request failed!', e)
            
            response = response.json()

            if (response == []) or (type(response[0]) != dict):
                return None
            else:
                entry = ''.join(filter(str.isalpha, entry))
                return response[0]['shortdef']

    def process_entries(self, data):
        filename = os.path.join(basedir, 'data.json')
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4, default=str)