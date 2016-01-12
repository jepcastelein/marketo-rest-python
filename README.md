Marketo REST Python
===================

Python Client for the Marketo REST API. It covers all of the basic REST API for Lead, List, Activity and Campaign 
Objects. It also includes some Email, Folder and File APIs. It does not yet cover Custom Objects, Opportunity, 
Company and Sales Person Objects. This is a fork of the project started by Arunim Samat at 
https://github.com/asamat/python_marketo, which had stalled. <br />

Full Marketo REST API documentation - http://developers.marketo.com/documentation/rest/

Installation
============

pip install marketorestpython

Usage
=====
```python
from marketorestpython.client import MarketoClient
munchkin_id = "" # fill in Munchkin ID, typical format 000-AAA-000
mc = MarketoClient(munchkin_id, 
                   client_id="", 
                   client_secret="") # enter Client ID and Secret from Admin > LaunchPoint > View Details 
```


Lead, List, Activity and Campaign Objects
=========================================

Get Lead by Id
--------------
API Ref: http://developers.marketo.com/documentation/rest/get-lead-by-id/
```python
lead = mc.execute(method='get_lead_by_id', id=3482141, fields=['firstName', 'middleName', 'lastName', 'department'])
```

Get Multiple Leads by Filter Type
---------------------------------
API Ref: http://developers.marketo.com/documentation/rest/get-multiple-leads-by-filter-type/
```python
lead = mc.execute(method='get_multiple_leads_by_filter_type', filterType='email', filterValues=['a@b.com','c@d.com'], 
                  fields=['firstName', 'middleName', 'lastName'], batchSize=None)

# fields and batchSize are optional
# max 100 filterValues
# max 1000 results, otherwise you'll get error 1003 ('Too many results match the filter')
```

Get Multiple Leads by List Id
-----------------------------
API Ref: http://developers.marketo.com/documentation/rest/get-multiple-leads-by-list-id/
```python
mc.execute(method='get_multiple_leads_by_list_id', listId='676', 
                fields=['email','firstName','lastName','company','postalCode'], batchSize=None)

# fields and batchSize are optional
# static lists only (does not work with smart lists)
```

Get Multiple Leads by Program Id
--------------------------------
API Ref: http://developers.marketo.com/documentation/rest/get-multiple-leads-by-program-id/
```python
mc.execute(method='get_multiple_leads_by_program_id', programId='1014', 
                fields=['email','firstName','lastName','company','postalCode'], batchSize=None)

# fields and batchSize are optional
```

Create/Update Leads
-------------------
API Ref: http://developers.marketo.com/documentation/rest/createupdate-leads/
```python
leads = [{"email":"joe@example.com","firstName":"Joe"},{"email":"jill@example.com","firstName":"Jill"}]
lead = mc.execute(method='create_update_leads', leads=leads, action='createOnly', lookupField='email', 
                asyncProcessing='false', partitionName='Default')

# action, lookupField and asyncProcessing are optional (defaults are 'email' and 'false')
# action can be "createOrUpdate" (default if omitted), "createOnly", "updateOnly" or "createDuplicate"
# partitionName is required if Marketo instance has more than 1 Lead Partition
# max batch size is 300
```

Associate Lead
--------------
API Ref: http://developers.marketo.com/documentation/rest/associate-lead/
```python
lead = mc.execute(method='associate_lead', id=2234, cookie='id:287-GTJ-838%26token:_mch-marketo.com-1396310362214-46169')
```

Merge Lead
----------
API Ref: http://developers.marketo.com/documentation/rest/merge-lead/
```python
lead = mc.execute(method='merge_lead', id=3482183, leadIds=[3482182], mergeInCRM=False)

# mergeInCRM is optional (default is False)
# returns True if successful
```

Get Lead Partitions
-------------------
API Ref: http://developers.marketo.com/documentation/rest/get-lead-partitions/
```python
lead = mc.execute(method='get_lead_partitions')
```

