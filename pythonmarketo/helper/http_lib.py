import requests
import urllib
import urllib2
import json

class HttpLib:

    def get(self, endpoint, args = {}):
        url = endpoint + "?" + urllib.urlencode(args)
        resp = urllib2.urlopen(url)
        if resp.getcode() == 200:
            return json.loads(resp.read())
        return None

    def post(self, endpoint, args, data):
        url = endpoint + "?" + urllib.urlencode(args)
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(data), headers=headers)
        return r.json()
