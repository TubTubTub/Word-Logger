import json
import requests
import os
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
                response = requests.get(f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{entry}?key=eb9c4d01-f573-4294-8f0a-b96eb7765b6f')
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