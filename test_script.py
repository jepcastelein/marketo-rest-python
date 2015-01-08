from pythonmarketo.client import MarketoClient
import json

mc = MarketoClient(host = <Host>, 
                   client_id = <ClientId>, 
                   client_secret = <ClentSecret>)
mc.update_lead(lookupField='email', lookupValue='test@test.com', values={'firstName':'Test1','lastName':'Test2'})
