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

Get Multiple Leads by Filter Type
---------------------------------
API Ref: http://developers.marketo.com/documentation/rest/get-multiple-leads-by-filter-type/
```python
lead = mc.execute(method='get_multiple_leads_by_filter_type', filterType='email', filterValues=['a@b.com','c@d.com'], 
                  fields=['firstName', 'middleName', 'lastName'], batchSize=None)

# fields and batchSize are optional
# max 100 filterValues
# max 1000 results, otherwise you'll get error 1003 ('Too many results match the filter')
# you can also specify filterValues and fields as a comma-separated string (for example: 'a@b.com,c@d.com')
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

Create/Update Leads
-------------------
API Ref: http://developers.marketo.com/documentation/rest/createupdate-leads/
```python
leads = [{"email":"joe@example.com","firstName":"Joe"},{"email":"jill@example.com","firstName":"Jill"}]
lead = mc.execute(method='create_update_leads', leads=leads, lookupField='email', asyncProcessing='false', partitionName='Default')

# lookupField and asyncProcessing are optional (defaults are 'email' and 'false')
# partitionName is only required if Marketo instance has > 1 Lead Partition
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
lead = mc.execute(method='merge_lead', winning_ld=3482183, loosing_leads_list=[3482182], mergeInCRM=False)

# mergeInCRM is optional
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
lead = mc.execute(method='get_multiple_lists', id=[724,725], name=None, programName=None, workspaceName=None, batchSize=300, nextPageToken=None)

# all parameters are optional
```

Add Leads to List
-----------------
API Ref: http://developers.marketo.com/documentation/rest/add-leads-to-list/ 
```python
lead = mc.execute(method='add_leads_to_list', listId=1, leadIds=[1,2,3])

# can handle 300 Leads at a time
```

Remove Leads from List
----------------------
API Ref: http://developers.marketo.com/documentation/rest/remove-leads-from-list/
```python
lead = mc.execute(method = 'remove_leads_from_list', listId = 1, leadIds = [1,2,3])

# can handle 300 Leads at a time
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
lead = mc.execute(method='get_multiple_campaigns', id=[1170,1262], name=None, programName=None, workspaceName=None, batchSize=None, nextPageToken=None)

# all parameters are optional
# batchSize defaults to the maximum (300)
# while it's theoretically possible to pass in a nextPageToken, the nextPageToken is currently not returned in 'lead'
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
lead = mc.execute(method='schedule_campaign', id=1878, runAt=time_as_txt, tokens={'Campaign Name': 'new token value'}, cloneToProgramName=None)

# runAt is optional; default is 5 minutes from now; if specified, it needs to be at least 5 minutes from now
# tokens and cloneToProgramName are optional
# token override only works for tokens without spaces
# returns True or False
```

Request Campaign
----------------
API Ref: http://developers.marketo.com/documentation/rest/request-campaign/
```python
lead = mc.execute(method='request_campaign', id=1880, leads=[46,38], tokens={'my.increment': '+2'})

# tokens is optional; not tested on tokens with spaces 
```

Import Lead
-----------
API Ref: http://developers.marketo.com/documentation/rest/import-lead/
```python
lead = mc.execute(method='import_lead', file='test.csv', format='csv', lookupField='email', listId=None, partitionName='Default')

# lookupField and listId are optional. Email is the default for lookupField.
# partitionName is required when the Marketo instance has more than 1 Lead Partition
```

Get Import Lead Status
----------------------
API Ref: http://developers.marketo.com/documentation/rest/get-import-lead-status/
```python
lead = mc.execute(method='get_import_lead_status', id=900)

# specify the batch ID that is returned in 'Import Lead'
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

# specify the batch ID that is returned in 'Import Lead'
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

# specify the batch ID that is returned in 'Import Lead'
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

Get PagingToken
----------------
API Ref: http://developers.marketo.com/documentation/rest/get-paging-token/
```python
#sinceDatetime format: 
#2014-10-06T13:22:17-08:00
#2014-10-06T13:22-07:00
#2014-10-06

mc.execute(method='get_paging_token', sinceDatetime='2014-10-06')
```

Get Lead Activity
----------------
API Ref: http://developers.marketo.com/documentation/rest/get-lead-activities/
```python
#activityTypeIds could be either "v1 v2 v3" or [v1,v2,v3]

mc.execute(method = 'get_lead_activity', activityTypeIds = ['23','22'], sinceDatetime = '2014-10-06', batchSize = None, listId = None)
```

Get Lead Changes
----------------
API Ref: http://developers.marketo.com/documentation/rest/get-lead-changes/
```python
lead = mc.execute(method='get_lead_changes', fields='firstName', sinceDatetime='2015-09-01', listId=None)

# sinceDateTime and listId are optional
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

# max number of leads to pass in is 300
```

Get Deleted Leads
-----------------
API Ref: http://developers.marketo.com/documentation/rest/get-deleted-leads/
```python
lead = mc.execute(method='get_deleted_leads', sinceDatetime=date.today(), batchSize=None)

# batchSize is optional; default batchSize is 300
# function will loop to download all deleted leads since the specified time
# will return first and last name, Marketo ID and time of deletion, but no additional Lead attributes
```

Update Leads Partition
----------------------
API Ref: http://developers.marketo.com/documentation/rest/update-leads-partition/
```python
idAndPartitionName = [{'id': 3482156, 'partitionName': 'Default'}, {'id': 3482141, 'partitionName': 'Europe'}]
lead = mc.execute(method='update_leads_partition', idAndPartitionName=idAndPartitionName)
```



Asset Objects
=============

Create Folder
-------------
API Ref: http://developers.marketo.com/documentation/asset-api/create-folder/
```python
lead = mc.execute(method='create_folder', name='pytest2', parent=115, description='optional description')

# description is optional
```

Get Folder by Id
----------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-folder-by-id/
```python
lead = mc.execute(method='get_folder_by_id', id=3, type='Folder')

# type is optional (even though the docs say it's required); type is 'Folder' or 'Program'
# returns False when no folder found
```

Get Folder by Name
------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-folder-by-name/
```python
lead = mc.execute(method='get_folder_by_name', name='pytest', type='Folder', root=115, workSpace='Europe')

# type, root and workSpace are optional
# returns False when no folders found
```

Browse Folders
--------------
API Ref: http://developers.marketo.com/documentation/asset-api/browse-folders
```python
lead = mc.execute(method='browse_folders', root=3, maxDepth=5, maxReturn=200, workSpace='Default')

# maxDepth, maxReturn and workSpace are optional
# the folder ID for 'root' is not always the same as the folder ID you see in the UI of the Marketo app
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


TODO
====
Remaining API


Programming Conventions
=======================
Conventions used for functions: 
* functions mirror as closely as possible how the functions work in the Marketo REST API
* name of the function is exactly the same as on the Marketo Developer website, but lowercase with spaces replaced by 
underscores
* variables are written exactly the same as in the Marketo REST API, even though they should be lower case according to 
PEP8
* all required variables are checked on whether they're passed in, if not we raise a ValueError
* if possible, functions return the 'result' node from the Marketo REST API response
* if the Marketo REST API returns an error, it will raise a Python error with error code and details, which can be 
handled in your code through try/except
* the variable in with the API response is loaded is called 'result' also (so result['result'] is what is returned)
* the client will loop and return all results together; this is not always ideal, because some calls could take up to 
10 seconds for 300 results, so it could take hours or days to get a result and it would not be advisable to load it all
in memory and return it in one giant chunk
* batchSize is offered as a parameter (if available), but should usually be left blank
* calls that support both GET and POST are implemented as POST to handle more data (for example: long lists of fields)
