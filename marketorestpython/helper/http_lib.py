import requests
import json
import time
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

class HttpLib:
    max_retries = 3
    sleep_duration = 3

    def get(self, endpoint, args = None, mode=None):
        retries = 0
        while True:
            if retries > self.max_retries:
                return None
            try:
                url = endpoint
                if args:
                    r = requests.get(url, params=args)
                else:
                    r = requests.get(url)
                if mode is 'nojson':
                    return r
                else:
                    return r.json()
            except Exception as e:
                print("HTTP Get Exception!!! Retrying.....")
                time.sleep(self.sleep_duration)
                retries += 1


    def post(self, endpoint, args, data=None, files=None, mode=None):
        retries = 0
        while True:
            if retries > self.max_retries:
                return None
            try:
                url = endpoint + "?" + urlencode(args)
                headers = {'Content-type': 'application/json'}
                if mode is 'nojsondumps':
                    r = requests.post(url, data=data)
                elif data is None and files is None:
                    r = requests.post(url, headers=headers)
                elif data is not None and files is None:
                    r = requests.post(url, data=json.dumps(data), headers=headers)
                elif data is None and files is not None:
                    # removed the headers with JSON content type, because the file is not JSON
                    # in future try to infer the correct content type based on file extension
                    with open(files,'rb') as f:
                        files = {'file': f}
                        r = requests.post(url, files=files)
                else:
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
                url = endpoint + "?" + urlencode(args)
                headers = {'Content-type': 'application/json'}
                r = requests.delete(url, data=json.dumps(data), headers=headers)
                return r.json()
            except Exception as e:
                print("HTTP Delete Exception!!! Retrying....."+ str(e))
                time.sleep(self.sleep_duration)
                retries += 1
