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
API Ref: http://developers.marketo.com/documentation/rest/get-multiple-leads-by-filter-type/ 
```python
#values could be either "v1 v2 v3" or [v1,v2,v3]

mc.execute(method = 'get_leads', filtr = 'email', values = 'test@test.com', fields=['email','firstName','lastName','company','postalCode'])
```

Get Leads from listId
---------------------
API Ref: http://developers.marketo.com/documentation/rest/get-multiple-leads-by-list-id/
```python
mc.execute(method = 'get_leads_by_listId', listId = '676', fields=['email','firstName','lastName','company','postalCode']))
```

Get Activity Types
------------------
API Ref: http://developers.marketo.com/documentation/rest/get-activity-types/
```python
mc.execute(method = 'get_activity_types')
```

Get PagingToken
----------------
API Ref: http://developers.marketo.com/documentation/rest/get-paging-token/
```python
#sinceDatetime format: 
#2014-10-06T13:22:17-08:00
#2014-10-06T13:22-07:00
#2014-10-06

mc.execute(method = 'get_paging_token', sinceDatetime = '2014-10-06')
```

Get Lead Activity
----------------
API Ref: http://developers.marketo.com/documentation/rest/get-lead-activities/
```python
#activityTypeIds could be either "v1 v2 v3" or [v1,v2,v3]

mc.execute(method = 'get_lead_activity', activityTypeIds = ['23','22'], sinceDatetime = '2014-10-06', batchSize = None, listId = None)
```

Create Lead
------------
API Ref: http://developers.marketo.com/documentation/rest/createupdate-leads/
```python
mc.execute(method = 'create_lead', lookupField = 'email', lookupValue = 'test@test.com', values = {'firstName':'Test1', 'lastName':'Test2'})
```

Update Lead
------------
API Ref: http://developers.marketo.com/documentation/rest/createupdate-leads/
```python
mc.execute(method = 'update_lead', lookupField = 'email', lookupValue = 'test@test.com', values = {'firstName':'Test1', 'lastName':'Test2'})
```


TODO
====
Remaining API
