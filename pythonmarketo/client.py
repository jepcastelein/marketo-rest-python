from pythonmarketo.helper.http_lib  import  HttpLib
from pythonmarketo.helper.exceptions import MarketoException
import time
import requests

class MarketoClient:    
    host = None
    client_id = None
    client_secret = None
    token = None
    expires_in = None
    valid_until = None
    token_type = None
    scope = None
    last_request_id = None
    API_CALLS_MADE = 0
    API_LIMIT = None
    
    def __init__(self, host, client_id, client_secret, api_limit=None):
        assert(host is not None)
        assert(client_id is not None)
        assert(client_secret is not None)
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.API_LIMIT = api_limit

    def execute(self, method, *args, **kargs):
        result = None
        if self.API_LIMIT and self.API_CALLS_MADE >= self.API_LIMIT:
            raise Exception({'message':'API Calls exceeded the limit : ' + str(self.API_LIMIT), 'code':'416'})

        '''
            max 10 rechecks
        '''
        for i in range(0,10):
            try:
                method_map={
                    'get_leads':self.get_leads,
                    'get_leads_by_listId':self.get_leads_by_listId,
                    'get_multiple_leads_by_filter_type':self.get_multiple_leads_by_filter_type,
                    'get_activity_types':self.get_activity_types,
                    'get_lead_activity':self.get_lead_activity,
                    'get_paging_token':self.get_paging_token,
                    'update_lead':self.update_lead,
                    'create_lead':self.create_lead,
                    'create_update_leads':self.create_update_leads,
                    'get_lead_activity_page':self.get_lead_activity_page,
                    'get_email_content_by_id':self.get_email_content_by_id,
                    'get_email_template_content_by_id':self.get_email_template_content_by_id,
                    'get_email_templates':self.get_email_templates,
                    'run_request_campaign':self.run_request_campaign,
                    'merge_leads':self.merge_leads,
                    'add_to_list':self.add_to_list,
                    'remove_from_list':self.remove_from_list,
                    'browse_folders':self.browse_folders,
                    'create_folder':self.create_folder,
                    'create_get_folder':self.create_get_folder,
                    'get_folder_by_id':self.get_folder_by_id,
                    'get_folder_by_name':self.get_folder_by_name,
                    'list_files':self.list_files,
                    'create_file':self.create_file,
                    'associate_lead':self.associate_lead,
                    'get_lead_partitions':self.get_lead_partitions,
                    'get_list_by_id':self.get_list_by_id,
                    'get_multiple_lists':self.get_multiple_lists,
                    'member_of_list':self.member_of_list,
                    'get_campaign_by_id':self.get_campaign_by_id,
                    'get_multiple_campaigns':self.get_multiple_campaigns,
                    'schedule_campaign':self.schedule_campaign,
                    'request_campaign':self.request_campaign,
                    'import_lead':self.import_lead,
                    'get_import_lead_status':self.get_import_lead_status,
                    'get_import_failure_file':self.get_import_failure_file,
                    'get_import_warning_file':self.get_import_warning_file,
                    'describe':self.describe,
                    'get_lead_changes':self.get_lead_changes,
                    'get_daily_usage':self.get_daily_usage,
                    'get_last_7_days_usage':self.get_last_7_days_usage,
                    'get_daily_errors':self.get_daily_errors,
                    'get_last_7_days_errors':self.get_last_7_days_errors,
                    'delete_lead':self.delete_lead,
                    'get_deleted_leads':self.get_deleted_leads,
                    'update_leads_partition':self.update_leads_partition,
                    'get_lead_by_id':self.get_lead_by_id,
                    'get_multiple_leads_by_program_id':self.get_multiple_leads_by_program_id
                }

                result = method_map[method](*args,**kargs) 
                self.API_CALLS_MADE += 1
            except MarketoException as e:
                '''
                601 -> auth token not valid
                602 -> auth token expired
                '''
                if e.code in ['601', '602']:
                   continue   
                else:
                    raise Exception({'message':e.message, 'code':e.code})    
            break        
        return result
    

    def authenticate(self):
        if self.valid_until is not None and\
            self.valid_until > time.time():
            return
        args = { 
            'grant_type' : 'client_credentials', 
            'client_id' : self.client_id,
            'client_secret' : self.client_secret
        }
        data = HttpLib().get("https://" + self.host + "/identity/oauth/token", args)
        if data is None: raise Exception("Empty Response")
        self.token = data['access_token']
        self.token_type = data['token_type']
        self.expires_in = data['expires_in']
        self.valid_until = time.time() + data['expires_in'] 
        self.scope = data['scope']

    
    def get_leads(self, filtr, values = [], fields = []):
        self.authenticate()
        values = values.split() if type(values) is str else values
        args = {
            'access_token' : self.token,
            'filterType' : str(filtr),
            'filterValues' : (',').join(values)
        }
        if len(fields) > 0:
            args['fields'] = ",".join(fields)
        data = HttpLib().get("https://" + self.host + "/rest/v1/leads.json", args)
        if data is None: raise Exception("Empty Response")
        self.last_request_id = data['requestId']
        if not data['success'] : raise MarketoException(data['errors'][0]) 
        return data['result']

    def get_email_templates(self, offset, maxreturn, status=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token,
            'offset' : offset,
            'maxreturn' : maxreturn
        }
        if status is not None:
            args['status'] = status
        data = HttpLib().get("https://" + self.host + "/rest/asset/v1/emailTemplates.json", args)
        if data is None: raise Exception("Empty Response")
        self.last_request_id = data['requestId']
        if not data['success'] : raise MarketoException(data['errors'][0]) 
        return data['result']
    
    def get_email_content_by_id(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        data = HttpLib().get("https://" + self.host + "/rest/asset/v1/email/" + str(id) + "/content", args)
        if data is None: raise Exception("Empty Response")
        self.last_request_id = data['requestId']
        if not data['success'] : raise MarketoException(data['errors'][0]) 
        return data['result']
    
    def get_email_template_content_by_id(self, id, status = None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        if status is not None:
            args['status'] = status
        data = HttpLib().get("https://" + self.host + "/rest/asset/v1/emailTemplate/" + str(id) + "/content", args)
        if data is None: raise Exception("Empty Response")
        self.last_request_id = data['requestId']
        if not data['success'] : raise MarketoException(data['errors'][0]) 
        return data['result']

    def get_leads_by_listId(self, listId = None , batchSize = None, fields = []):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        if len(fields) > 0:
            args['fields'] = ",".join(fields)
        if batchSize:
            args['batchSize'] = batchSize   
        result_list = []    
        while True:
            data = HttpLib().get("https://" + self.host + "/rest/v1/list/" + str(listId)+ "/leads.json", args)
            if data is None: raise Exception("Empty Response")
            self.last_request_id = data['requestId']
            if not data['success'] : raise MarketoException(data['errors'][0]) 
            result_list.extend(data['result'])
            if len(data['result']) == 0 or 'nextPageToken' not in data:
                break
            args['nextPageToken'] = data['nextPageToken']         
        return result_list    

    def get_multiple_leads_by_filter_type(self, filterType, filterValues, fields=None, nextPageToken=None):
        self.authenticate()
        data=[('filterValues',filterValues),('filterType',filterType)]
        if fields is not None:
            data.append(('fields',fields))
        args = {
            'access_token' : self.token,
            '_method' : 'GET'
        }
        if nextPageToken is not None:
            args['nextPageToken'] = nextPageToken
        result = HttpLib().post("https://" + self.host + "/rest/v1/leads.json",args,data,mode='nojsondumps')
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_activity_types(self):
        self.authenticate()
        args = {
            'access_token' : self.token 
        }
        data = HttpLib().get("https://" + self.host + "/rest/v1/activities/types.json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0]) 
        return data['result']

        
    def get_lead_activity_page(self, activityTypeIds, nextPageToken, batchSize = None, listId = None):
        self.authenticate()
        activityTypeIds = activityTypeIds.split() if type(activityTypeIds) is str else activityTypeIds
        args = {
            'access_token' : self.token,
            'activityTypeIds' : ",".join(activityTypeIds),
            'nextPageToken' : nextPageToken
        }
        if listId:
            args['listId'] = listId
        if batchSize:
            args['batchSize'] = batchSize
        data = HttpLib().get("https://" + self.host + "/rest/v1/activities.json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data

    def get_lead_activity(self, activityTypeIds, sinceDatetime, batchSize = None, listId = None):
        activity_result_list = []
        nextPageToken = self.get_paging_token(sinceDatetime = sinceDatetime)
        moreResult = True
        while moreResult:
            result = self.get_lead_activity_page(activityTypeIds, nextPageToken, batchSize, listId)
            if result is None:
                break
            moreResult = result['moreResult']
            nextPageToken = result['nextPageToken']
            if 'result' in result:
                activity_result_list.extend(result['result'])
       
        return activity_result_list         
           
    def get_paging_token(self, sinceDatetime):
        self.authenticate()
        args = {
            'access_token' : self.token, 
            'sinceDatetime' : sinceDatetime
        }
        data = HttpLib().get("https://" + self.host + "/rest/v1/activities/pagingtoken.json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data['nextPageToken']

    def update_lead(self, lookupField, lookupValue, values):
        updated_lead = dict(list({lookupField : lookupValue}.items()) + list(values.items()))
        data = {
            'action' : 'updateOnly',
            'lookupField' : lookupField,
            'input' : [
             updated_lead
            ]
        }
        return self.post(data)

    def create_lead(self, lookupField, lookupValue, values):
        new_lead = dict(list({lookupField : lookupValue}.items()) + list(values.items()))
        data = {
            'action' : 'createOnly',
            'lookupField' : lookupField,
            'input' : [
             new_lead
            ]
        }
        return self.post(data)

    def upsert_lead(self, lookupField, lookupValue, values):
        new_lead = dict(list({lookupField : lookupValue}.items()) + list(values.items()))
        data = {
            'action' : 'createOrUpdate',
            'lookupField' : lookupField,
            'input' : [
             new_lead
            ]
        }
        return self.post(data)

    def create_update_leads(self, leads, action='createOrUpdate', lookupField=None, asyncProcessing=None, partitionName=None):
        # expected format for 'leads': [{"email":"joe@example.com","firstName":"Joe"},{"email":"jill@example.com","firstName":"Jill"}]
        data = {
            'action' : action,
            'input' : leads
        }
        if lookupField is not None:
            data['lookupField'] = lookupField
        if asyncProcessing is not None:
            data['asyncProcessing '] = asyncProcessing
        if partitionName is not None:
            data['partitionName'] = partitionName
        return self.post(data)

    def post(self, data):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        data = HttpLib().post("https://" + self.host + "/rest/v1/leads.json" , args, data)
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data['result']

    def run_request_campaign(self, campaignID, leadsID, values):
        token_list = [{'name':'{{' + k + '}}', 'value':v} for k, v in values.items()]
        leads_list = [{'id':items} for items in leadsID]
        data={
          'input': {"leads":
                    leads_list,                  
                    "tokens":
                    token_list
                   }
             }
        
        self.authenticate()
        args = {
            'access_token' : self.token 
        }
        x="https://" + self.host + "/rest/v1/campaigns/" + str(campaignID)+ "/trigger.json"
        result = HttpLib().post("https://" + self.host + "/rest/v1/campaigns/" + str(campaignID)+ "/trigger.json", args, data)
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['success']

    def merge_leads(self, winning_ld, loosing_leads_list, mergeInCRM=False):
        leadstr = str(loosing_leads_list).strip('[]')
        leadsing = '&leadIds=' + leadstr
        self.authenticate()
        args = {
            'access_token' : self.token 
        }
        if len(loosing_leads_list) >  1:
            data={
                 'leadIds':leadstr
                 }
        else:
            data={
                 'leadld' : leadstr,
                 'mergeInCRM' : mergeInCRM
                 }
        data = None
        args = None
        headers = {'content-type': 'application/json'}
        urls = "https://" + self.host + "/rest/v1/leads/" + str(winning_ld) + "/merge.json?access_token=" + self.token + leadsing
        result = requests.post(urls, headers = headers)
        x = result.json()
        if result.status_code != 200:
            return False
        else:
            return x['success']

    def add_to_list(self, listId, leadIds):
        #currently only handles 300 Leads at a time; looping needs to be implemented outside
        self.authenticate()
        leads_list = [{'id':items} for items in leadIds]
        data={
            'input': leads_list
            }
        args = {
            'access_token' : self.token
            }
        result = HttpLib().post("https://" + self.host + "/rest/v1/lists/" + str(listId)+ "/leads.json", args, data)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result

    def remove_from_list(self, listId, leadIds):
        self.authenticate()
        leads_list = [{'id':items} for items in leadIds]
        data={
            'input': leads_list
            }
        args = {
            'access_token' : self.token
            }
        result = HttpLib().delete("https://" + self.host + "/rest/v1/lists/" + str(listId)+ "/leads.json", args, data)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result
       
    def browse_folders(self, root, offset=None, maxDepth=None, maxReturn=None, workSpace=None):
        # this does not loop, so for now limited to 200 folder; will implement looping in the future
        self.authenticate()
        if root is None: raise ValueError("Invalid argument: required argument root is none.")
        args = {
            'access_token' : self.token,
            'root' : root
        }
        if offset is not None:
            args['offset'] = offset
        if maxDepth is not None:
            args['maxDepth'] = maxDepth
        if maxReturn is not None:
            args['maxReturn'] = maxReturn
        if workSpace is not None:
            args['workSpace'] = workSpace
        result = HttpLib().get("https://" + self.host + "/rest/asset/v1/folders.json", args)
        if result is None: raise Exception("Empty Response")
        self.last_request_id = result['requestId']
        if not result['success'] : raise MarketoException(result['errors'][0])
        try:
            return result['result']
        except KeyError:
            return False

    def get_folder_by_id(self, id, type=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        if type is not None:
            args['type'] = type
        result = HttpLib().get("https://" + self.host + "/rest/asset/v1/folder/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        self.last_request_id = result['requestId']
        if not result['success'] : raise MarketoException(result['errors'][0])
        try:
            return result['result']
        except KeyError:
            return False

    def get_folder_by_name(self, name, type=None, root=None, workSpace=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        args = {
            'access_token' : self.token,
            'name' : name
        }
        if type is not None:
            args['type'] = type
        if root is not None:
            args['root'] = root
        if workSpace is not None:
            args['workSpace'] = workSpace
        result = HttpLib().get("https://" + self.host + "/rest/asset/v1/folder/byName.json", args)
        if result is None: raise Exception("Empty Response")
        self.last_request_id = result['requestId']
        if not result['success'] : raise MarketoException(result['errors'][0])
        try:
            return result['result']
        except KeyError:
            return False

    def create_folder(self, name, parent, description=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if parent is None: raise ValueError("Invalid argument: required argument parent is none.")
        args = {
            'access_token' : self.token,
            'name' : name,
            'parent' : parent
        }
        if description is not None:
            args['description'] = description
        result = HttpLib().post("https://" + self.host + "/rest/asset/v1/folders.json", args)
        if result is None: raise Exception("Empty Response")
        self.last_request_id = result['requestId']
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def create_get_folder(self, name, parent, description=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if parent is None: raise ValueError("Invalid argument: required argument parent is none.")
        args = {
            'access_token' : self.token,
            'name' : name,
            'parent' : parent
        }
        if description is not None:
            args['description'] = description
        result = HttpLib().post("https://" + self.host + "/rest/asset/v1/folders.json", args)
        if result is None: raise Exception("Empty Response")
        self.last_request_id = result['requestId']
        if not result['success']:
            if result['errors'][0]['code'] == "709":
                get_fldr = self.get_folder_by_name(name, type='Folder', root=parent)
                get_fldr[0]['status'] = 'existing'
            else:
                raise MarketoException(result['errors'][0])
            return get_fldr
        else:
            result['result'][0]['status'] = 'new'
            return result['result']

    def list_files(self, folder=None, offset=None, maxReturn=None):
        # this does not loop, so for now limited to 200 files; will implement looping in the future
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        if folder is not None:
            args['folder'] = folder
        if offset is not None:
            args['offset'] = offset
        if maxReturn is not None:
            args['maxReturn'] = maxReturn
        result = HttpLib().get("https://" + self.host + "/rest/asset/v1/files.json", args)
        if result is None: raise Exception("Empty Response")
        self.last_request_id = result['requestId']
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result

    def create_file(self, name, file, folder, description=None, insertOnly=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if file is None: raise ValueError("Invalid argument: required argument file is none.")
        if folder is None: raise ValueError("Invalid argument: required argument folder is none.")
        args = {
            'access_token' : self.token,
            'name' : name,
            'folder' : folder
        }
        if description is not None:
            args['description'] = description
        if insertOnly is not None:
            args['insertOnly'] = insertOnly
        result = HttpLib().post("https://" + self.host + "/rest/asset/v1/files.json", args, files=file)
        if result is None: raise Exception("Empty Response")
        self.last_request_id = result['requestId']
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result


    def associate_lead(self, id, cookie):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if cookie is None: raise ValueError("Invalid argument: required argument cookie is none.")
        args = {
            'access_token' : self.token,
            'id' : id,
            'cookie' : cookie
        }
        result = HttpLib().post("https://" + self.host + "/rest/v1/leads/" + str(id) + "associate.json", args)
        if result is None: raise Exception("Empty Response")
        self.last_request_id = result['requestId']
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_lead_partitions(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        data = HttpLib().get("https://" + self.host + "/rest/v1/leads/partitions.json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data['result']

    def get_list_by_id(self, id):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        data = HttpLib().get("https://" + self.host + "/rest/v1/lists/" + str(id) + ".json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data['result']

    def get_multiple_lists(self, id=None, name=None, programName=None, workspaceName=None, batchSize=None, nextPageToken=None):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        if id is not None:
            args['id'] = id
        if name is not None:
            args['name'] = name
        if programName is not None:
            args['programName'] = programName
        if workspaceName is not None:
            args['workspaceName'] = workspaceName
        if batchSize is not None:
            args['batchSize'] = batchSize
        if nextPageToken is not None:
            args['nextPageToken'] = nextPageToken
        result = HttpLib().get("https://" + self.host + "/rest/v1/lists.json", args)
        if result is None: raise Exception("Empty Response")
        self.last_request_id = result['requestId']
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def member_of_list(self, listId, id):
        # this uses POST so large numbers of leads can be specified
        self.authenticate()
        leads_list = [{'id':items} for items in id]
        data = {
            'input': leads_list
        }
        args = {
            'access_token' : self.token,
            '_method' : 'GET'
        }
        data = HttpLib().post("https://" + self.host + "/rest/v1/lists/" + str(listId) + "/leads/ismember.json", args, data)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data['result']

    def get_campaign_by_id(self, id):
        self.authenticate()
        args = {
            'access_token' : self.token,
            'id' : id
        }
        data = HttpLib().get("https://" + self.host + "/rest/v1/campaigns/" + str(id) + ".json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data['result']

    def get_multiple_campaigns(self, id=None, name=None, programName=None, workspaceName=None, batchSize=None, nextPageToken=None):
        self.authenticate()
        args = {
            'access_token' : self.token,
            '_method' : 'GET'
        }
        if id is not None:
            data = [('id',items) for items in id]
            #print(data)
        if name is not None:
            args['name'] = name
        if programName is not None:
            args['programName'] = programName
        if workspaceName is not None:
            args['workspaceName'] = workspaceName
        if batchSize is not None:
            args['batchSize'] = batchSize
        if nextPageToken is not None:
            args['nextPageToken'] = nextPageToken
        if id is not None:
            result = HttpLib().post("https://" + self.host + "/rest/v1/campaigns.json", args, data, mode='nojsondumps')
        else:
            result = HttpLib().post("https://" + self.host + "/rest/v1/campaigns.json", args)
        if result is None: raise Exception("Empty Response")
        self.last_request_id = result['requestId']
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def schedule_campaign(self, id, runAt=None, cloneToProgramName=None, tokens=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if runAt is not None or cloneToProgramName is not None or tokens is not None:
            data={
              'input': {}
                 }
        if runAt is not None:
            data['input']['runAt'] = runAt
            print(data)
        elif cloneToProgramName is not None:
            data['input']['cloneToProgramName'] = cloneToProgramName
        elif tokens is not None:
            token_list = [{'name':'{{' + k + '}}', 'value':v} for k, v in tokens.items()]
            print(token_list)
            data['input']['tokens'] = token_list
        args = {
            'access_token' : self.token
        }
        if runAt is not None or cloneToProgramName is not None or tokens is not None:
            result = HttpLib().post("https://" + self.host + "/rest/v1/campaigns/" + str(id)+ "/schedule.json", args, data)
        else:
            result = HttpLib().post("https://" + self.host + "/rest/v1/campaigns/" + str(id)+ "/schedule.json", args)
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['success']

    def request_campaign(self, id, leads, tokens=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if leads is None: raise ValueError("Invalid argument: required argument leads is none.")
        leads_list = [{'id':items} for items in leads]
        if tokens is not None:
            token_list = [{'name':'{{' + k + '}}', 'value':v} for k, v in tokens.items()]
            data={
              'input': {"leads":
                        leads_list,
                        "tokens":
                        token_list
                       }
                 }
        else:
            data={
              'input': {"leads":
                        leads_list
                       }
                 }
        args = {
            'access_token' : self.token
        }
        result = HttpLib().post("https://" + self.host + "/rest/v1/campaigns/" + str(id)+ "/trigger.json", args, data)
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['success']

    def import_lead(self, format, file, lookupField=None, listId=None, partitionName=None):
        self.authenticate()
        if format is None: raise ValueError("Invalid argument: required argument format is none.")
        if file is None: raise ValueError("Invalid argument: required argument file is none.")
        args = {
            'access_token' : self.token,
            'format' : format
        }
        if lookupField is not None:
            args['lookupField'] = lookupField
        if listId is not None:
            args['listId'] = listId
        if partitionName is not None:
            args['partitionName'] = partitionName
        result = HttpLib().post("https://" + self.host + "/bulk/v1/leads.json", args, files=file)
        if result is None: raise Exception("Empty Response")
        self.last_request_id = result['requestId']
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result

    def get_import_lead_status(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        data = HttpLib().get("https://" + self.host + "/bulk/v1/leads/batch/" + str(id) + ".json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data['result']

    def get_import_failure_file(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        data = HttpLib().get("https://" + self.host + "/bulk/v1/leads/batch/" + str(id) + "/failures.json", args, mode='nojson')
        if data is None: raise Exception("Empty Response")
        return data.text

    def get_import_warning_file(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        data = HttpLib().get("https://" + self.host + "/bulk/v1/leads/batch/" + str(id) + "/warnings.json", args, mode='nojson')
        if data is None: raise Exception("Empty Response")
        return data.text

    def describe(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        data = HttpLib().get("https://" + self.host + "/rest/v1/leads/describe.json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data['result']

    def get_lead_changes_page(self, fields, nextPageToken, batchSize = None, listId = None):
        self.authenticate()
        fields = fields.split() if type(fields) is str else fields
        args = {
            'access_token' : self.token,
            'fields' : ",".join(fields),
            'nextPageToken' : nextPageToken
        }
        if listId:
            args['listId'] = listId
        if batchSize:
            args['batchSize'] = batchSize
        data = HttpLib().get("https://" + self.host + "/rest/v1/activities/leadchanges.json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data

    def get_lead_changes(self, fields, sinceDatetime, batchSize = None, listId = None):
        if fields is None: raise ValueError("Invalid argument: required argument fields is none.")
        if sinceDatetime is None: raise ValueError("Invalid argument: required argument sinceDatetime is none.")
        activity_result_list = []
        nextPageToken = self.get_paging_token(sinceDatetime = sinceDatetime)
        moreResult = True
        while moreResult:
            result = self.get_lead_changes_page(fields, nextPageToken, batchSize, listId)
            if result is None:
                break
            moreResult = result['moreResult']
            nextPageToken = result['nextPageToken']
            if 'result' in result:
                activity_result_list.extend(result['result'])

        return activity_result_list

    def get_daily_usage(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        data = HttpLib().get("https://" + self.host + "/rest/v1/stats/usage.json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data['result']

    def get_last_7_days_usage(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        data = HttpLib().get("https://" + self.host + "/rest/v1/stats/usage/last7days.json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data['result']

    def get_daily_errors(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        data = HttpLib().get("https://" + self.host + "/rest/v1/stats/errors.json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data['result']

    def get_last_7_days_errors(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        data = HttpLib().get("https://" + self.host + "/rest/v1/stats/errors/last7days.json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data['result']

    def delete_lead(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        leads_list = [{'id':items} for items in id]
        data={
            'input': leads_list
            }
        args = {
            'access_token' : self.token
            }
        result = HttpLib().delete("https://" + self.host + "/rest/v1/leads.json", args, data)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result

    def get_deleted_leads_page(self, nextPageToken, batchSize = None):
        self.authenticate()
        args = {
            'access_token' : self.token,
            'nextPageToken' : nextPageToken
        }
        if batchSize:
            args['batchSize'] = batchSize
        data = HttpLib().get("https://" + self.host + "/rest/v1/activities/deletedleads.json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data

    def get_deleted_leads(self, sinceDatetime, batchSize = None):
        if sinceDatetime is None: raise ValueError("Invalid argument: required argument sinceDatetime is none.")
        deleted_leads_list = []
        nextPageToken = self.get_paging_token(sinceDatetime = sinceDatetime)
        moreResult = True
        while moreResult:
            result = self.get_deleted_leads_page(nextPageToken, batchSize)
            if result is None:
                break
            moreResult = result['moreResult']
            nextPageToken = result['nextPageToken']
            if 'result' in result:
                deleted_leads_list.extend(result['result'])

        return deleted_leads_list

    def update_leads_partition(self, idAndPartitionName):
        self.authenticate()
        if idAndPartitionName is None: raise ValueError("Invalid argument: required argument idAndPartitionName is none.")
        data={
          'input': []
             }
        for lead in idAndPartitionName:
            data['input'].append(lead)
        args = {
            'access_token' : self.token
        }
        result = HttpLib().post("https://" + self.host + "/rest/v1/leads/partitions.json", args, data)
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result

    def get_lead_by_id(self, id, fields=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        if fields is not None:
            args['fields'] = fields
        data = HttpLib().get("https://" + self.host + "/rest/v1/lead/" + str(id) + ".json", args)
        if data is None: raise Exception("Empty Response")
        if not data['success'] : raise MarketoException(data['errors'][0])
        return data['result']

    def get_multiple_leads_by_program_id(self, programId , batchSize = None, fields = []):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        if len(fields) > 0:
            args['fields'] = ",".join(fields)
        if batchSize:
            args['batchSize'] = batchSize
        result_list = []
        while True:
            data = HttpLib().get("https://" + self.host + "/rest/v1/leads/programs/" + str(programId)+ ".json", args)
            if data is None: raise Exception("Empty Response")
            self.last_request_id = data['requestId']
            if not data['success'] : raise MarketoException(data['errors'][0])
            result_list.extend(data['result'])
            if len(data['result']) == 0 or 'nextPageToken' not in data:
                break
            args['nextPageToken'] = data['nextPageToken']
        return result_list

