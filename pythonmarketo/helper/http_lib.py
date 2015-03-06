import requests
import urllib
import json
import time

class HttpLib:
    max_retries = 3
    sleep_duration = 3


    def get(self, endpoint, args = None):
        retries = 0
        while True:
            if retries > self.max_retries:
                return None 
            try:
                url = endpoint
                if args: 
                    url = endpoint + "?" + urllib.urlencode(args)
                r = requests.get(url)
                return r.json()
            except Exception as e:
                print("HTTP Get Exception!!! Retrying.....")
                time.sleep(self.sleep_duration)
                retries += 1

        
    def post(self, endpoint, args, data):
        retries = 0
        while True:
            if retries > self.max_retries:
                return None 
            try:
                url = endpoint + "?" + urllib.urlencode(args)
                headers = {'Content-type': 'application/json'}
                r = requests.post(url, data=json.dumps(data), headers=headers)
                return r.json()
            except Exception as e:
                print("HTTP Post Exception!!! Retrying.....")
                time.sleep(self.sleep_duration)
                retries += 1
