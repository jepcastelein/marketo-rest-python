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
mc.get_leads(filtr = 'email', values = 'test@test.com')
```

Get Leads from listId
---------------------
```python
mc.get_leads_by_listId(listId = '676', fields=['email','firstName','lastName','company','postalCode']))
```

Get Activity Types
------------------
```python
mc.get_activity_types()
```

Get PagingToken
----------------
```python
mc.get_paging_token(sinceDatetime = '2014-10-06')
```

Get Lead Activity
----------------
```python
mc.get_lead_activity(activityTypeIds = ['23','22'], sinceDatetime = '2014-10-06', batchSize = None, listId = None)
```

Create Lead
------------
```python
mc.create_lead(lookupField = 'email', lookupValue = 'test@test.com', values = {'firstName':'Test1', 'lastName':'Test2'})
```

Update Lead
------------
```python
mc.update_lead(lookupField = 'email', lookupValue = 'test@test.com', values = {'firstName':'Test1', 'lastName':'Test2'})
```


TODO
====
Remaining API
