from pythonmarketo.client import MarketoClient

mc = MarketoClient(host = <Host>, 
                   client_id = <Client_Id>, 
                   client_secret = <Client_Secret>)

mc.update_lead(lookupField='email', lookupValue='test@test.com', values={'firstName':'Test1','lastName':'Test2'})
print(mc.get_leads(filtr='email', values='test@test.com'))