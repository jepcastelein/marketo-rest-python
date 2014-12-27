from pythonmarketo.helper  import http_lib 
import json
import time

class MarketoClient:    
    host = None
    client_id = None
    client_secret = None
    token = None
    expires_in = None
    valid_until = None
    token_type = None
    scope = None
    last_request_id = None
    
    def __init__(self, host, client_id, client_secret):
        assert(host is not None)
        assert(client_id is not None)
        assert(client_secret is not None)
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret

    def authenticate(self):
        if self.valid_until is not None and\
            self.valid_until > time.time():
            return

        args = { 
            'grant_type' : 'client_credentials', 
            'client_id' : self.client_id,
            'client_secret' : self.client_secret
        }
        data = http_lib.HttpLib().get("https://" + self.host + "/identity/oauth/token", args)
        if data is None: raise Exception("Empty Response")
        self.token = data['access_token']
        self.token_type = data['token_type']
        self.expires_in = data['expires_in']
        self.valid_until = time.time() + data['expires_in'] 
        self.scope = data['scope']

    def get_leads(self, filtr, values = [], fields = []):
        self.authenticate()
        values = values.split()
        args = {
        'access_token' : self.token,
        'filterType' : str(filtr),
        'filterValues' : (',').join(values)
        }
        if len(fields) > 0:
            args['fields'] = ",".join(fields)
        data = http_lib.HttpLib().get("https://" + self.host + "/rest/v1/leads.json", args)
        if data is None: raise Exception("Empty Response")
        self.last_request_id = data['requestId']
        if not data['success'] : raise Exception(str(data['errors'])) 
        leads = []
        return data['result']
        

    def update_lead(self, lookupField, lookupValue, values):
        updated_lead = dict(list({lookupField : lookupValue}.items()) + list(values.items()))
        data = {
            'action' : 'updateOnly',
            'lookupField' : lookupField,
            'input' : [
             updated_lead
            ]
        }
        self.post(data)

    def create_lead(self, lookupField, lookupValue, values):
        new_lead = dict(list({lookupField : lookupValue}.items()) + list(values.items()))
        data = {
            'action' : 'createOnly',
            'lookupField' : lookupField,
            'input' : [
             new_lead
            ]
        }
        self.post(data)
       
    
    def post(self, data):
          self.authenticate()
          args = {
            'access_token' : self.token 
          }
          data = http_lib.HttpLib().post("https://" + self.host + "/rest/v1/leads.json" , args, data)
          if not data['success'] : raise Exception(str(data['errors']))
          print("Status:", data['result'][0]['status'])
          