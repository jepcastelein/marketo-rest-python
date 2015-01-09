python_marketo
==============

Python interface to marketo REST api <br />
Detailed Doc - http://developers.marketo.com/documentation/rest/

Installation
============

pip install pythonmarketo

Usage
=====
```python
from pythonmarketo.client import MarketoClient
mc = MarketoClient(host = <Host>, 
                   client_id = <Client_Id>, 
                   client_secret = <Client_Secret>)
```
Get Leads
---------
```python
mc.execute(method = 'get_leads', filtr = 'email', values = 'test@test.com', fields=['email','firstName','lastName','company','postalCode'])
#value could be either "v1 v2 v3" or [v1,v2,v3]
```

Get Leads from listId
---------------------
```python
mc.execute(method = 'get_leads_by_listId', listId = '676', fields=['email','firstName','lastName','company','postalCode']))
```

Get Activity Types
------------------
```python
mc.execute(method = 'get_activity_types')
```

Get PagingToken
----------------
```python
mc.execute(method = 'get_paging_token', sinceDatetime = '2014-10-06')
#sinceDatetime format: 
#2014-10-06T13:22:17-08:00
#2014-10-06T13:22-07:00
#2014-10-06
```

Get Lead Activity
----------------
```python
mc.execute(method = 'get_lead_activity', activityTypeIds = ['23','22'], sinceDatetime = '2014-10-06', batchSize = None, listId = None)
#activityTypeIds could be either "v1 v2 v3" or [v1,v2,v3]
```

Create Lead
------------
```python
mc.execute(method = 'create_lead', lookupField = 'email', lookupValue = 'test@test.com', values = {'firstName':'Test1', 'lastName':'Test2'})
```

Update Lead
------------
```python
mc.execute(method = 'update_lead', lookupField = 'email', lookupValue = 'test@test.com', values = {'firstName':'Test1', 'lastName':'Test2'})
```


TODO
====
Remaining API