Get List by Id
--------------
API Ref: http://developers.marketo.com/documentation/rest/get-list-by-id/
```python
lead = mc.execute(method='get_list_by_id', id=724)
```

Get Multiple Lists
------------------
API Ref: http://developers.marketo.com/documentation/rest/get-multiple-lists/
```python
lead = mc.execute(method='get_multiple_lists', id=[724,725], name=None, programName=None, workspaceName=None, batchSize=300)

# all parameters are optional; no parameters returns all lists
```

Add Leads to List
-----------------
API Ref: http://developers.marketo.com/documentation/rest/add-leads-to-list/ 
```python
lead = mc.execute(method='add_leads_to_list', listId=1, id=[1,2,3])

# max batch size is 300
```

Remove Leads from List
----------------------
API Ref: http://developers.marketo.com/documentation/rest/remove-leads-from-list/
```python
lead = mc.execute(method='remove_leads_from_list', listId=1, id=[1,2,3])

# max batch size is 300
```

Member of List
--------------
API Ref: http://developers.marketo.com/documentation/rest/member-of-list/
```python
lead = mc.execute(method='member_of_list', listId=728, id=[3482093,3482095,3482096])
```

Get Campaign by Id
------------------
API Ref: http://developers.marketo.com/documentation/rest/get-campaign-by-id/
```python
lead = mc.execute(method='get_campaign_by_id', id=1170)
```

Get Multiple Campaigns
----------------------
API Ref: http://developers.marketo.com/documentation/rest/get-multiple-campaigns/
```python
lead = mc.execute(method='get_multiple_campaigns', id=[1170,1262], name=None, programName=None, workspaceName=None, batchSize=None)

# all parameters are optional
```

Schedule Campaign
-----------------
API Ref: http://developers.marketo.com/documentation/rest/schedule-campaign/
```python
# date format: 2015-11-08T15:43:12-08:00
from datetime import datetime, timezone, timedelta
now = datetime.now(timezone.utc)
now_no_ms = now.replace(microsecond=0)
now_plus_7 = now_no_ms + timedelta(minutes = 7)
time_as_txt = now_plus_7.astimezone().isoformat()
print(time_as_txt)
lead = mc.execute(method='schedule_campaign', id=1878, runAt=time_as_txt, tokens={'my.Campaign Name': 'new token value'}, cloneToProgramName=None)

# runAt is optional; default is 5 minutes from now; if specified, it needs to be at least 5 minutes from now
# tokens and cloneToProgramName are optional
# returns True
```

Request Campaign
----------------
API Ref: http://developers.marketo.com/documentation/rest/request-campaign/
```python
lead = mc.execute(method='request_campaign', id=1880, leads=[46,38], tokens={'my.increment': '+2'})

# tokens is optional
# returns True
```

Import Lead
-----------
API Ref: http://developers.marketo.com/documentation/rest/import-lead/
```python
lead = mc.execute(method='import_lead', file='../folder/test.csv', format='csv', lookupField='email', listId=None, partitionName='Default')

# lookupField and listId are optional. Email is the default for lookupField.
# partitionName is required when the Marketo instance has more than 1 Lead Partition
```

Get Import Lead Status
----------------------
API Ref: http://developers.marketo.com/documentation/rest/get-import-lead-status/
```python
lead = mc.execute(method='get_import_lead_status', id=900)

# specify the batchId that is returned in 'Import Lead'
```

Get Import Failure File
-----------------------
API Ref: http://developers.marketo.com/documentation/rest/get-import-failure-file/
```python
batch_id = 899
failed_leads = mc.execute(method='get_import_failure_file', id=batch_id)
file_name = "import-failure-for-batch-" + str(batch_id) + ".csv"
if failed_leads is not '':
    f = open(file_name, encoding='utf-8', mode='w')
    f.write(failed_leads)
    f.close()

# specify the batchId that is returned in 'Import Lead'
```

