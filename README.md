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
mc.execute(method='get_lead_activities', activityTypeIds=['23','22'], nextPageToken=None, sinceDatetime='2015-10-06', 
    batchSize=None, listId=None, leadIds=[1,2])

# sinceDatetime format: 2015-10-06T13:22:17-08:00 or 2015-10-06T13:22-0700 or 2015-10-06
# either nextPageToken or sinceDatetime need to be specified
# batchSize, listId and leadIds are optional
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
# maxReturn is optional; default is 20, max is 200
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

# maxDepth, maxReturn and workSpace are optional; default for maxReturn is 20, max is 200
# use the id as returned by 'Browse Folders' or 'Get Folder by Name
# function will loop and return all results
# will throw KeyError when no folder found
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

# status and maxReturn are optional; status is 'draft' or 'approved'
# if you specify status, it will return an approved email with a draft for both status='draft' AND status='approved'
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
email = mc.execute(method='update_email', id=264, name="API Email 2", description='Hello New Description')

# name and description are optional, but - of course - you want to pass in at least 1 of them
```

Get Emails
----------
API Ref: http://developers.marketo.com/documentation/asset-api/get-emails/
```python
email = mc.execute(method='get_emails', status='approved', folderId=13, folderType='Folder', maxReturn=None)

# status, folderId, folderType and maxReturn are optional; folderId and folderType need to be specified together
# status can be 'draft' or 'approved'
```

Get Email Content
-----------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-email-content-by-id
```python
email = mc.execute(method='get_email_content', id=40, status=None)

# status is optional
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
email = mc.execute(method='get_email_dynamic_content', id=279, dynamicContentId='RVMtU2VjdGlvbiAx')
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
                   description='description', isOperational=True)

# description and isOperational are optional; isOperational defaults to false
# right now, if isOperational is set to True, it doesn't seem to create an Operational email 
```

Send Sample Email
-----------------
API Ref: http://developers.marketo.com/documentation/asset-api/send-sample-email/
```python
email = mc.execute(method='send_sample_email', id=117, emailAddress='jep@example.com', textOnly=None, leadId=46)

# textOnly and leadId are optional; textOnly will send the text version of the email in additional to the html version
```


Files
========

Create a File
-------------
API Ref: http://developers.marketo.com/documentation/asset-api/create-a-file/
```python
lead = mc.execute(method='create_file', name='Marketo-Logo3.jpg', file='Marketo-Logo.jpg', folder=115, 
                  description='test file', insertOnly=False)

# description and insertOnly are optional
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
lead = mc.execute(method='list_files', folder=709, offset=0, maxReturn=200)

# offset and maxReturn are optional; max offset is 200, default is 20
```

Update File Content
-------------
API Ref: http://developers.marketo.com/documentation/asset-api/update-file-content/
```python
file = mc.execute(method='update_file_content', id=23307, file='Marketo-Logo-Large.jpg')

# in 'file', specify a path if file is not in the same folder as the Python script
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

<!--
Delete Landing Page Template
---------------------
API Ref: N/A
```python
template = mc.execute(method='delete_landing_page_template', id=64)
```
-->

Get Landing Page Templates
-------------------
API Ref: http://developers.marketo.com/documentation/asset-api/get-multiple-landing-page-templates/
```python
template = mc.execute(method='get_landing_page_templates', status='approved', folderId=842, folderType='Folder')

# status, folderId, folderType and maxReturn are optional; status is 'draft' or 'approved'
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

<!--
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
-->

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
    program = mc.execute(method='get_program_by_tag_type', tagType='Language', tagValue='English')
except KeyError:
    program = False
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

Get Channels
------------
API Ref: http://developers.marketo.com/documentation/programs/get-channels/
```python
channels = mc.execute(method='get_channels', maxReturn=None)

# maxReturn is optional
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

# maxReturn is optional
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


TODO
====
* Implement Snippet APIs
* for Clone Email, fix isOperational parameter


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