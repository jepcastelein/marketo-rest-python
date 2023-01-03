Marketo REST Python
===================
Python Client that covers most of the Marketo REST API. It handles authentication, error handling and rate limiting
to the standard limit of 100 calls in 20 seconds (defined in http_lib module). This is a fork of the project started by 
Arunim Samat at https://github.com/asamat/python_marketo, which had stalled. <br />

Full Marketo REST API documentation - http://developers.marketo.com/documentation/rest/

Installation
============

`pip install marketorestpython`

Unit tests
==========
[![Build Status](https://travis-ci.org/jepcastelein/marketo-rest-python.svg?branch=master)](https://travis-ci.org/jepcastelein/marketo-rest-python)

See tests in `test_script.py` and see `.travis.yml` for automated
testing setup. Travis does not test pull requests. 

To test locally, create a local file `conf.json` and enter your Marketo credentials and 
type `pytest` on the command line: 
```json
{
  "munchkin_id": "",
  "client_id": "",
  "client_secret": ""
}
```
This runs `test_script.py`. It will automatically create and delete Person records and Assets
in Marketo (self-contained). It is recommended to only run it on a sandbox instance. 

Usage
=====
```python
from marketorestpython.client import MarketoClient
munchkin_id = "" # fill in Munchkin ID, typical format 000-AAA-000
client_id = "" # enter Client ID from Admin > LaunchPoint > View Details
client_secret= "" # enter Client ID and Secret from Admin > LaunchPoint > View Details
api_limit=None
max_retry_time=None
requests_timeout=(3.0, 10.0)
mc = MarketoClient(munchkin_id, client_id, client_secret, api_limit, max_retry_time, requests_timeout=requests_timeout)

# 'api_limit' and 'max_retry_time' are optional;
# 'api_limit' limits the number of Marketo API calls made by this instance of MarketoClient
# 'max_retry_time' defaults to 300 and sets the time in seconds to retry failed API calls that 
#   are retryable; if it still fails after the configured time period, it will throw a 
#   MarketoException
# 'requests_timeout' can be an int, float, or tuple of ints or floats to pass as a timeout 
#   argument to calls made by the requests library. Defaults to None, i.e., no timeout.
#   See requests docs for more info: http://docs.python-requests.org/en/master/user/advanced/
```
Then use mc.execute(method='') to call the various methods (see documentation below) 

For very specific use cases where you only have the access_token, you can also pass that in directly; you are then
responsible for requesting the initial access_token and renewing it when it expires. 
```python
from marketorestpython.client import MarketoClient
munchkin_id = "" # fill in Munchkin ID, typical format 000-AAA-000
access_token = "" # enter access_token
mc = MarketoClient(munchkin_id, access_token=access_token)
```


Lead, List, Activity and Campaign Objects
=========================================

Get Lead by Id
--------------
API Ref: http://developers.marketo.com/documentation/rest/get-lead-by-id/
```python
lead = mc.execute(method='get_lead_by_id', id=3482141, fields=['firstName', 'middleName', 'lastName', 'department'])

# fields is optional
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

Get Multiple Leads by List Id Yield (Generator)
-----------------------------------------------
API Ref: http://developers.marketo.com/documentation/rest/get-multiple-leads-by-list-id/
```python
for leads in mc.execute(method='get_multiple_leads_by_list_id_yield', listId='676', 
                fields=['email','firstName','lastName'], batchSize=None, return_full_result=False):
    print(len(leads))

# OR: 

leads = mc.execute(method='get_multiple_leads_by_list_id_yield', listId='676', 
                fields=['email','firstName','lastName'], batchSize=None, return_full_result=False)
lead_chunk = next(leads) # keep calling next until no more Leads

# this is a generator, so it will return chunks of Leads rather that all Leads on the 
#   List at once; therefore, it's useful for Lists with large numbers of Leads 
# fields and batchSize are optional; batchSize defaults to 300, which is the max
# set return_full_result to True to get the nextPageToken and requestId returned; actual 
#  result will be in the 'result' key
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

Get Multiple Leads by Program Id Yield (Generator)
--------------------------------------------------
API Ref: http://developers.marketo.com/documentation/rest/get-multiple-leads-by-program-id/
```python
for leads in mc.execute(method='get_multiple_leads_by_program_id_yield', programId='1014', 
                fields=['email','firstName','lastName','company','postalCode'], batchSize=None):
    print(len(leads))

# this is a generator, so it will return chunks of Leads rather that all Program Members 
#   at once; therefore, it's useful for Programs with large numbers of Members 
# fields and batchSize are optional
```


Change Lead Program Status
--------------------------
API Ref: http://developers.marketo.com/documentation/rest/change-lead-program-status/
```python
status = mc.execute(method = 'change_lead_program_status', id=1097, leadIds=[51,10,11,24], status="Registered")
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

Push Lead
---------
API Ref: http://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Leads/pushToMarketoUsingPOST
```python
leads = [
    {"email":"lead1@example.com","firstName":"Joe", "cookies":"id:662-XAB-092&token:_mch-castelein.net-1487035251303-23757"},
    {"email":"lead2@example.com","firstName":"Jillian"}
]
lead = mc.execute(method='push_lead', leads=leads, lookupField='email', programName='Big Launch Webinar',
                  programStatus='Registered', source='example source', reason='example reason')

# leads, lookupField and programName are required
# all others are optional
# to associate Cookie ID, put it in a field called 'cookies' (see example above)
# to associate mkt_tok, put it in a field called 'mktToken' (see http://developers.marketo.com/rest-api/lead-database/leads/#push_lead_to_marketo)
```

Submit Form
------------
API docs: https://developers.marketo.com/rest-api/lead-database/leads/#submit_form
```python
input = {
   "leadFormFields":{
      "firstName":"Marge",
      "lastName":"Simpson",
      "email":"marge.simpson@fox.com",
      "pMCFField":"PMCF value"
   },
   "visitorData":{
      "pageURL":"https://na-sjst.marketo.com/lp/063-GJP-217/UnsubscribePage.html",
      "queryString":"Unsubscribed=yes",
      "leadClientIpAddress":"192.150.22.5",
      "userAgentString":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
   },
   "cookie":"id:063-GJP-217&token:_mch-marketo.com-1594662481190-60776"
}
response = mc.execute(method='submit_form', formId=1029, input=input)

# please note that `input` doesn't need to contain a list, the method does that. 
```

Merge Lead
----------
API Ref: http://developers.marketo.com/documentation/rest/merge-lead/
```python
lead = mc.execute(method='merge_lead', id=3482183, leadIds=[3482182], mergeInCRM=False)

# mergeInCRM is optional (default is False)
# returns True if successful
```

Get Smart Campaigns by Lead ID
------------------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Leads/getSmartCampaignMembershipUsingGET
```python
results = mc.execute(method='get_smart_campaigns_by_lead_id', lead_id=39881)
```

Get Lead Partitions
-------------------
API Ref: http://developers.marketo.com/documentation/rest/get-lead-partitions/
```python
lead = mc.execute(method='get_lead_partitions')
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
lead_fields = mc.execute(method='describe')
```

Describe2
--------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Leads/describeUsingGET_6
```python
lead_fields = mc.execute(method='describe2')
```

Describe Program Member
-----------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Program_Members/describeProgramMemberUsingGET2
```python
program_member_fields = mc.execute(method='describe_program_member')
```

Get Activity Types
------------------
API Ref: http://developers.marketo.com/documentation/rest/get-activity-types/
```python
activity_types = mc.execute(method = 'get_activity_types')
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
mc.execute(method='get_lead_activities', activityTypeIds=['23','22'], nextPageToken=None, 
    sinceDatetime='2015-10-06', untilDatetime='2016-04-30', 
    batchSize=None, listId=None, leadIds=[1,2])

# sinceDatetime format: 2015-10-06T13:22:17-08:00 or 2015-10-06T13:22-0700 or 2015-10-06
# either nextPageToken or sinceDatetime need to be specified
# untilDatetime, batchSize, listId and leadIds are optional; batchsize defaults to 300 (max)
# unless you specify untilDatetime, the function loops until it has all activities until right now, 
#  then returns them (which could potentially be a lot of data)
```

Get Lead Activities Yield (Generator)
----------------------------------
API Ref: http://developers.marketo.com/documentation/rest/get-lead-activities/
```python
for activities in mc.execute(method='get_lead_activities_yield', activityTypeIds=['23','22'], nextPageToken=None, 
                             sinceDatetime='2015-10-06', untilDatetime='2016-04-30', 
                             batchSize=None, listId=None, leadIds=[1,2], return_full_result=False,
                             max_empty_more_results=None):
    print(len(activities))

# sinceDatetime format: 2015-10-06T13:22:17-08:00 or 2015-10-06T13:22-0700 or 2015-10-06
# either nextPageToken or sinceDatetime need to be specified
# untilDatetime, batchSize, listId and leadIds are optional; batchsize defaults to 300 (max)
# set return_full_result to get the nextPageToken and requestId returned; actual 
#  result will be in the 'result' key
# sometimes Marketo responds with 0 results but indicates there may be more
#  results in the next call; max_empty_more_results defines how many times "0 results"
#  is acceptable until it gives up
# this is a generator, so it will return chunks of Leads rather that all Activities 
#   at once; therefore, it's useful for retrieving large numbers of Activities
```

Get Lead Changes
----------------
API Ref: http://developers.marketo.com/documentation/rest/get-lead-changes/
```python
lead = mc.execute(method='get_lead_changes', fields=['firstName','lastName'], nextPageToken=None,
                  sinceDatetime='2015-09-01', untilDatetime='2017-01-01', batchSize=None, listId=None)

# sinceDatetime format: 2015-10-06T13:22:17-08:00 or 2015-10-06T13:22-0700 or 2015-10-06
# either nextPageToken or sinceDatetime need to be specified
# untilDatetime, batchSize and listId are optional; batchsize defaults to 300 (max)
# this will potentially return a lot of records: the function loops until it has all activities, then returns them
```

Get Lead Changes Yield (Generator)
----------------------------------
API Ref: http://developers.marketo.com/documentation/rest/get-lead-changes/
```python
for leads in mc.execute(method='get_lead_changes_yield', fields=['firstName','lastName'], nextPageToken=None,
                  sinceDatetime='2015-09-01', untilDatetime='2017-01-01', batchSize=None, listId=None, 
                  leadIds=[1,2], return_full_result=False, max_empty_more_results=None):
    print(len(leads))

# sinceDatetime format: 2015-10-06T13:22:17-08:00 or 2015-10-06T13:22-0700 or 2015-10-06
# either nextPageToken or sinceDatetime need to be specified
# untilDatetime, batchSize, listId and leadIds are optional; batchsize defaults to 300 (max)
# set return_full_result to get the nextPageToken and requestId returned; actual 
#  result will be in the 'result' key
# sometimes Marketo responds with 0 results but indicates there may be more
#  results in the next call; max_empty_more_results defines how many times "0 results"
#  is acceptable until it gives up
```

Add Custom Activities
---------------------
API Ref: http://developers.marketo.com/documentation/rest/add-custom-activities/
```python
custom_activities = [
    {
        "leadId": 46,
        "activityDate": "2016-03-05T09:51:00-08:00",
        "activityTypeId": 100004,
        "primaryAttributeValue":"Blue",
        "attributes":[
            {
                "name": "Attribute 1",
                "value": "First Attribute"
            },
            {
                "name": "Attribute 2",
                "value": "Second Attribute"
            }
        ]
    }
]
result = mc.execute(method = 'add_custom_activities', input=custom_activities)

# Currently, Custom Activities need to be set up by Marketo Technical Support or Consulting Services
# max batch size is 300
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


Folders
=============

Create Folder
-------------
API Ref: http://developers.marketo.com/documentation/asset-api/create-folder/
```python
folder = mc.execute(method='create_folder', name='folder2', parentId=115, parentType="Folder", description='optional')

# parentType is "Folder" or "Program"
# description is optional
```

Get Folder by Id
----------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-folder-by-id/
```python
folder = mc.execute(method='get_folder_by_id', id=3, type='Folder')

# type is 'Folder' or 'Program'; this is required because a Folder and a Program can have the same Id
# will throw KeyError when no folder found
```

Get Folder by Name
------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-folder-by-name/
```python
folder = mc.execute(method='get_folder_by_name', name='test', type='Folder', root=115, workSpace='Europe')

# type, root and workSpace are optional
# will throw KeyError when no folder found
```

Get Folder Contents
-------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-folder-contents/
```python
assets = mc.execute(method='get_folder_contents', id=1205, type='Program', maxReturn=None)

# type is Folder or Program
# maxReturn is optional; default for maxReturn is 20 and max is 200
# function will loop and return all results
```

Update Folder
-------------
API Ref: http://developers.marketo.com/documentation/asset-api/update-folder/
```python
folder = mc.execute(method='update_folder', id=141, name="New Name", description=None, isArchive=None)

# name, description and isArchive are optional
# use the id as returned by 'Browse Folders' or 'Get Folder by Name
# can only be used to update Folders, not Programs
```

Delete Folder
-------------------
API Ref: http://developers.marketo.com/documentation/asset-api/delete-folder-by-id/
```python
folder = mc.execute(method='delete_folder', id=789)

# can only be used to delete Folders, not Programs
```

Browse Folders
--------------
API Ref: http://developers.marketo.com/documentation/asset-api/browse-folders
```python
lead = mc.execute(method='browse_folders', root=3, maxDepth=5, maxReturn=200, workSpace='Default')

# maxDepth, maxReturn and workSpace are optional; default for maxReturn is 20 and max is 200
# use the id as returned by 'Browse Folders' or 'Get Folder by Name
# function will loop and return all results
# will throw KeyError when no folder found
```

Browse Folders (Yield)
--------------
API Ref: http://developers.marketo.com/documentation/asset-api/browse-folders
```python
for folders in mc.execute(method='browse_folders_yield', root=3, maxDepth=5, maxReturn=200, workSpace='Default', 
                          offset=0, return_full_result=False): 
    print(folders)
```

Tokens
=======

Create Token
------------
API Ref: http://developers.marketo.com/documentation/asset-api/create-token-by-folder-id/
```python
token = mc.execute(method='create_token', id="28", folderType="Folder", name="test", value="testing 2", type="text")

# this can also be used to update the value of a token
```

Get Tokens
----------
API Ref: http://developers.marketo.com/documentation/asset-api/get-tokens-by-folder-id/
```python
tokens = mc.execute(method='get_tokens', id="28", folderType="Folder")
```

Delete Tokens
-------------
API Ref: http://developers.marketo.com/documentation/asset-api/delete-tokens-by-folder-id/
```python
tokens = mc.execute(method='delete_tokens', id="28", folderType="Folder", name="test", type="text")
```

Static Lists
=====

Get Static List by Id
--------------
API Ref: http://developers.marketo.com/rest-api/assets/static-lists/#by_id
```python
lead = mc.execute(method='get_list_by_id', id=724)
```

Get Static List by Name
--------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Static_Lists/getStaticListByNameUsingGET
```python
lead = mc.execute(method='get_list_by_name', name='My Test List')
```

Get Multiple Lists (OLD)
------------------
API Ref: http://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Static_Lists/getListsUsingGET
```python
lead = mc.execute(method='get_multiple_lists', id=[724,725], name=None, programName=None, workspaceName=None, batchSize=300)

# NOTE: this call has different options compared to 'browse_lists' below
# all parameters are optional; no parameters returns all lists
```

Get Static Lists
------------------
API Ref: http://developers.marketo.com/rest-api/assets/static-lists/#browse
```python
lead = mc.execute(method='browse_lists', folderId=8, folderType='Folder', offset=None, 
                  maxReturn=None, earliestUpdatedAt=None, latestUpdatedAt=None)

# NOTE: this call has different options compared to 'get_multiple_lists' above
# all parameters are optional; no parameters returns all lists
```

Get Static Lists (Yield)
------------------
API Ref: http://developers.marketo.com/rest-api/assets/static-lists/#browse
```python
for lists in mc.execute(method='browse_lists_yield', folderId=8, folderType='Folder', offset=0, 
               maxReturn=20, earliestUpdatedAt=None, latestUpdatedAt=None, return_full_result=False): 
    print(lists)

# all parameters are optional; no parameters returns all lists
```

Create Static List
-----------
API Ref: http://developers.marketo.com/rest-api/assets/static-lists/#create_and_update
```python
lead = mc.execute(method='create_list', folderId=8, folderType='Folder', name='Test List', description='Optional')

# 'folderType' is either 'Folder' or 'Program'
# description is optional
```

Update Static List
----------
API Ref: http://developers.marketo.com/rest-api/assets/static-lists/#create_and_update
```python
lead = mc.execute(method='update_list', id=123, name='new name', description='new description')

# 'id' and either 'name' or 'description' need to be specified (or all of them)
```

Delete List
-----------
API Ref: http://developers.marketo.com/rest-api/assets/static-lists/#delete
```python
lead = mc.execute(method='delete_list', id=123)
```

Smart Lists
=====

Get Smart List by Id
-------------------
API ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Smart_Lists/getSmartListByIdUsingGET
```python
smart_list = mc.execute(method='get_smart_list_by_id', id=123, return_full_result=False)
# set return_full_result to get the nextPageToken and requestId returned; actual 
#  result will be in the 'result' key
```

Get Smart List by Name
-------------------
API ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Smart_Lists/getSmartListByNameUsingGET
```python
smart_list = mc.execute(method='get_smart_list_by_name', name='Abc', return_full_result=False)
# set return_full_result to get the nextPageToken and requestId returned; actual 
#  result will be in the 'result' key
```

Get Smart Lists
-------------------
API ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Smart_Lists/getSmartListsUsingGET
```python
for smart_lists in mc.execute(method='get_smart_lists', folderId=123, folderType='Folder', offset=None, 
                              maxReturn=None, earliestUpdatedAt=None, latestUpdatedAt=None, return_full_result=False):
    print(smart_lists)
# all parameters are optional; no parameters returns all lists
# maxReturn defaults to 200
# offset defaults to 0; it is automatically incremented, so it's only for when you want to start at a specific offset
# set return_full_result to get the nextPageToken and requestId returned; actual 
#  result will be in the 'result' key
```

Delete Smart List
-------------------
API ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Smart_Lists/deleteSmartListByIdUsingPOST 
```python
smart_list = mc.execute(method='delete_smart_list', id=123)
# set return_full_result to get the nextPageToken and requestId returned; actual 
#  result will be in the 'result' key
```

Clone Smart List
-------------------
API ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Smart_Lists/cloneSmartListUsingPOST 
```python
smart_list = mc.execute(method='clone_smart_list', id=123, name='cloned smart list', folderId=123, folderType='Folder', 
                        return_full_result=False, description=None)
# set return_full_result to get the nextPageToken and requestId returned; actual 
#  result will be in the 'result' key
# description is optional
```

Smart Campaigns
================


Get Smart Campaign by Id
-----------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Smart_Campaigns/getSmartCampaignByIdUsingGET
```python
campaign = mc.execute(method='get_smart_campaign_by_id', id=1170)
```

Get Smart Campaign by Name
-----------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Smart_Campaigns/getSmartCampaignByNameUsingGET
```python
campaign = mc.execute(method='get_smart_campaign_by_name', name='my smart campaign name')
```

Get Campaign by Id - SUPERCEDED
------------------
Use "Get Smart Campaign by Id" instead. 

API Ref: http://developers.marketo.com/documentation/rest/get-campaign-by-id/
```python
campaign = mc.execute(method='get_campaign_by_id', id=1170)
```

Get Smart Campaigns (Generator)
-------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Smart_Campaigns/getAllSmartCampaignsGET
```python
for campaigns in mc.execute(method='get_smart_campaigns', earliestUpdatedAt=None, latestUpdatedAt=None, 
                            folderId=None, folderType=None,
                            maxReturn=200, offset=0, 
                            return_full_result=False): 
    print(campaigns)

# all parameters are optional; folderId and folderType need to be specified together; 
# folderType can be "Folder" or "Program"
# set return_full_result to True to get the full API response including requestId (not just the 'result' key)
```

Get Multiple Campaigns - SUPERCEDED
----------------------
Use "Get Smart Campaigns" instead. 

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

Activate Smart Campaign
-----------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Smart_Campaigns/activateSmartCampaignUsingPOST
```python
campaign = mc.execute(method='activate_smart_campaign', id=1880)
```

Deactivate Smart Campaign
-----------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Smart_Campaigns/deactivateSmartCampaignUsingPOST
```python
campaign = mc.execute(method='deactivate_smart_campaign', id=1880)
```

Create Smart Campaign
---------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Smart_Campaigns/createSmartCampaignUsingPOST
```python
campaign = mc.execute(method='create_smart_campaign', name='New Smart Campaign', folderId=898, folderType='Folder', 
                      description=None)
```

Update Smart Campaign
--------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Smart_Campaigns/updateSmartCampaignUsingPOST
```python
campaign = mc.execute(method='update_smart_campaign', id=1880, name='New Name', description=None)
```

Clone Smart Campaign
--------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Smart_Campaigns/cloneSmartCampaignUsingPOST
```python
campaign = mc.execute(method='clone_smart_campaign', id=1880, name='New Name', folderId=898, folderType='Folder', 
                      isExecutable=False, description=None)
# isExecutable and description are optional
```

Delete Smart Campaign
--------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Smart_Campaigns/deleteSmartCampaignUsingPOST
```python
campaign = mc.execute(method='delete_smart_campaign', id=1880)
```

Get Smart List by Smart Campaign Id
--------------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Smart_Campaigns/getSmartListBySmartCampaignIdUsingGET 
```python
smart_list = mc.execute(method='get_smart_list_by_smart_campaign_id', id=123, includeRules=True, 
                        return_full_result=False)
# set includeRules to False if you do not want to get all triggers and filters of the smart list in the response 
```


Email Templates
===============

Create Email Template
---------------------
API Ref: http://developers.marketo.com/documentation/asset-api/create-email-template/
```python
template = mc.execute(method='create_email_template', folderId=14, folderType="Folder", name="API Email Template", 
    content="email_template.html", description="Hello Description")

# description is optional
# content should contain path to HTML file
```

Get Email Template by Id
------------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-email-template-by-id/
```python
template = mc.execute(method='get_email_template_by_id', id=41, status='approved')

# status is optional; values are 'draft' or 'approved'; a single email can have both an approved and a draft version
```

Get Email Template by Name
------------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-email-template-by-name/
```python
template = mc.execute(method='get_email_template_by_name', name='API Email Template', status='approved')

# status is optional: values are 'draft' or 'approved'; a single email can have both an approved and a draft version
```

Update Email Template
---------------------
API Ref: http://developers.marketo.com/documentation/asset-api/update-email-template/
```python
template = mc.execute(method='update_email_template', id=41, name='API Email Template', description=None)

# name and description are optional, but - of course - you want to pass in at least 1 of them
# this is only to update name and description, use 'Update Email Template Content' to update the HTML
```

Delete Email Template
---------------------
API Ref: http://developers.marketo.com/documentation/asset-api/delete-email-template-by-id/
```python
template = mc.execute(method='delete_email_template', id=41)
```

Get Email Templates
-------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-email-templates/
```python
template = mc.execute(method='get_email_templates', status='draft', maxReturn=None)

# status and maxReturn are optional; status is 'draft' or 'approved'; default for maxReturn is 20 and max is 200
# if you specify status, it will return an approved email with a draft for both status='draft' AND status='approved'
```

Get Email Template Used By
-------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Email_Templates/getEmailTemplateUsedByUsingGET

```python
template = mc.execute(method='get_email_template_used_by', id=41, maxReturn=None)

# maxReturn is optional; default for maxReturn is 20 and max is 200
```


Get Email Template Content
--------------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-email-template-content-by-id/
```python
template = mc.execute(method='get_email_template_content', id=39, status='approved')
with open('email-template-content.html', 'w', encoding='utf-8') as f:
    f.write(template[0]['content'])

# status is optional: values are 'draft' or 'approved'
```

Update Email Template Content
-----------------------------
API Ref: http://developers.marketo.com/documentation/asset-api/update-email-template-content-by-id/
```python
template = mc.execute(method='update_email_template_content', id=42, content='email-template-content.html')

# 'content' points to a file
```

Approve Email Template
----------------------
API Ref: http://developers.marketo.com/documentation/asset-api/approve-email-template-by-id/
```python
template = mc.execute(method='approve_email_template', id=42)
```

Unapprove Email Template
----------------------
API Ref: http://developers.marketo.com/documentation/asset-api/unapprove-email-template-by-id/
```python
template = mc.execute(method='unapprove_email_template', id=42)
```

Discard Email Template Draft
----------------------------
API Ref: http://developers.marketo.com/documentation/asset-api/discard-email-template-draft-by-id/
```python
template = mc.execute(method='discard_email_template_draft', id=42)
```

Clone Email Template
--------------------
API Ref: http://developers.marketo.com/documentation/asset-api/clone-email-template/
```python
template = mc.execute(method='clone_email_template', id=42, name='cloned template', folderId=14, folderType='Folder')

# folderId 14 is the Email Templates folder in the Default workspace
```

Emails
======

Create Email
------------
API Ref: http://developers.marketo.com/documentation/asset-api/create-email/
```python
email = mc.execute(method='create_email', folderId=13, folderType="Folder", name="API Email", template=30,
                      description='Hello Description', subject='Subject for API Email', fromName='Info',
                      fromEmail='info@example.com', replyEmail=None, operational=None)

# description, subject, fromName, fromEmail, replyEmail and operational are optional
# without subject, fromName and fromEmail you can't approve the email
# this is where you create the email shell, in 'Update Email Content in Editable Section' you specify the email body
```

Get Email by Id
---------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-email-by-id/
```python
email = mc.execute(method='get_email_by_id', id=263, status='draft')

# status is optional: values are 'draft' or 'approved'
```

Get Email by Name
-----------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-email-by-name/
```python
email = mc.execute(method='get_email_by_name', name='API Email', status='draft', folderId=None, folderType=None)

# status, folderId and folderType are optional; folderId and folderType need to be specified together
```

Delete Email
------------
API Ref: http://developers.marketo.com/documentation/asset-api/delete-email-by-id/
```python
email = mc.execute(method='delete_email', id=263)
```

Update Email
------------
API Ref: http://developers.marketo.com/documentation/asset-api/update-email/
```python
email = mc.execute(method='update_email', id=264, name="API Email 2", description='Hello New Description', preHeader=None, operational=None, published=None, textOnly=None, webView=None)

# name and description are optional, but - of course - you want to pass in at least 1 of them
```

Get Emails
----------
API Ref: http://developers.marketo.com/documentation/asset-api/get-emails/
```python
email = mc.execute(method='get_emails', status='approved', folderId=13, folderType='Folder', maxReturn=None)

# status, folderId, folderType and maxReturn are optional; folderId and folderType need to be specified together
# default for maxReturn is 20 and max is 200
# status can be 'draft' or 'approved'
```

Get Email Content
-----------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-email-content-by-id
```python
email = mc.execute(method='get_email_content', id=40, status=None)

# status is optional and can be 'draft' or 'approved'
```

Update Email Content
--------------------
API Ref: http://developers.marketo.com/documentation/asset-api/update-email-content-by-id
```python
email = mc.execute(method='update_email_content', id=13, type='Text', subject='New Subject Line',
                   fromEmail='jep@example.com', fromName='Jep', replyTo='jep@example.com')

# subject, fromEmail, fromName and replyTo are optional
# type should be 'Text' or 'DynamicContent'; if you need a combination of text and dynamic, make 2 calls
```

Update Email Content in Editable Section
----------------------------------------
API Ref: http://developers.marketo.com/documentation/asset-api/update-email-content-in-editable-section/
```python
html_content = '''<span style="color:#d9930e; font-size:27px;">Dear {{lead.First Name:default=friend}}, Donec 
                  Scelerisque Leosera</span><br /><br /><div style="font-size:18px;">Aliquam nec erat at purus 
                  cursus interdum<br/>vestibulum ligula augue</div><br />'''
email = mc.execute(method='update_email_content_in_editable_section', id=275, htmlId='lt-column', type='Text', 
                   value=html_content, textValue=None)

# textValue is optional
# type can be 'Text', 'DynamicContent' or 'Snippet'
```

Get Email Dynamic Content
-------------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-email-dynamic-content-by-id/
```python
email = mc.execute(method='get_email_dynamic_content', id=279, dynamicContentId='RVMtU2VjdGlvbiAx', status=None)

# status is optional and can be 'draft' or 'approved'
```

Update Email Dynamic Content
----------------------------
API Ref: http://developers.marketo.com/documentation/asset-api/update-email-dynamic-content-by-id/
```python
email = mc.execute(method='update_email_dynamic_content', id=280, dynamicContentId='RVMtY29sdW1uX3N1YnRpdGxl',
                   segment='Dutch', value='<p>Dutch text</p>', type='HTML')
```

Approve Email
-------------
API Ref: http://developers.marketo.com/documentation/asset-api/approve-email-by-id
```python
email = mc.execute(method='approve_email', id=117)
```

Unapprove Email
---------------
API Ref: http://developers.marketo.com/documentation/asset-api/unapprove-email-by-id
```python
email = mc.execute(method='unapprove_email', id=117)
```

Discard Email Draft
-------------------
API Ref: http://developers.marketo.com/documentation/asset-api/discard-email-draft-by-id/
```python
email = mc.execute(method='discard_email_draft', id=117)
```

Clone Email
-----------
API Ref: http://developers.marketo.com/documentation/asset-api/clone-email
```python
email = mc.execute(method='clone_email', id=117, name='clone of MHE', folderId=13, folderType='Folder', 
                   description='description', operational=None)

# description and operational are optional; operational defaults to false
```

Send Sample Email
-----------------
API Ref: http://developers.marketo.com/documentation/asset-api/send-sample-email/
```python
email = mc.execute(method='send_sample_email', id=117, emailAddress='jep@example.com', textOnly=None, leadId=46)

# textOnly and leadId are optional; textOnly will send the text version of the email in additional to the html version
```

Get Email Full Content
-----------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Emails/getEmailFullContentUsingGET
```python
email = mc.execute(method='get_email_full_content', id=117, status=None, leadId=None, type=None)

# status, leadId, and type are optional; status defaults to approved if asset is approved, draft if not.
# leadId defines the lead to impersonate
# default for type is HTML
```

Update Email Full Content
-----------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Emails/createEmailFullContentUsingPOST
```python
email = mc.execute(method='update_email_full_content', id=117, content='email_content.html')

# NOTE: Replaces the HTML of an Email that has had its relationship broken from its template; currently appears there is no way to set text only content
# content should be an HTML document to update with (cannot include JavaScript or script tags)
```

Get Email Variables
-------------------

API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Emails/getEmailVariablesUsingGET
```python
variables = mc.execute(method='get_email_variables', id=1124)
```

Update Email Variable
-------------------

API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Emails/updateVariableUsingPOST
```python
variable = mc.execute(method='update_email_variable', id=1124, name='preheaderBackgroundColor', value='#81898c',
           moduleId='preheader')
```

Landing pages
=============

Get Landing Pages
-----------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/get-landing-pages/
```python
lp = mc.execute(method='get_landing_pages', maxReturn=None, status=None, folderId=None, folderType=None)

# status, folderId, folderType and maxReturn are optional; folderId and folderType need to be specified together
# default for maxReturn is 20 and max is 200
# status can be 'draft' or 'approved'
```

Create Landing Page
-------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/create-landing-page/
```python
lp = mc.execute(method='create_landing_page', name='API LP', folderId=894,
                folderType='Folder', template=42, description=None, title=None, 
                keywords=None, robots=None, customHeadHTML=None, facebookOgTags=None,
                prefillForm=None, mobileEnabled=None)

# description, title, keywords, robots, customHeadHTML, facebookOgTags, 
#  prefillForm and mobileEnabled are optional
# prefillForm and mobileEnabled default to false
```

Get Landing Page by Id
-----------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/get-landing-page-by-id/
```python
lp = mc.execute(method='get_landing_page_by_id', id=360, status=None)

# status is optional and can be 'draft' or 'approved'
```

Get Landing Page by Name
------------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/get-landing-page-by-name/
```python
lp = mc.execute(method='get_landing_page_by_name', name='Landing page Demo', status=None)

# status is optional and can be 'draft' or 'approved'
```

Delete Landing Page
-------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/delete-landing-page/
```python
lp = mc.execute(method='delete_landing_page', id=411)
```

Update Landing Page Metadata
----------------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/update-landing-page-metadata/
```python
lp = mc.execute(method='update_landing_page', id=410, description=None, title=None,
                keywords=None, robots=None, customHeadHTML=None, facebookOgTags=None, 
                prefillForm=None, mobileEnabled=None, styleOverRide=None, urlPageName=None)

# description, title, keywords, robots, customHeadHTML, facebookOgTags, 
#  prefillForm, mobileEnabled, styleOverRide and urlPageName are optional
# urlPageName is used to change the URL of the page
```

Get Landing Page Content
------------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/get-landing-page-content/
```python
lp = mc.execute(method='get_landing_page_content', id=410, status='draft')

# status is optional and can be 'draft' or 'approved'
```


Create Landing Page Content Section
-----------------------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/add-landing-page-content-section/
```python
lp = mc.execute(method='create_landing_page_content_section', id=410, type='RichText', value='<p>Subtitle</p>',
                backgroundColor=None, borderColor=None, borderStyle=None, borderWidth=None, height=None,
                layer=None, left=100, opacity=1.0, top=50, width=300, hideDesktop=None, hideMobile=None,
                contentId=None)

# contentId is required for Guided Landing pages
# backgroundColor, borderColor, borderStyle, borderWidth, height, layer, left, opacity, top, width, 
#  hideDesktop and hideMobile are optional
# height defaults to auto; layer defaults to 15; specify opacity as fractional and use 1.0 for 100%
# backgroundColor, borderColor, borderStyle and borderWidth don't seem to do anything at this time
```

Update Landing Page Content Section
-----------------------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/update-landing-page-content-section/
```python
lp = mc.execute(method='update_landing_page_content_section', id=410, contentId=2200, type='RichText',
                value='<p>Updated Title</p>', backgroundColor=None, borderColor=None, borderStyle=None,
                borderWidth=None, height=None, zIndex=15, left=50, opacity=1.0, top=50, width=300, 
                hideDesktop=None, hideMobile=None, imageOpenNewWindow=None, linkUrl=None)

# make section dynamic: 
lp = mc.execute(method='update_landing_page_content_section', id=410, contentId=2218,
                                  type='DynamicContent', value=1003)

# backgroundColor, borderColor, borderStyle, borderWidth, height, layer, left, opacity, top, width, 
#  hideDesktop and hideMobile are optional
# height defaults to auto; layer defaults to 15; specify opacity as fractional and use 1.0 for 100%
# contentId changes when the page is approved
# in case of type=DynamicContent, the value is the id of the Segmentation
# backgroundColor, borderColor, borderStyle and borderWidth don't seem to do anything
```

Delete Landing Page Content Section
-----------------------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/delete-landing-page-content-section/
```python
lp = mc.execute(method='delete_landing_page_content_section', id=410, contentId=2215)

# use 'Get Landing page Content' to find the contentId (which changes when page is approved)
```

Get Landing Page Dynamic Content
--------------------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/get-dynamic-content-section/
```python
lp = mc.execute(method='get_landing_page_dynamic_content', id=410, ...)
```

Update Landing Page Dynamic Content
-----------------------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/update-dynamic-content-section/
```python
lp = mc.execute(method='update_landing_page_dynamic_content', id=410, ...)
```


Approve Landing Page
--------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/discard-landing-page-draft/
```python
lp = mc.execute(method='approve_landing_page', id=410)
```

Unapprove Landing Page
----------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/unapprove-landing-page/
```python
lp = mc.execute(method='unapprove_landing_page', id=410)
```

Discard Landing Page Draft
--------------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/discard-landing-page-draft/
```python
lp = mc.execute(method='discard_landing_page_draft', id=410)
```

Clone Landing Page
------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/clone-landing-page/
```python
lp = mc.execute(method='clone_landing_page', id=410, name='cloned landing page', folderId=894, 
                folderType='Folder', description=None, template=42)
                
# description is optional
# template should be optional but is currently required
```

Forms
=====

Get Forms: 
----------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/get-forms/
```python
forms = mc.execute(method='get_forms', status=None, folderId=None, folderType=None, maxReturn=None)

# status, folderId, folderType and maxReturn are optional
```

Get Form by Id
----------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/get-form-by-id/
```python
form = mc.execute(method='get_form_by_id', id=50, status=None)

# status is optional and can be 'draft' or 'approved'
```

Get Form by Name
----------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/get-form-by-name/
```python
form = mc.execute(method='get_form_by_name', name='Form Demo', status=None)

# status is optional and can be 'draft' or 'approved'
```

Get Form Fields List
----------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/get-form-fields-list/
```python
fields = mc.execute(method='get_form_fields', id=50, status=None)

# status is optional and can be 'draft' or 'approved'
```

Add Field to Form
----------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/add-field-to-form/
```python
field = mc.execute(method='create_form_field', id=104, fieldId='AnnualRevenue', label='Rev', labelWidth=200, 
                   fieldWidth=200, instructions='fill out this field',
                   required=True, formPrefill=True, initiallyChecked=None, values=None, labelToRight=None,
                   hintText='hint', defaultValue=100, minValue=100, maxValue=1000000, multiSelect=None,
                   maxLength=None, maskInput=None, visibleLines=None)

# only id and fieldId are required, all others are optional
```

Create Form
-----------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/create-form/
```python
form = mc.execute(method='create_form', name='API Form 4', folderId=140, folderType='Folder',
                  description='optional description', language='Dutch', locale='nl_NL', progressiveProfiling=True,
                  labelPosition='above', fontFamily='Droid Sans Mono', fontSize='12px', knownVisitor=None)

# description, language, locale, progressiveProfiling, labelPosition, fontFamily, fontSize, knownVisitor, theme are optional
# locale examples: en_US, en_UK, fr_FR, de_DE, zh_CN, ja_JP, hi_IN, nl_NL, nl_BE
# fontFamily/fontSize and theme are mutually exclusive
# fontFamily doesn't seem to work
# labelPosition is left or above (lower case)
# TODO: knownVisitor needs further explanation
```

Get Form Thank You Page
------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/get-form-thank-you-page/
```python
# not implemented yet
```

Update Form Thank You Page
--------------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/update-form-thank-you-page/
```python
# not implemented yet
```

Update Form Metadata
-----------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/update-form/
```python
form = mc.execute('update_form', id=50, name=None, description=None, language=None, locale=None, progressiveProfiling=None,
                    labelPosition=None, fontFamily=None, fontSize=None, knownVisitor=None, formTheme=None,
                    customcss=None)

# id is required, all others are optional
```

Discard Form Draft
--------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/discard-form-draft/
```python
form = mc.execute(method='discard_form_draft', id)
```

Approve Form
------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/approve-form/
```python
form = mc.execute(method='approve_form', id)
```

Unapprove Form
--------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/unapprove-form/
```python
form = mc.execute(method='unapprove_form', id)
```

Clone Form
----------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/clone-form/
```python
form = mc.execute(method='clone_form', id=50, name='new form name', folderId=12, folderType='Folder', description=None)
```

Delete Form
-----------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/delete-form/
```python
form = mc.execute(method='delete_form', id=50)
```

Update Form Field
-----------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/update-form-field/
```python
field = mc.execute(method='update_form_field', id=104, fieldId='AnnualRevenue', label='Revenue', labelWidth=150, 
                   fieldWidth=150, instructions='please fill out this field',
                   required=False, formPrefill=True, initiallyChecked=None, values=None, labelToRight=None,
                   hintText='hint', defaultValue=100, minValue=100, maxValue=1000000, multiSelect=None,
                   maxLength=None, maskInput=None, visibleLines=None)

# only id and fieldId are required, all others are optional
```

Remove Form Field
-----------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/remove-form-field/
```python
field = mc.execute(method='delete_form_field', id=104, fieldId='AnnualRevenue')
```

Update Form Field Visibility Rules
----------------------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/update-form-field-visibility-rules/
```python
not yet implemented
```

Add Rich Text Form Field
------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/add-rich-text-form-field/
```python
not yet implemented
```

Add Fieldset
------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/add-fieldset/
```python
not yet implemented
```

Remove Field from Fieldset
--------------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/remove-field-from-fieldset/
```python
not yet implemented
```

Get Available Form Fields
------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/get-available-form-fields/
```python
not yet implemented
```

Change Form Field Positions
--------------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/change-form-field-positions/
```python
not yet implemented
```

Update Submit Button
--------------------
API Ref: http://developers.marketo.com/documentation/marketo-rest-apis-web-page-objects/update-submit-button/
```python
not yet implemented
```


Files
========

Create File
-------------
API Ref: http://developers.marketo.com/documentation/asset-api/create-a-file/
```python
lead = mc.execute(method='create_file', name='Marketo-Logo.jpg', file='Marketo-Logo.jpg', folder=115, description=None)

# NOTE: the behavior of the call will change; this describes current behavior
# description is optional
# insertOnly is documented in the API Ref but it is non-functional
# 'name' needs to match the 'file' name, otherwise you get error 709 "Upload file name and/or extension is 
#   different from name in parameter"
# in 'file', specify a path if file is not in the same folder as the Python script
```

Get File by Id
--------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-file-by-id/
```python
try:
    file = mc.execute(method='get_file_by_id', id=16837)
except KeyError:
    file = False
```

Get File by Name
----------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-file-by-name/
```python
try:
    file = mc.execute(method='get_file_by_name', name='clogo8.jpg')
except KeyError:
    file = False
```

List Files
----------
API Ref: http://developers.marketo.com/documentation/asset-api/list-files/
```python
lead = mc.execute(method='list_files', folder=709, maxReturn=None)

# folder and maxReturn are optional; default for maxReturn is 20 and max is 200
```

Update File Content
-------------
API Ref: http://developers.marketo.com/documentation/asset-api/update-file-content/
```python
file = mc.execute(method='update_file_content', id=23307, file='Marketo-Logo-Large.jpg')

# in 'file', specify a path if file is not in the same folder as the Python script
```

Snippets
========

Create Snippet
--------------
API Ref: http://developers.marketo.com/documentation/asset-api/create-snippet/
```python
snippet = mc.execute(method='create_snippet', folderId=132, folderType="Folder", name="API Snippet", description=None)

# description is optional
```

Get Snippet By Id
-----------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-snippet-by-id/
```python
snippet = mc.execute(method='get_snippet_by_id', id=9)
```

Delete Snippet
--------------
API Ref: http://developers.marketo.com/documentation/asset-api/delete-snippet-by-id/
```python
snippet = mc.execute(method='delete_snippet', id=9)
```

Update Snippet
--------------
API Ref: http://developers.marketo.com/documentation/asset-api/update-snippet/
```python
snippet = mc.execute(method='update_snippet', id=9, name="API Snippet 2", description='Hello New Description')
```

Get Snippets
------------
API Ref: http://developers.marketo.com/documentation/asset-api/update-snippet/
```python
snippets = mc.execute(method='get_snippets', maxReturn=None)

# maxReturn is optional; default for maxReturn is 20 and max is 200
```

Get Snippet Content
-------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-snippet-content-by-id/
```python
snippet = mc.execute(method='get_snippet_content', id=9, status=None)

# status is optional and can be 'draft' or 'approved'
```

Update Snippet Content
----------------------
API Ref: http://developers.marketo.com/documentation/asset-api/update-snippet-content-by-id/
```python
html_content = '<html><head></head><body><p>Hello World</p></body></html>'
snippet = mc.execute(method='update_snippet_content', id=9, type='HTML', content=html_content)
```

Approve Snippet
---------------
API Ref: http://developers.marketo.com/documentation/asset-api/approve-snippet-by-id/
```python
snippet = mc.execute(method='approve_snippet', id=9)
```

Unapprove Snippet
-------------------
API Ref: http://developers.marketo.com/documentation/asset-api/unapprove-snippet-by-id/
```python
snippet = mc.execute(method='unapprove_snippet', id=9)
```

Discard Snippet Draft
---------------------
API Ref: http://developers.marketo.com/documentation/asset-api/discard-snippet-draft-by-id/
```python
snippet = mc.execute(method='discard_snippet_draft', id=9)
```

Clone Snippet
--------------
API Ref: http://developers.marketo.com/documentation/asset-api/clone-snippet/
```python
snippet = mc.execute(method='clone_snippet', id=9, name='Cloned Snippet', folderId=132, folderType='Folder', 
                     description=None)

# description is optional
```

Update Snippet Dynamic Content
-------------------
API Ref: http://developers.marketo.com/documentation/asset-api/update-snippet-dynamic-content-by-id/    
```python
snippet = mc.execute(method='update_snippet_dynamic_content', id=9, segmentId=1008, 
                     value='<p>Text in Dutch</p>', type='HTML')
```

Get Snippet Dynamic Content
-------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-snippet-dynamic-content-by-id/
```python
snippet = mc.execute(method='get_snippet_dynamic_content', id=9)
```

Segmentations
=============

Get Segmentations
-----------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-segmentation-by-id/
```python
segmentations = mc.execute(method='get_segmentations', status='approved')

# status is optional; values are 'draft' or 'approved'
```

Get Segments
-----------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-segments/
```python
segments = mc.execute(method='get_segments', id=1001, status=None)

# status is optional; values are 'draft' or 'approved'
```


Landing Page Templates
===============

Create Landing Page Template
---------------------
API Ref: http://developers.marketo.com/documentation/asset-api/create-landing-page-template/
```python
template = mc.execute(method='create_landing_page_template', name='API LP Template', folderId=11,
                      folderType='Folder', description='Description', templateType='freeForm')

# description and templateType are optional; templateType can be freeForm (default) or guided
```

Get Landing Page Template by Id
------------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-landing-page-template-by-id/
```python
template = mc.execute(method='get_landing_page_template_by_id', id=30, status='approved')

# status is optional; values are 'draft' or 'approved'; a single landing page can have both an approved and a draft 
# version
```

Get Landing Page Template by Name
------------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-landing-page-template-by-name/
```python
template = mc.execute(method='get_landing_page_template_by_name', name='API LP Template', status='draft')

# status is optional: values are 'draft' or 'approved'; a single landing page can have both an approved and a draft 
# version
```

Update Landing Page Template
---------------------
API Ref: http://developers.marketo.com/documentation/asset-api/update-landing-page-template/
```python
template = mc.execute(method='update_landing_page_template', id=59, name='API LP Template 2', description=None)

# name and description are optional, but - of course - you want to pass in at least 1 of them
# this is only to update name and description, use 'Update Landing Page Template Content' to update the HTML
```

Delete Landing Page Template
---------------------
API Ref: N/A
```python
template = mc.execute(method='delete_landing_page_template', id=64)
```

Get Landing Page Templates
-------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-multiple-landing-page-templates/
```python
template = mc.execute(method='get_landing_page_templates', status='approved', folderId=842, folderType='Folder')

# status, folderId, folderType and maxReturn are optional; status is 'draft' or 'approved'
# default for maxReturn is 20 and max is 200
# if you specify status, it will return an approved landing page with a draft for both status='draft' AND status='approved'
```

Get Landing Page Template Content
--------------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-landing-page-template-content/
```python
template = mc.execute(method='get_landing_page_template_content', id=30)
with open('landing-page-template-content-2.html', 'w', encoding='utf-8') as f:
    f.write(template[0]['content'])

# status is optional: values are 'draft' or 'approved'
```

Update Landing Page Template Content
-----------------------------
API Ref: http://developers.marketo.com/documentation/asset-api/update-landing-page-template-content-by-id/
```python
template = mc.execute(method='update_landing_page_template_content', id=59, content='LP-template-content.html')

# 'content' points to a file
```

Approve Landing Page Template
----------------------
API Ref: N/A
```python
template = mc.execute(method='approve_landing_page_template', id=61)
```

Unapprove Landing Page Template
----------------------
API Ref: N/A
```python
template = mc.execute(method='unapprove_landing_page_template', id=61)
```

Discard Landing Page Template Draft
----------------------------
API Ref: N/A
```python
template = mc.execute(method='discard_landing_page_template_draft', id=42)
```

Clone Landing Page Template
--------------------
API Ref: N/A
```python
template = mc.execute(method='clone_landing_page_template', id=42, name='cloned landing page template', 
                      folderId=11, folderType='Folder')

# folderId 11 is the Landing Page Templates folder in the Default workspace
```


Programs
========

Create Program
--------------
API Ref: http://developers.marketo.com/documentation/programs/create-a-program/
```python
tags = {'Language': 'English'}
costs = '[{"startDate":"2015-01-01","cost":2000,"note":""}]'
program = mc.execute(method='create_program', folderId=28, folderType='Folder', name='Program Name', 
        description='new Program', type='Default', channel='Operational', tags=tags, costs=costs)

# description, tags and costs are optional
# the 'note' parameter in 'costs' is currently required but will be made optional in a future release  
```

Get Program by Id
-----------------
API Ref: http://developers.marketo.com/documentation/programs/get-program-by-id/
```python
try:
    lead = mc.execute(method='get_program_by_id', id=1014)
except KeyError:
    lead = False
```

Get Program by Name
-------------------
API Ref: http://developers.marketo.com/documentation/programs/get-program-by-name/
```python
try:
    lead = mc.execute(method='get_program_by_name', name='Email Program Test')
except KeyError:
    lead = False
```

Get Program by Tag Type
-----------------------
API Ref: http://developers.marketo.com/documentation/programs/get-programs-by-tag-type/
```python
try:
    program = mc.execute(method='get_program_by_tag_type', tagType='Language', tagValue='English', maxReturn=20)
except KeyError:
    program = False
# maxReturn defaults to 20 and can be set to 200 max; this loops and gets all programs with the specific Tag & Value
```

Update Program
--------------
API Ref: http://developers.marketo.com/documentation/programs/update-program/
```python
tags = {'Language': 'English'}
program = mc.execute(method='update_program', id=1160, name='Updated Name', description='description update', tags=tags)

# the 'costs' and 'costsDestructiveUpdate' parameters as mentioned in the docs are not implemented yet
```

Delete Program
--------------
API Ref: http://developers.marketo.com/documentation/programs/delete-program-by-id/
```python
program = mc.execute(method='delete_program', id=1208)
```

Browse Programs
---------------
API Ref: http://developers.marketo.com/documentation/programs/browse-programs/
```python
lead = mc.execute(method='browse_programs', status='completed', maxReturn=200)

# status and maxReturn are optional; default for maxReturn is 20 and max is 200
```

Clone Program
-------------
API Ref: http://developers.marketo.com/documentation/programs/clone-program/
```python
program = mc.execute(method='clone_program', id=1207, name="Program Clone", folderId=28, folderType='Folder', 
                     description="this is a description")

# description is optional
```

Approve Program
---------------
API Ref: http://developers.marketo.com/documentation/programs/approve-program/
```python
program = mc.execute(method='approve_program', id=1208)
```

Unapprove Program
-----------------
API Ref: http://developers.marketo.com/documentation/programs/unapprove-program/
```python
program = mc.execute(method='approve_program', id=1208)
```

Get Smart List by Program Id
--------------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Programs/getSmartListByProgramIdUsingGET 
```python
smart_list = mc.execute(method='get_smart_list_by_program_id', id=123, includeRules=True, 
                        return_full_result=False)
# only works to get the built-in Smart List for Email Programs
# set includeRules to False if you do not want to get all filters of the smart list in the response 
```

Get Channels
------------
API Ref: http://developers.marketo.com/documentation/programs/get-channels/
```python
channels = mc.execute(method='get_channels', maxReturn=None)

# maxReturn is optional; default for maxReturn is 20 and max is 200
```

Get Channel by Name
-------------------
API Ref: http://developers.marketo.com/documentation/programs/get-channel-by-name/
```python
try:
    channel = mc.execute(method='get_channel_by_name', name="Nurture")
except KeyError:
    channel = False
```

Get Tags
--------
API Ref: http://developers.marketo.com/documentation/programs/get-tags/
```python
tags = mc.execute(method='get_tags', maxReturn=None)

# maxReturn is optional; default for maxReturn is 20 and max is 200
```

Get Tag by Name
---------------
API Ref: http://developers.marketo.com/documentation/programs/get-tag-by-name/
```python
try:
    tag = mc.execute(method='get_tag_by_name', name="Language")
except KeyError:
    tag = False
```

Custom Object Types
===================

Create/Update Custom Object Type
-----------------------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Custom_Objects/syncCustomObjectTypeUsingPOST
```python
    resultType = mc.execute(method='create_update_custom_object_type', apiName='transactions', displayName='Transactions', action='createOnly', description='Transactions custom object for the transactions')
```

Delete Custom Object Type
-------------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Custom_Objects/deleteCustomObjectsUsingPOST
```python
    result = mc.execute(method='delete_custom_object_type', apiName='transactions')
```

Approve Custom Object Type
--------------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Custom_Objects/approveCustomObjectTypeUsingPOST
```python
    result = mc.execute(method='approve_custom_object_type', apiName='transactions')
```

Discard Custom Object Type Draft
--------------------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Custom_Objects/discardCustomObjectTypeUsingPOST
```python
    result = mc.execute(method='discard_custom_object_type', apiName='transactions')
```

Add Custom Object Type Fields
-----------------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Custom_Objects/addCustomObjectTypeFieldsUsingPOST
```python
    fields = [{"displayName": "Email", "description": "Email", "name": "email", "dataType": "link", "relatedTo": {"name": "lead", "field": "email"}},
    {"displayName": "Transaction ID", "description": "Transaction ID", "name": "txid", "dataType": "integer", "isDedupeField": True},
    {"displayName": "Total", "description": "Transaction total", "name": "total", "dataType": "float"}]
    result = mc.execute(method='add_field_custom_object_type', apiName='transactions',fields=fields)
```

List Custom Object Types
------------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Custom_Objects/listCustomObjectTypesUsingGET
```python
    coTypes = mc.execute(method='get_list_of_custom_object_types')
```

Describe Custom Object Type
---------------------------
API Ref: https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Custom_Objects/describeCustomObjectTypeUsingGET
```python
    description = mc.execute(method='describe_custom_object_type')
```

** Not currently implemented **

Delete Custom Object Type Fields
--------------------------------
https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Custom_Objects/deleteCustomObjectTypeFieldsUsingPOST

Update Custom Object Type Field
-------------------------------
https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Custom_Objects/updateCustomObjectTypeFieldUsingPOST

Get Custom Object Type Field Data Types
---------------------------------------
https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Custom_Objects/getCustomObjectTypeFieldDataTypesUsingGET

Get Custom Object Linkable Objects
----------------------------------
https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Custom_Objects/getCustomObjectTypeLinkableObjectsUsingGET

Get Custom Object Dependent Assets
----------------------------------
https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Custom_Objects/getCustomObjectTypeDependentAssetsUsingGET


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
query = [{'TK_ID': 'abc123', 'ListID': 123},{'TK_ID': 'abc123', 'ListID': 12396}]
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

Opportunity Object
==================

Describe Opportunity
--------------------
API Ref: http://developers.marketo.com/documentation/opportunity-api/describe-opportunity/
```python
result = mc.execute(method='describe_opportunity')
```

Create/Update Opportunities
---------------------------
API Ref: http://developers.marketo.com/documentation/opportunity-api/createupdateupsert-opportunities/
```python
opportunities = [{'externalOpportunityId': 'O000004', 'externalCompanyId': 'C000003', 'name': 'Test Opportunity',
                  'amount': 5000, 'closeDate': '2016-06-30', 'isClosed': False, 'stage': 'Qualification',
                  'externalSalesPersonId': 'sam@test.com'}]
result = mc.execute(method='create_update_opportunities', input=opportunities, action=None, dedupeBy=None)

# action and dedupeBy are optional 
# action can be createOnly, updateOnly or createOrUpdate (default)
# dedupeBy is dedupeFields (default) or idField 
```

Delete Opportunities
--------------------
API Ref: http://developers.marketo.com/documentation/opportunity-api/delete-opportunities/
```python
opportunities = [{"externalOpportunityId": "O000004"}]
result = mc.execute(method='delete_opportunities', input=opportunities, deleteBy=None)

# deleteBy is optional; it can be dedupeFields (default) or idField
```

Get Opportunities
-----------------
API Ref: http://developers.marketo.com/documentation/opportunity-api/get-opportunities/
```python
result = mc.execute(method='get_opportunities', filterType='externalOpportunityId', filterValues=['O000003'],
                    fields=['name', 'amount', 'closeDate', 'stage'])
#result = mc.execute(method='get_opportunities', filterType='externalCompanyId', filterValues=['C000003'])

# fields and batchSize are optional; default and maximum batch size is 300
```

Describe Opportunity Roles
--------------------
API Ref: http://developers.marketo.com/documentation/opportunity-api/describe-opportunity-role/
```python
result = mc.execute(method='describe_opportunity_role')
```

Create/Update Opportunities Roles
---------------------------------
API Ref: http://developers.marketo.com/documentation/opportunity-api/createupdateupsert-opportunities-roles/
```python
opportunities_roles = [{'externalOpportunityId': 'O000004', 'leadId': 2, 'role': 'Technical Buyer', 'isPrimary': False}]
result = mc.execute(method='create_update_opportunities_roles', input=opportunities_roles, action=None, dedupeBy=None)

# action and dedupeBy are optional 
# action can be createOnly, updateOnly or createOrUpdate (default)
# dedupeBy is dedupeFields (default) or idField 
```

Delete Opportunity Roles
------------------------
API Ref: http://developers.marketo.com/documentation/opportunity-api/delete-opportunity-roles/
```python
opportunities = [{'externalOpportunityId': 'O000004', 'leadId': 2, 'role': 'Technical Buyer'}]
result = mc.execute(method='delete_opportunity_roles', input=opportunities, deleteBy=None)

# deleteBy is optional; it can be dedupeFields (default, all 3 fields shown) or idField
```

Get Opportunity Roles
---------------------
API Ref: http://developers.marketo.com/documentation/opportunity-api/get-opportunity-roles/
```python
result = mc.execute(method='get_opportunity_roles', filterType='externalOpportunityId', filterValues=['O000003'])
#result = mc.execute(method='get_opportunity_roles', filterType='marketoGUID', filterValues=['63ea3a3f-1b35-4723-850e-99b41b14a636'])
#result = mc.execute(method='get_opportunity_roles', filterType='leadId', filterValues=['2'])

# fields and batchSize are optional; default and maximum batch size is 300
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
```python
result = mc.execute(method='get_companies', filterType='company', filterValues=['Acme 1', 'Acme 2'],
                    fields=['company', 'billingCity', 'billingState', 'website', 'numberOfEmployees'], batchSize=None)
                    
# fields and batchSize are optional
# filterType can be: externalCompanyId, id, externalSalesPersonId, company 
```

Sales Person Object
==============

Describe Sales Person
----------------
API Ref: http://developers.marketo.com/documentation/sales-persons/describe-sales-person/
```python
salesperson = mc.execute(method='describe_sales_person')
```

Create/Update Sales Persons
-----------------------
API Ref: http://developers.marketo.com/documentation/sales-persons/createupdateupsert-sales-persons/
```python
salespeople = [{"externalSalesPersonId":"sam@test.com", "email":"sam@test.com", "firstName":"Sam", "lastName":"Sanosin"},
    {"externalSalesPersonId":"david@test.com", "email":"david@test.com", "firstName":"David", "lastName":"Aulassak"}]
result = mc.execute(method='create_update_sales_persons', input=salespeople, action=None, dedupeBy=None)

# action and dedupeBy are optional
```

Delete Sales Persons
-----------
API Ref: http://developers.marketo.com/documentation/sales-persons/delete-sales-persons/
```python
salespeople = [{"externalSalesPersonId":"sam@test.com"}]
result = mc.execute(method='delete_sales_persons', input=salespeople, deleteBy=None)

# deleteBy is optional; values can be dedupeFields (default) or idField
```

Get Sales Persons
-----------
API Ref: http://developers.marketo.com/documentation/sales-persons/get-sales-persons/
```python
result = mc.execute(method='get_sales_persons', filterType='externalSalesPersonId', filterValues=['sam@test.com'], 
        fields=None, batchSize=None)

# fields and batchSize are optional
# filterType can be: externalSalesPersonId, id, email
```

Bulk Export Leads/Activities/Custom Objects/Program Members
==============

> Replace 'activities' with 'leads', 'custom_objects' or 'program_members' in below to get the equivalent for leads,
> custom objects and program members export. For Custom Objects, the `object_name` attribute is always required.  

List Bulk Export Activities Jobs
----------------
API Ref: http://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Bulk_Export_Activities/getExportActivitiesUsingGET
```python
export_jobs = mc.execute(method='get_activities_export_jobs_list')
```

List Bulk Export Custom Objects Jobs
----------------
```python
export_jobs = mc.execute(method='get_activities_export_jobs_list', object_name='pet_c')

# `object_name` is required; this is the same for all Custom Object bulk export calls
```

Create Bulk Export Activities Job
----------------
API Ref: http://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Bulk_Export_Activities/createExportActivitiesUsingPOST
```python
new_export_job_details = mc.execute(method='create_activities_export_job', fields=['string', 'string'], filters={'createdAt': {'endAt': '2017-11-02', 'startAt': '2017-11-01'}})
```

Create Bulk Export Custom Object Job
----------------
```python
new_export_job_details = mc.execute(method='create_custom_objects_export_job', object_name='pet_c', fields=['string', 'string'], filters={'staticListId': 1025})

# `object_name`, `fields` and `filters` are all required
```

Cancel Bulk Export Activities Job
----------------
API Ref: http://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Bulk_Export_Activities/cancelExportActivitiesUsingPOST
```python
new_export_job_details = mc.execute(method='cancel_activities_export_job', job_id='284742ec-1e5a-46f2-b164-498a41fcaaf6')
```

Enqueue Bulk Export Activities Job
----------------
API Ref: http://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Bulk_Export_Activities/enqueueExportActivitiesUsingPOST
```python
enqueued_job_details = mc.execute(method='enqueue_activities_export_job', job_id='284742ec-1e5a-46f2-b164-498a41fcaaf6')
```

Get Bulk Export Activities Job Status
----------------
API Ref: http://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Bulk_Export_Activities/getExportActivitiesStatusUsingGET
```python
export_job_status = mc.execute(method='get_activities_export_job_status', job_id='284742ec-1e5a-46f2-b164-498a41fcaaf6')
```

Get Bulk Export Activities File
----------------
API Ref: http://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Bulk_Export_Activities/getExportActivitiesFileUsingGET
```python
export_file_contents = mc.execute(method='get_activities_export_job_file', job_id='284742ec-1e5a-46f2-b164-498a41fcaaf6')
```
Or use streaming: 
```python
with mc.execute(method='get_activities_export_job_file', job_id='284742ec-1e5a-46f2-b164-498a41fcaaf6', stream=True) as r:
    with open('filename.csv', 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
# set your preferred chunk_size
```

Named Account Object
==============

Describe Named Accounts
----------------
```python
mc.execute(method='describe_named_accounts')
```

Get Named Accounts
-----------------
```python
for accounts in mc.execute(method='get_named_accounts', filterType='name', filterValues='Acme', 
                        fields='name,score1,annualRevenue', batchSize=None, return_full_result=False, 
                        nextPageToken=None):
    print(accounts)

# filterType may be any single field returned in the searchableFields member of the describe result for named accounts
# specify up to 300 filterValues comma-separated or as a list; you are out of luck if your filterValues have commas
# default and maximum batchSize is 300 (in the response) 
# return_full_result=True will return requestId and nextPageToken
# nextPageToken: optional; normally you wouldn't need it, unless you are resuming a prior export 
```

Get Named Account Lists
-----------------
```python
for lists in mc.execute(method='get_named_account_lists', filterType='dedupeFields', filterValues='Accounts Tier 1',
                        batchSize=None, return_full_result=False, nextPageToken=None):
    print(lists)

# instead of 'dedupeFields' you can also use 'idField', which would be the marketoGUID
# specify up to 300 filterValues comma-separated or as a list; you are out of luck if your filterValues have commas
# default and maximum batchSize is 300 (in the response)
# return_full_result=True will return requestId and nextPageToken
# nextPageToken: optional; normally you wouldn't need it, unless you are resuming a prior export 
```

Get Named Account List Members
------------------
```python
for accounts in mc.execute(method='get_named_account_list_members', id='d5080d12-a40c-4b9f-ae01-453bdf662fdd', 
                        fields='name,score1', batchSize=None, return_full_result=False, nextPageToken=None):
    print(accounts)

# default and maximum batchSize is 300 
# return_full_result=True will return requestId and nextPageToken
# nextPageToken: optional; normally you wouldn't need it, unless you are resuming a prior export 
```

Other Named Account Methods
------
There are stubs for other Named Account methods in `client.py` but those aren't implemented yet. 




Programming Conventions
=======================
Conventions used for functions: 
* functions mirror as closely as possible how the functions work in the Marketo REST API; exceptions: 
get_lead_activities, get_lead_changes and get_deleted_leads where you can pass in a datetime directly rather 
than having to use get_paging_token (which you can still use, if you want to)
* name of the function is exactly the same as on the Marketo Developer website, but lowercase with spaces replaced by 
underscores, and "by Id" removed in case "by Id" is the only option
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
