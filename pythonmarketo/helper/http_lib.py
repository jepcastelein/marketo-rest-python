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
                    url = endpoint + "?" + urllib.parse.urlencode(args)
                r = requests.get(url)
                return r.json()
            except Exception as e:
                print("HTTP Get Exception!!! Retrying.....")
                time.sleep(self.sleep_duration)
                retries += 1


    def post(self, endpoint, args, data=None, files=None):
        retries = 0
        while True:
            if retries > self.max_retries:
                return None
            try:
                url = endpoint + "?" + urllib.parse.urlencode(args)
                headers = {'Content-type': 'application/json'}
                if data is None and files is None:
                    #print('only args')
                    r = requests.post(url, headers=headers)
                elif data is not None and files is None:
                    #print('args plus data')
                    r = requests.post(url, data=json.dumps(data), headers=headers)
                elif data is None and files is not None:
                    #print('args plus files')
                    # removed the headers with JSON content type, because the file is not JSON
                    # in future try to infer the correct content type based on file extension (create separate function)
                    with open(files,'rb') as f:
                        files = {'file': f}
                        r = requests.post(url, files=files)
                else:
                    #print('args plus data plus files')
                    # removed the headers with JSON content type, because the file is not JSON
                    with open(files,'rb') as f:
                        files = {'file': f}
                        r = requests.post(url, data=json.dumps(data), files=files)
                return r.json()
            except Exception as e:
                print("HTTP Post Exception!!! Retrying....."+ str(e))
                time.sleep(self.sleep_duration)
                retries += 1

    def delete(self, endpoint, args, data):
        retries = 0
        while True:
            if retries > self.max_retries:
                return None
            try:
                url = endpoint + "?" + urllib.parse.urlencode(args)
                headers = {'Content-type': 'application/json'}
                r = requests.delete(url, data=json.dumps(data), headers=headers)
                return r.json()
            except Exception as e:
                print("HTTP Delete Exception!!! Retrying....."+ str(e))
                time.sleep(self.sleep_duration)
                retries += 1
