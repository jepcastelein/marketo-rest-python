python_marketo
==============

Python interface to marketo REST api

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
mc.get_leads(filtr='email', values='test@test.com')
```
Create Lead
------------
```python
mc.create_lead(lookupField='email', lookupValue='test@test.com', values={'firstName':'Test1','lastName':'Test2'})
```
Update Lead
------------
```python
mc.update_lead(lookupField='email', lookupValue='test@test.com', values={'firstName':'Test1','lastName':'Test2'})
```

TODO
====
Remaining API
