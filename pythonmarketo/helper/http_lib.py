import requests
import urllib
import json

class HttpLib:

    def get(self, endpoint, args = None):
        url = endpoint
        if args: 
            url = endpoint + "?" + urllib.urlencode(args)
        r = requests.get(url)
        return r.json()
        
    def post(self, endpoint, args, data):
        url = endpoint + "?" + urllib.urlencode(args)
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(data), headers=headers)
        return r.json()