Get Import Warning File
-----------------------
API Ref: http://developers.marketo.com/documentation/rest/get-import-warning-file/
```python
batch_id = 899
warning_leads = mc.execute(method='get_import_warning_file', id=batch_id)
file_name = "import-warning-for-batch-" + str(batch_id) + ".csv"
if warning_leads is not '':
    f = open(file_name, encoding='utf-8', mode='w')
    f.write(warning_leads)
    f.close()

# specify the batchId that is returned in 'Import Lead'
```

Describe
--------
API Ref: http://developers.marketo.com/documentation/rest/describe/
```python
lead = mc.execute(method='describe')
```

Get Activity Types
------------------
API Ref: http://developers.marketo.com/documentation/rest/get-activity-types/
```python
mc.execute(method = 'get_activity_types')
```

Get Paging Token
----------------
API Ref: http://developers.marketo.com/documentation/rest/get-paging-token/
```python
mc.execute(method='get_paging_token', sinceDatetime='2014-10-06')

# sinceDatetime format: 2015-10-06T13:22:17-08:00 or 2015-10-06T13:22-0700 or 2015-10-06
# This call is optional, you can directly pass in the datetime into 'Get Lead Activity' and 'Get Lead Changes'
# Returns the paging token
```

Get Lead Activities
-------------------
API Ref: http://developers.marketo.com/documentation/rest/get-lead-activities/
```python
mc.execute(method='get_lead_activities', activityTypeIds=['23','22'], nextPageToken=None, sinceDatetime='2015-10-06', batchSize=None, listId=None)

# sinceDatetime format: 2015-10-06T13:22:17-08:00 or 2015-10-06T13:22-0700 or 2015-10-06
# either nextPageToken or sinceDatetime need to be specified
# batchSize and listId are optional
# this will potentially return a lot of records: the function loops until it has all activities, then returns them
```

Get Lead Changes
----------------
API Ref: http://developers.marketo.com/documentation/rest/get-lead-changes/
```python
lead = mc.execute(method='get_lead_changes', fields=['firstName','lastName'], nextPageToken=None, sinceDatetime='2015-09-01', batchSize=None, listId=None)

# sinceDatetime format: 2015-10-06T13:22:17-08:00 or 2015-10-06T13:22-0700 or 2015-10-06
# either nextPageToken or sinceDatetime need to be specified
# batchSize and listId are optional
# this will potentially return a lot of records: the function loops until it has all activities, then returns them
```

Get Daily Usage
---------------
API Ref: http://developers.marketo.com/documentation/rest/get-daily-usage/
```python
lead = mc.execute(method='get_daily_usage')
```

Get Last 7 Days Usage
---------------------
API Ref: http://developers.marketo.com/documentation/rest/get-last-7-days-usage/
```python
lead = mc.execute(method='get_last_7_days_usage')
```

Get Daily Errors
----------------
API Ref: http://developers.marketo.com/documentation/rest/get-daily-errors/
```python
lead = mc.execute(method='get_daily_errors')
```

Get Last 7 Days Errors
----------------------
API Ref: http://developers.marketo.com/documentation/rest/get-last-7-days-errors/
```python
lead = mc.execute(method='get_last_7_days_errors')
```

Delete Lead
-----------
API Ref: http://developers.marketo.com/documentation/rest/delete-lead/
```python
lead = mc.execute(method='delete_lead', id=[1,2])

# max batch size is 300
```

Get Deleted Leads
-----------------
API Ref: http://developers.marketo.com/documentation/rest/get-deleted-leads/
```python
lead = mc.execute(method='get_deleted_leads', nextPageToken=None, sinceDatetime=date.today(), batchSize=None)

# sinceDatetime format: 2015-10-06T13:22:17-08:00 or 2015-10-06T13:22-0700 or 2015-10-06
# either nextPageToken or sinceDatetime need to be specified
# batchSize is optional
# will return first and last name, Marketo ID and time of deletion, but no additional Lead attributes
```

