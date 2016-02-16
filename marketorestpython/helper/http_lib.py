import requests
import time
import mimetypes

class HttpLib:
    max_retries = 3
    sleep_duration = 3

    def get(self, endpoint, args=None, mode=None):
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


    def post(self, endpoint, args, data=None, files=None, filename=None, mode=None):
        retries = 0
        while True:
            if retries > self.max_retries:
                return None
            try:
                headers = {'Content-type': 'application/json'}
                if mode is 'nojsondumps':
                    r = requests.post(endpoint, params=args, data=data)
                elif mode is 'merge_lead':
                    r = requests.post(endpoint, params=args, headers=headers)
                elif data is None and files is None:
                    r = requests.post(endpoint, params=args, headers=headers)
                elif data is not None and files is None:
                    r = requests.post(endpoint, params=args, json=data, headers=headers)
                elif data is None and files is not None:
                    # removed the headers with JSON content type, because the file is not JSON
                    # in future try to infer the correct content type based on file extension (create separate function)
                    if filename is None:
                        # print("I'm in open files with NO custom name")
                        headers = {'Content-type': mimetypes.guess_type(files)[0]}
                        with open(files,'rb') as f:
                            files = {'file': f}
                            r = requests.post(endpoint, params=args, files=files, headers=headers)
                    else:
                        # print("I'm in open files with custom name")
                        with open(files,'rb') as f:
                            files = {filename: f}
                            r = requests.post(endpoint, params=args, files=files)
                else:
                    # removed the headers with JSON content type, because the file is not JSON
                    # print("I'm in 'else'")
                    headers = {'Content-type': mimetypes.guess_type(files)[0]}
                    with open(files,'rb') as f:
                        files = {'file': f}
                        r = requests.post(endpoint, params=args, json=data, files=files, headers=headers)
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
                headers = {'Content-type': 'application/json'}
                r = requests.delete(endpoint, params=args, json=data, headers=headers)
                return r.json()
            except Exception as e:
                print("HTTP Delete Exception!!! Retrying....."+ str(e))
                time.sleep(self.sleep_duration)
                retries += 1