Update Leads Partition
----------------------
API Ref: http://developers.marketo.com/documentation/rest/update-leads-partition/
```python
new_partitions = [{'id': 3482156, 'partitionName': 'Default'}, {'id': 3482141, 'partitionName': 'Europe'}]
lead = mc.execute(method='update_leads_partition', input=new_partitions)
```


Asset Objects
=============

Create Folder
-------------
API Ref: http://developers.marketo.com/documentation/asset-api/create-folder/
```python
lead = mc.execute(method='create_folder', name='folder2', parentId=115, parentType="Folder", description='optional')

# parentType is "Folder" or "Program"
# description is optional
```

Get Folder by Id
----------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-folder-by-id/
```python
lead = mc.execute(method='get_folder_by_id', id=3, type='Folder')

# type is 'Folder' or 'Program'; this is required because a Folder and a Program can have the same Id
# will throw KeyError when no folder found
```

Get Folder by Name
------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-folder-by-name/
```python
lead = mc.execute(method='get_folder_by_name', name='test', type='Folder', root=115, workSpace='Europe')

# type, root and workSpace are optional
# will throw KeyError when no folder found
```

Browse Folders
--------------
API Ref: http://developers.marketo.com/documentation/asset-api/browse-folders
```python
lead = mc.execute(method='browse_folders', root=3, maxDepth=5, maxReturn=200, workSpace='Default')

# maxDepth, maxReturn and workSpace are optional
# the folder ID for 'root' is not always the same as the folder ID you see in the UI of the Marketo app
# will throw KeyError when no folder found
```

Create a File
-------------
API Ref: http://developers.marketo.com/documentation/asset-api/create-a-file/
```python
lead = mc.execute(method='create_file', name='Marketo-Logo3.jpg', file='Marketo-Logo.jpg', folder=115, description='test file', insertOnly=False)

# description and insertOnly are optional
# in 'file', specify a path if file is not in the same folder as the Python script
```

List Files
----------
API Ref: http://developers.marketo.com/documentation/asset-api/list-files/
```python
lead = mc.execute(method='list_files', folder=709, offset=0, maxReturn=200)

# offset and maxReturn are optional
```

Custom Objects
==============

Get List of Custom Objects
--------------------------
API Ref: http://developers.marketo.com/documentation/custom-api/get-list-of-custom-objects/
```python
result = mc.execute(method='get_list_of_custom_objects', names=['Order', 'Test'])

# names is optional
```

Describe Custom Object
----------------------
API Ref: http://developers.marketo.com/documentation/custom-api/describe-custom-object/
```python
result = mc.execute(method='describe_custom_object', name='Campaigns')
```

Create/Update Custom Objects
----------------------------
API Ref: http://developers.marketo.com/documentation/custom-api/createupdateupsert-custom-objects/
```python
custom_objects = [{'TK_ID': 'abc123', 'PartNo_1': 'ABC', 'CatalogDescription_1': 'ABC Description'},
                  {'TK_ID': 'abc123', 'PartNo_1': 'DEF', 'CatalogDescription_1': 'DEF Description'}]
result = mc.execute(method='create_update_custom_objects', name='Campaigns', input=custom_objects, action=None, dedupeBy=None)

# action and dedupeBy are optional
```

Delete Custom Objects
---------------------
API Ref: http://developers.marketo.com/documentation/custom-api/delete-custom-objects/
```python
custom_objects = [{'TK_ID': 'abc123', 'PartNo_1': 'ABC'}]
result = mc.execute(method='delete_custom_objects', name='Campaigns', input=custom_objects, deleteBy=None)

# dedupeBy is optional
# in the example above there are 2 dedupe fields
```

Get Custom Objects
------------------
API Ref: http://developers.marketo.com/documentation/custom-api/get-custom-objects/
```python
query = [{'TK_ID': 'abc123', 'ListID': 123}]
result = mc.execute(method='get_custom_objects', input=query, name='Campaigns', filterType='dedupeFields', 
         fields=['TK_ID', 'ListID', 'PartNo_1'], batchSize=None)

query2 = [{'marketoGUID': 'eadc92fb-17ef-4e4d-bb20-73aee1a0d57e'}]
result2 = mc.execute(method='get_custom_objects', input=query2, name='Campaigns', filterType='idField')

query3 = [{'TK_ID': 'abc123'}]
result3 = mc.execute(method='get_custom_objects', input=query3, name='Campaigns', filterType='TK_ID')

# fields and batchSize are optional
# in the first example there are two dedupeFields, which is why the dictionary has two keys; the 'link' field is also
#   searchable, but then 'filterType' needs to be the name of that field. 
```


Company Object
==============

Describe Company
----------------
API Ref: http://developers.marketo.com/documentation/company-api/describe-company/
```python
company = mc.execute(method='describe_company')
```

Create/Update Companies
-----------------------
API Ref: http://developers.marketo.com/documentation/company-api/createupdateupsert-companies/
```python
companies = [{'externalCompanyId': 'C000001', 'company': 'Acme 1', 'website': 'http://www.acme1.com', 
             'numberOfEmployees': 856, 'billingCity': 'San Mateo', 'billingState': 'CA'},
             {'externalCompanyId': 'C000002', 'company': 'Acme 2', 'website': 'http://www.acme2.com', 
             'numberOfEmployees': 114, 'billingCity': 'Redmond', 'billingState': 'WA'}]
company = mc.execute(method='create_update_companies', input=companies, action=None, dedupeBy=None)

# action and dedupeBy are optional
```

Delete Companies
-----------
API Ref: http://developers.marketo.com/documentation/company-api/delete-companies/
```python
companies = [{'externalCompanyId': 'C000003'}]
company = mc.execute(method='delete_companies', input=companies, deleteBy=None)

# deleteBy is optional; values can be dedupeFields (default) or idField
```
OR: 
```python
companies = [{'id': 8}]
company = mc.execute(method='delete_companies', input=companies, deleteBy='idField')
```

Get Companies
-----------
API Ref: http://developers.marketo.com/documentation/company-api/get-companies/

To be implemented. 

TODO
====
* Implement remaining Asset APIs
* Implement Opportunity APIs
* Finish implementing "Get Companies"
* Implement Sales Person APIs


Programming Conventions
=======================
Conventions used for functions: 
* functions mirror as closely as possible how the functions work in the Marketo REST API; exceptions: 
get_lead_activities, get_lead_changes and get_deleted_leads where you can pass in a datetime directly rather 
than having to use get_paging_token (which you can still use, if you want to)
* name of the function is exactly the same as on the Marketo Developer website, but lowercase with spaces replaced by 
underscores
* variables are written exactly the same as in the Marketo REST API, even though they should be lower case according to 
PEP8
* all required variables are checked on whether they're passed in, if not we raise a ValueError
* functions return the 'result' node from the Marketo REST API response; if there is no 'result' node, 'success' is 
returned (which is true/false)
* if the Marketo REST API returns an error, it will raise a Python error with error code and details, which can be 
handled in your code through try/except
* the variable in with the API response is loaded is called 'result' also (so result['result'] is what is returned)
* the client will loop if the number of results is greater than the batch size; it will then return all results 
together; this is not always ideal, because large data sets may take lots of processing time and memory; 
* batchSize is offered as a parameter (if available), but should usually be left blank
* calls that support both GET and POST are implemented as POST to handle more data (for example: long lists of fields)
* folder IDs are split up in Id and Type parameters
* some parameters names shadow build-ins, which is not ideal, but done for consistency with the Marketo API parameters