import time
from datetime import datetime
from marketorestpython.helper.http_lib import HttpLib
from marketorestpython.helper.exceptions import MarketoException


class MarketoClient:    
    host = None
    client_id = None
    client_secret = None
    token = None
    expires_in = None
    valid_until = None
    token_type = None
    scope = None
    last_request_id = None # intended to save last request id, but not used right now
    API_CALLS_MADE = 0
    API_LIMIT = None
    
    def __init__(self, munchkin_id, client_id, client_secret, api_limit=None):
        assert(munchkin_id is not None)
        assert(client_id is not None)
        assert(client_secret is not None)
        self.host = "https://" + munchkin_id + ".mktorest.com"
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
                    'get_lead_by_id': self.get_lead_by_id,
                    'get_multiple_leads_by_filter_type': self.get_multiple_leads_by_filter_type,
                    'get_multiple_leads_by_list_id': self.get_multiple_leads_by_list_id,
                    'get_multiple_leads_by_list_id_yield': self.get_multiple_leads_by_list_id_yield,
                    'get_multiple_leads_by_program_id': self.get_multiple_leads_by_program_id,
                    'change_lead_program_status': self.change_lead_program_status,
                    'create_update_leads': self.create_update_leads,
                    'associate_lead': self.associate_lead,
                    'merge_lead': self.merge_lead,
                    'get_lead_partitions': self.get_lead_partitions,
                    'get_list_by_id': self.get_list_by_id,
                    'get_multiple_lists': self.get_multiple_lists,
                    'add_leads_to_list': self.add_leads_to_list,
                    'remove_leads_from_list': self.remove_leads_from_list,
                    'member_of_list': self.member_of_list,
                    'get_campaign_by_id': self.get_campaign_by_id,
                    'get_multiple_campaigns': self.get_multiple_campaigns,
                    'schedule_campaign': self.schedule_campaign,
                    'request_campaign': self.request_campaign,
                    'import_lead': self.import_lead,
                    'get_import_lead_status': self.get_import_lead_status,
                    'get_import_failure_file': self.get_import_failure_file,
                    'get_import_warning_file': self.get_import_warning_file,
                    'describe': self.describe,
                    'get_activity_types': self.get_activity_types,
                    'get_paging_token': self.get_paging_token,
                    'get_lead_activities': self.get_lead_activities,
                    'get_lead_changes': self.get_lead_changes,
                    'add_custom_activities': self.add_custom_activities,
                    'get_daily_usage': self.get_daily_usage,
                    'get_last_7_days_usage': self.get_last_7_days_usage,
                    'get_daily_errors': self.get_daily_errors,
                    'get_last_7_days_errors': self.get_last_7_days_errors,
                    'delete_lead': self.delete_lead,
                    'get_deleted_leads': self.get_deleted_leads,
                    'update_leads_partition': self.update_leads_partition,
                    'create_folder': self.create_folder,
                    'get_folder_by_id': self.get_folder_by_id,
                    'get_folder_by_name': self.get_folder_by_name,
                    'get_folder_contents': self.get_folder_contents,
                    'update_folder': self.update_folder,
                    'delete_folder': self.delete_folder,
                    'browse_folders': self.browse_folders,
                    'create_token': self.create_token,
                    'get_tokens': self.get_tokens,
                    'delete_tokens': self.delete_tokens,
                    'create_email_template': self.create_email_template,
                    'get_email_template_by_id': self.get_email_template_by_id,
                    'get_email_template_by_name': self.get_email_template_by_name,
                    'update_email_template': self.update_email_template,
                    'delete_email_template': self.delete_email_template,
                    'get_email_templates': self.get_email_templates,
                    'get_email_template_content': self.get_email_template_content,
                    'update_email_template_content': self.update_email_template_content,
                    'approve_email_template': self.approve_email_template,
                    'unapprove_email_template': self.unapprove_email_template,
                    'discard_email_template_draft': self.discard_email_template_draft,
                    'clone_email_template': self.clone_email_template,
                    'create_email': self.create_email,
                    'get_email_by_id': self.get_email_by_id,
                    'get_email_by_name': self.get_email_by_name,
                    'delete_email': self.delete_email,
                    'update_email': self.update_email,
                    'get_emails': self.get_emails,
                    'get_email_content': self.get_email_content,
                    'update_email_content': self.update_email_content,
                    'update_email_content_in_editable_section': self.update_email_content_in_editable_section,
                    'get_email_dynamic_content': self.get_email_dynamic_content,
                    'update_email_dynamic_content': self.update_email_dynamic_content,
                    'approve_email': self.approve_email,
                    'unapprove_email': self.unapprove_email,
                    'discard_email_draft': self.discard_email_draft,
                    'clone_email': self.clone_email,
                    'send_sample_email': self.send_sample_email,
                    'create_landing_page': self.create_landing_page,
                    'get_landing_page_by_id': self.get_landing_page_by_id,
                    'get_landing_page_by_name': self.get_landing_page_by_name,
                    'delete_landing_page': self.delete_landing_page,
                    'update_landing_page': self.update_landing_page,
                    'get_landing_pages': self.get_landing_pages,
                    'get_landing_page_content': self.get_landing_page_content,
                    'create_landing_page_content_section': self.create_landing_page_content_section,
                    'update_landing_page_content_section': self.update_landing_page_content_section,
                    'delete_landing_page_content_section': self.delete_landing_page_content_section,
                    'get_landing_page_dynamic_content': self.get_landing_page_dynamic_content,
                    'update_landing_page_dynamic_content': self.update_landing_page_dynamic_content,
                    'approve_landing_page': self.approve_landing_page,
                    'unapprove_landing_page': self.unapprove_landing_page,
                    'discard_landing_page_draft': self.discard_landing_page_draft,
                    'clone_landing_page': self.clone_landing_page,
                    'create_form': self.create_form,
                    'get_form_by_id': self.get_form_by_id,
                    'get_form_by_name': self.get_form_by_name,
                    'delete_form': self.delete_form,
                    'update_form': self.update_form,
                    'get_forms': self.get_forms,
                    'get_form_fields': self.get_form_fields,
                    'create_form_field': self.create_form_field,
                    'update_form_field': self.update_form_field,
                    'delete_form_field': self.delete_form_field,
                    'approve_form': self.approve_form,
                    'unapprove_form': self.unapprove_form,
                    'discard_form_draft': self.discard_form_draft,
                    'clone_form': self.clone_form,
                    'create_file': self.create_file,
                    'get_file_by_id': self.get_file_by_id,
                    'get_file_by_name': self.get_file_by_name,
                    'list_files': self.list_files,
                    'update_file_content': self.update_file_content,
                    'create_snippet': self.create_snippet,
                    'get_snippet_by_id': self.get_snippet_by_id,
                    'delete_snippet': self.delete_snippet,
                    'update_snippet': self.update_snippet,
                    'get_snippets': self.get_snippets,
                    'get_snippet_content': self.get_snippet_content,
                    'update_snippet_content': self.update_snippet_content,
                    'approve_snippet': self.approve_snippet,
                    'unapprove_snippet': self.unapprove_snippet,
                    'discard_snippet_draft': self.discard_snippet_draft,
                    'clone_snippet': self.clone_snippet,
                    'update_snippet_dynamic_content': self.update_snippet_dynamic_content,
                    'get_snippet_dynamic_content': self.get_snippet_dynamic_content,
                    'get_segmentations': self.get_segmentations,
                    'get_segments': self.get_segments,
                    'create_landing_page_template': self.create_landing_page_template,
                    'get_landing_page_template_by_id': self.get_landing_page_template_by_id,
                    'get_landing_page_template_by_name': self.get_landing_page_template_by_name,
                    'get_landing_page_templates': self.get_landing_page_templates,
                    'get_landing_page_template_content': self.get_landing_page_template_content,
                    'update_landing_page_template_content': self.update_landing_page_template_content,
                    'update_landing_page_template': self.update_landing_page_template,
                    'delete_landing_page_template': self.delete_landing_page_template,
                    'approve_landing_page_template': self.approve_landing_page_template,
                    'unapprove_landing_page_template': self.unapprove_landing_page_template,
                    'discard_landing_page_template_draft': self.discard_landing_page_template_draft,
                    'clone_landing_page_template': self.clone_landing_page_template,
                    'create_program': self.create_program,
                    'get_program_by_id': self.get_program_by_id,
                    'get_program_by_name': self.get_program_by_name,
                    'get_program_by_tag_type': self.get_program_by_tag_type,
                    'update_program': self.update_program,
                    'delete_program': self.delete_program,
                    'browse_programs': self.browse_programs,
                    'clone_program': self.clone_program,
                    'approve_program': self.approve_program,
                    'unapprove_program': self.unapprove_program,
                    'get_channels': self.get_channels,
                    'get_channel_by_name': self.get_channel_by_name,
                    'get_tags': self.get_tags,
                    'get_tag_by_name': self.get_tag_by_name,
                    'get_list_of_custom_objects': self.get_list_of_custom_objects,
                    'describe_custom_object': self.describe_custom_object,
                    'create_update_custom_objects': self.create_update_custom_objects,
                    'delete_custom_objects': self.delete_custom_objects,
                    'get_custom_objects': self.get_custom_objects,
                    'describe_opportunity': self.describe_opportunity,
                    'create_update_opportunities': self.create_update_opportunities,
                    'delete_opportunities': self.delete_opportunities,
                    'get_opportunities': self.get_opportunities,
                    'describe_opportunity_role': self.describe_opportunity_role,
                    'create_update_opportunities_roles': self.create_update_opportunities_roles,
                    'delete_opportunity_roles': self.delete_opportunity_roles,
                    'get_opportunity_roles': self.get_opportunity_roles,
                    'describe_company': self.describe_company,
                    'create_update_companies': self.create_update_companies,
                    'delete_companies': self.delete_companies,
                    'get_companies': self.get_companies,
                    'describe_sales_person': self.describe_sales_person,
                    'create_update_sales_persons': self.create_update_sales_persons,
                    'delete_sales_persons': self.delete_sales_persons,
                    'get_sales_persons': self.get_sales_persons
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
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        data = HttpLib().get(self.host + "/identity/oauth/token", args)
        if data is None: raise Exception("Empty Response")
        if 'error' in data:
            if data['error'] in ['unauthorized', 'invalid_client']:
                raise Exception(data['error_description'])
        self.token = data['access_token']
        self.token_type = data['token_type']
        self.expires_in = data['expires_in']
        self.valid_until = time.time() + data['expires_in'] 
        self.scope = data['scope']

    # --------- LEADS ---------

    def get_lead_by_id(self, id, fields=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if fields is not None:
            args['fields'] = fields
        result = HttpLib().get(self.host + "/rest/v1/lead/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_multiple_leads_by_filter_type(self, filterType, filterValues, fields=None, batchSize=None):
        self.authenticate()
        if filterType is None: raise ValueError("Invalid argument: required argument filterType is none.")
        if filterValues is None: raise ValueError("Invalid argument: required argument filter_values is none.")
        filterValues = filterValues.split() if type(filterValues) is str else filterValues
        data=[('filterValues',(',').join(filterValues)), ('filterType', filterType)]
        if fields is not None:
            data.append(('fields',fields))
        if batchSize is not None:
            data.append(('batchSize',batchSize))
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        result_list = []
        while True:
            result = HttpLib().post(self.host + "/rest/v1/leads.json", args, data, mode='nojsondumps')
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def get_multiple_leads_by_list_id(self, listId, fields=None, batchSize=None):
        self.authenticate()
        if listId is None: raise ValueError("Invalid argument: required argument listId is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        data = []
        if fields is not None:
            data.append(('fields',fields))
        if batchSize is not None:
            data.append(('batchSize',batchSize))
        result_list = []
        while True:
            result = HttpLib().post(self.host + "/rest/v1/list/" + str(listId)+ "/leads.json", args, data, mode='nojsondumps')
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def get_multiple_leads_by_list_id_yield(self, listId, fields=None, batchSize=None, chunksize=-1):
        self.authenticate()
        if listId is None: raise ValueError("Invalid argument: required argument listId is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        data = []
        if fields is not None:
            data.append(('fields',fields))
        if batchSize is not None:
            data.append(('batchSize',batchSize))
        result_list = []
        count = 0
        while True:
            result = HttpLib().post(self.host + "/rest/v1/list/" + str(listId)+ "/leads.json", args, data, mode='nojsondumps')
            if result is None: raise Exception("Empty Response")
            if not result['success']: raise MarketoException(result['errors'][0])
            result_list.extend(result['result'])
            count += len(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                if result_list:
                    yield result_list  # yield remaining records at the end (or all records with chunk size -1)
                break
            args['nextPageToken'] = result['nextPageToken']
            if count >= chunksize != -1:  # yield when enough records to meet the chunk size; never yield here on -1
                yield result_list
                del result_list[:]
                count = 0

    def get_multiple_leads_by_program_id(self, programId, fields=None, batchSize=None):
        self.authenticate()
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        data = []
        if fields is not None:
            data.append(('fields',fields))
        if batchSize is not None:
            data.append(('batchSize',batchSize))
        result_list = []
        while True:
            result = HttpLib().post(self.host + "/rest/v1/leads/programs/" + str(programId)+ ".json", args, data, mode='nojsondumps')
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def change_lead_program_status(self, id, leadIds, status):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if leadIds is None: raise ValueError("Invalid argument: required argument input is none.")
        if status is None: raise ValueError("Invalid argument: required argument status is none.")
        args = {
            'access_token' : self.token
        }
        data={
            'status': status,
            'input': []
             }
        for leadId in leadIds:
            data['input'].append({'id': leadId})
        #result={}
        #result['success'] = True
        #result['result'] = data
        result = HttpLib().post(self.host + "/rest/v1/leads/programs/" + str(id) + "/status.json", args, data)
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def create_update_leads(self, leads, action=None, lookupField=None, asyncProcessing=None, partitionName=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        data = {
            'input': leads
        }
        if action is not None:
            data['action'] = action
        if lookupField is not None:
            data['lookupField'] = lookupField
        if asyncProcessing is not None:
            data['asyncProcessing '] = asyncProcessing
        if partitionName is not None:
            data['partitionName'] = partitionName
        result = HttpLib().post(self.host + "/rest/v1/leads.json", args, data)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def associate_lead(self, id, cookie):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if cookie is None: raise ValueError("Invalid argument: required argument cookie is none.")
        args = {
            'access_token': self.token,
            'id': id,
            'cookie': cookie
        }
        result = HttpLib().post(self.host + "/rest/v1/leads/" + str(id) + "/associate.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['success'] # there is no 'result' node returned in this call

    def merge_lead(self, id, leadIds, mergeInCRM=False):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if leadIds is None: raise ValueError("Invalid argument: required argument leadIds is none.")
        leadstr = ','.join(map(str, leadIds))
        args = {
            'access_token': self.token,
            'leadIds': leadstr,
            'mergeInCRM': mergeInCRM
        }
        result = HttpLib().post(self.host + "/rest/v1/leads/" + str(id) + "/merge.json", args, mode='merge_lead')
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['success'] # there is no 'result' node returned in this call

    # --------- LEAD PARTITIONS ---------

    def get_lead_partitions(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/rest/v1/leads/partitions.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    # --------- LISTS ---------

    def get_list_by_id(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/rest/v1/lists/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_multiple_lists(self, id=None, name=None, programName=None, workspaceName=None, batchSize=None):
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
        result_list = []
        while True:
            result = HttpLib().get(self.host + "/rest/v1/lists.json", args)
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def add_leads_to_list(self, listId, id):
        self.authenticate()
        if listId is None: raise ValueError("Invalid argument: required argument listId is none.")
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        leads_list = [{'id':items} for items in id]
        data={
            'input': leads_list
            }
        args = {
            'access_token' : self.token
            }
        result = HttpLib().post(self.host + "/rest/v1/lists/" + str(listId)+ "/leads.json", args, data)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def remove_leads_from_list(self, listId, id):
        self.authenticate()
        if listId is None: raise ValueError("Invalid argument: required argument listId is none.")
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        leads_list = [{'id':items} for items in id]
        data={
            'input': leads_list
            }
        args = {
            'access_token' : self.token
            }
        result = HttpLib().delete(self.host + "/rest/v1/lists/" + str(listId)+ "/leads.json", args, data)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def member_of_list(self, listId, id):
        self.authenticate()
        if listId is None: raise ValueError("Invalid argument: required argument listId is none.")
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        leads_list = [{'id':items} for items in id]
        data = {
            'input': leads_list
        }
        args = {
            'access_token' : self.token,
            '_method' : 'GET'
        }
        result = HttpLib().post(self.host + "/rest/v1/lists/" + str(listId) + "/leads/ismember.json", args, data)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    # --------- CAMPAIGNS ---------

    def get_campaign_by_id(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token,
            'id' : id
        }
        result = HttpLib().get(self.host + "/rest/v1/campaigns/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_multiple_campaigns(self, id=None, name=None, programName=None, workspaceName=None, batchSize=None):
        self.authenticate()
        args = {
            'access_token' : self.token,
            '_method' : 'GET'
        }
        if id is not None:
            data = [('id',items) for items in id]
        else:
            data = None
        if name is not None:
            args['name'] = name
        if programName is not None:
            args['programName'] = programName
        if workspaceName is not None:
            args['workspaceName'] = workspaceName
        if batchSize is not None:
            args['batchSize'] = batchSize
        result_list = []
        while True:
            result = HttpLib().post(self.host + "/rest/v1/campaigns.json", args, data, mode='nojsondumps')
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def schedule_campaign(self, id, runAt=None, cloneToProgramName=None, tokens=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        if runAt is not None or cloneToProgramName is not None or tokens is not None:
            data = {
              'input': {}
                   }
        else:
            data = None
        if runAt is not None:
            data['input']['runAt'] = runAt
        if cloneToProgramName is not None:
            data['input']['cloneToProgramName'] = cloneToProgramName
        if tokens is not None:
            token_list = [{'name':'{{' + k + '}}', 'value':v} for k, v in tokens.items()]
            data['input']['tokens'] = token_list
        result = HttpLib().post(self.host + "/rest/v1/campaigns/" + str(id)+ "/schedule.json", args, data)
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['success']

    def request_campaign(self, id, leads, tokens=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if leads is None: raise ValueError("Invalid argument: required argument leads is none.")
        args = {
            'access_token' : self.token
        }
        leads_list = [{'id':items} for items in leads]
        if tokens is not None:
            token_list = [{'name':'{{' + k + '}}', 'value':v} for k, v in tokens.items()]
            data={
              'input': {'leads':
                        leads_list,
                        'tokens':
                        token_list
                       }
                 }
        else:
            data={
              'input': {'leads':
                        leads_list
                       }
                 }
        result = HttpLib().post(self.host + "/rest/v1/campaigns/" + str(id)+ "/trigger.json", args, data)
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['success']

    # --------- IMPORT LEADS ---------

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
        result = HttpLib().post(self.host + "/bulk/v1/leads.json", args, files=file, filename="file")
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_import_lead_status(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/bulk/v1/leads/batch/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_import_failure_file(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/bulk/v1/leads/batch/" + str(id) + "/failures.json", args, mode='nojson')
        if result is None: raise Exception("Empty Response")
        return result.text

    def get_import_warning_file(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/bulk/v1/leads/batch/" + str(id) + "/warnings.json", args, mode='nojson')
        if result is None: raise Exception("Empty Response")
        return result.text

    # --------- DESCRIBE ---------

    def describe(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/rest/v1/leads/describe.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    # --------- ACTIVITIES ---------

    def get_activity_types(self):
        self.authenticate()
        args = {
            'access_token' : self.token 
        }
        result = HttpLib().get(self.host + "/rest/v1/activities/types.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']
        
    def get_paging_token(self, sinceDatetime):
        self.authenticate()
        args = {
            'access_token' : self.token,
            'sinceDatetime' : sinceDatetime
        }
        result = HttpLib().get(self.host + "/rest/v1/activities/pagingtoken.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['nextPageToken']

    def process_lead_activity_until_datetime(self, result, untilDatetime):
        latest_until_date = result[len(result)-1]['activityDate']
        result_until = datetime.strptime(latest_until_date, '%Y-%m-%dT%H:%M:%SZ')
        try:
            specified_until = datetime.strptime(untilDatetime, '%Y-%m-%dT%H:%M:%S')
        except:
            try:
                specified_until = datetime.strptime(untilDatetime, '%Y-%m-%d')
            except:
                raise('incorrect format for untilDatetime, use YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD')
        if result_until > specified_until:
            partial_result = []
            for record in result:
                if datetime.strptime(record['activityDate'], '%Y-%m-%dT%H:%M:%SZ') <= specified_until:
                    partial_result.append(record)
            return partial_result
        return result

    def get_lead_activities(self, activityTypeIds, nextPageToken=None, sinceDatetime=None, untilDatetime=None,
                            batchSize = None, listId = None, leadIds=None):
        self.authenticate()
        if activityTypeIds is None: raise ValueError("Invalid argument: required argument activityTypeIds is none.")
        if nextPageToken is None and sinceDatetime is None: raise ValueError("Either nextPageToken or sinceDatetime needs to be specified.")
        activityTypeIds = activityTypeIds.split() if type(activityTypeIds) is str else activityTypeIds
        args = {
            'access_token': self.token,
            'activityTypeIds': ",".join(activityTypeIds),
        }
        if listId is not None:
            args['listId'] = listId
        if leadIds is not None:
            args['leadIds'] = leadIds
        if batchSize is not None:
            args['batchSize'] = batchSize
        if nextPageToken is None:
            nextPageToken = self.get_paging_token(sinceDatetime=sinceDatetime)
        args['nextPageToken'] = nextPageToken
        result_list = []
        while True:
            result = HttpLib().get(self.host + "/rest/v1/activities.json", args)
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            if 'result' in result:
                if untilDatetime is not None:
                    new_result = self.process_lead_activity_until_datetime(result['result'], untilDatetime)
                    result_list.extend(new_result)
                else:
                    result_list.extend(result['result'])
            if result['moreResult'] is False:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def get_lead_changes(self, fields, nextPageToken=None, sinceDatetime=None, batchSize=None, listId=None):
        self.authenticate()
        if fields is None: raise ValueError("Invalid argument: required argument fields is none.")
        if nextPageToken is None and sinceDatetime is None: raise ValueError("Either nextPageToken or sinceDatetime needs to be specified.")
        fields = fields.split() if type(fields) is str else fields
        args = {
            'access_token' : self.token,
            'fields' : ",".join(fields),
        }
        if listId is not None:
            args['listId'] = listId
        if batchSize is not None:
            args['batchSize'] = batchSize
        if nextPageToken is None:
            nextPageToken = self.get_paging_token(sinceDatetime=sinceDatetime)
        args['nextPageToken'] = nextPageToken
        result_list = []
        while True:
            result = HttpLib().get(self.host + "/rest/v1/activities/leadchanges.json", args)
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            if 'result' in result:
                result_list.extend(result['result'])
            if result['moreResult'] is False:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def add_custom_activities(self, input):
        self.authenticate()
        if input is None: raise ValueError("Invalid argument: required argument input is none.")
        args = {
            'access_token' : self.token
        }
        data = {
            "input": input
        }
        result = HttpLib().post(self.host + "/rest/v1/activities/external.json", args, data)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    # --------- USAGE ---------

    def get_daily_usage(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/rest/v1/stats/usage.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_last_7_days_usage(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/rest/v1/stats/usage/last7days.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_daily_errors(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/rest/v1/stats/errors.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_last_7_days_errors(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/rest/v1/stats/errors/last7days.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    # --------- VARIOUS ---------

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
        result = HttpLib().delete(self.host + "/rest/v1/leads.json", args, data)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_deleted_leads(self, nextPageToken=None, sinceDatetime=None, batchSize = None):
        self.authenticate()
        if nextPageToken is None and sinceDatetime is None: raise ValueError("Either nextPageToken or sinceDatetime needs to be specified.")
        args = {
            'access_token' : self.token
        }
        if batchSize is not None:
            args['batchSize'] = batchSize
        if nextPageToken is None:
            nextPageToken = self.get_paging_token(sinceDatetime=sinceDatetime)
        args['nextPageToken'] = nextPageToken
        result_list = []
        while True:
            result = HttpLib().get(self.host + "/rest/v1/activities/deletedleads.json", args)
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            if 'result' in result:
                result_list.extend(result['result'])
            if result['moreResult'] is False:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def update_leads_partition(self, input):
        self.authenticate()
        if input is None: raise ValueError("Invalid argument: required argument input is none.")
        args = {
            'access_token' : self.token
        }
        data={
          'input': []
             }
        for lead in input:
            data['input'].append(lead)
        result = HttpLib().post(self.host + "/rest/v1/leads/partitions.json", args, data)
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    # --------- FOLDERS ---------

    def create_folder(self, name, parentId, parentType, description=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if parentId is None: raise ValueError("Invalid argument: required argument parentId is none.")
        if parentType is None: raise ValueError("Invalid argument: parentType should be 'Folder' or 'Parent'")
        args = {
            'access_token': self.token,
            'name': name,
            'parent': "{'id': " + str(parentId) + ", 'type': " + parentType + "}"
        }
        if description is not None:
            args['description'] = description
        result = HttpLib().post(self.host + "/rest/asset/v1/folders.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_folder_by_id(self, id, type):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if type is None: raise ValueError("Invalid argument: required argument type is none.")
        args = {
            'access_token': self.token,
            'type': type
        }
        result = HttpLib().get(self.host + "/rest/asset/v1/folder/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

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
        result = HttpLib().get(self.host + "/rest/asset/v1/folder/byName.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_folder_contents(self, id, type, maxReturn=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if type is None: raise ValueError("Invalid argument: required argument type is none.")
        args = {
            'access_token': self.token,
            'type': type
        }
        if maxReturn is not None:
            args['maxReturn'] = maxReturn
        else:
            maxReturn = 20
        result_list = []
        offset = 0
        while True:
            result = HttpLib().get(self.host + "/rest/asset/v1/folder/" + str(id) + "/content.json", args)
            if result is None: raise Exception("Empty Response")
            if not result['success']: raise MarketoException(result['errors'][0])
            if 'result' in result:
                if len(result['result']) < maxReturn:
                    result_list.extend(result['result'])
                    break
            else:
                break
            result_list.extend(result['result'])
            offset += maxReturn
            args['offset'] = offset
        return result_list

    def update_folder(self, id, description=None, name=None, isArchive=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token,
            'type': 'Folder'
        }
        if description is not None:
            args['description'] = description
        if name is not None:
            args['name'] = name
        if isArchive is not None:
            args['isArchive'] = isArchive
        result = HttpLib().post(self.host + "/rest/asset/v1/folder/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def delete_folder(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token,
            'type': 'Folder'
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/folder/" + str(id) + "/delete.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def browse_folders(self, root, maxDepth=None, maxReturn=None, workSpace=None):
        self.authenticate()
        if root is None: raise ValueError("Invalid argument: required argument root is none.")
        args = {
            'access_token' : self.token,
            'root' : root
        }
        if maxDepth is not None:
            args['maxDepth'] = maxDepth
        if maxReturn is not None:
            args['maxReturn'] = maxReturn
        else:
            maxReturn = 20
        if workSpace is not None:
            args['workSpace'] = workSpace
        result_list = []
        offset = 0
        while True:
            result = HttpLib().get(self.host + "/rest/asset/v1/folders.json", args)
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            if 'result' in result:
                if len(result['result']) < maxReturn:
                    result_list.extend(result['result'])
                    break
            else:
                break
            result_list.extend(result['result'])
            offset += maxReturn
            args['offset'] = offset
        return result_list

    # --------- TOKENS ---------

    def create_token(self, id, folderType, type, name, value):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if folderType is None: raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'.")
        if type is None: raise ValueError("Invalid argument: required argument type is none.")
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if value is None: raise ValueError("Invalid argument: required argument value is none.")
        args = {
            'access_token': self.token,
            'folderType': folderType,
            'type': type,
            'name': name,
            'value': value
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/folder/" + str(id) + "/tokens.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_tokens(self, id, folderType):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if folderType is None: raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'folderType': folderType
        }
        result = HttpLib().get(self.host + "/rest/asset/v1/folder/" + str(id) + "/tokens.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def delete_tokens(self, id, folderType, name, type):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if folderType is None: raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'.")
        if type is None: raise ValueError("Invalid argument: required argument type is none.")
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'folderType': folderType,
            'name': name,
            'type': type
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/folder/" + str(id) + "/tokens/delete.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    # --------- EMAIL TEMPLATES ---------

    def create_email_template(self, name, folderId, folderType, content, description=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if folderId is None: raise ValueError("Invalid argument: required argument folder is none.")
        if folderType is None: raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'.")
        if content is None: raise ValueError("Invalid argument: required argument content is none.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description is not None:
            args['description'] = description
        result = HttpLib().post(self.host + "/rest/asset/v1/emailTemplates.json", args, files=content, filename="content")
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_email_template_by_id(self, id, status=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/emailTemplate/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_email_template_by_name(self, name, status=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/emailTemplate/byName.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def update_email_template(self, id, name=None, description=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if name is not None:
            args['name'] = name
        if description is not None:
            args['description'] = description
        result = HttpLib().post(self.host + "/rest/asset/v1/emailTemplate/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def delete_email_template(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/emailTemplate/" + str(id) + "/delete.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_email_templates(self, maxReturn=None, status=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if maxReturn is not None:
            args['maxReturn'] = maxReturn
        else:
            maxReturn = 20
        if status is not None:
            args['status'] = status
        result_list = []
        offset = 0
        while True:
            result = HttpLib().get(self.host + "/rest/asset/v1/emailTemplates.json", args)
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            if 'result' in result:
                if len(result['result']) < maxReturn:
                    result_list.extend(result['result'])
                    break
            else:
                break
            result_list.extend(result['result'])
            offset += maxReturn
            args['offset'] = offset
        return result_list

    def get_email_template_content(self, id, status=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/emailTemplate/" + str(id) + "/content", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def update_email_template_content(self, id, content):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if content is None: raise ValueError("Invalid argument: required argument content is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/emailTemplate/" + str(id) + "/content.json", args,
                                files=content, filename="content")
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def approve_email_template(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/emailTemplate/" + str(id) + "/approveDraft.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def unapprove_email_template(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/emailTemplate/" + str(id) + "/unapprove.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def discard_email_template_draft(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/emailTemplate/" + str(id) + "/discardDraft.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def clone_email_template(self, id, name, folderId, folderType):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if folderId is None: raise ValueError("Invalid argument: required argument folder is none.")
        if folderType is None: raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/emailTemplate/" + str(id) + "/clone.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    # --------- EMAILS ---------

    def create_email(self, name, folderId, folderType, template, description=None, subject=None, fromName=None,
                     fromEmail=None, replyEmail=None, operational=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if folderId is None: raise ValueError("Invalid argument: required argument folder is none.")
        if folderType is None: raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'.")
        if template is None: raise ValueError("Invalid argument: required argument template is none.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}",
            'template': template
        }
        if description is not None:
            args['description'] = description
        if subject is not None:
            args['subject'] = subject
        if fromName is not None:
            args['fromName'] = fromName
        if fromEmail is not None:
            args['fromEmail'] = fromEmail
        if replyEmail is not None:
            args['replyEmail'] = replyEmail
        if operational is not None:
            args['operational'] = operational
        result = HttpLib().post(self.host + "/rest/asset/v1/emails.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_email_by_id(self, id, status=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/email/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_email_by_name(self, name, status=None, folderId=None, folderType=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        if status is not None:
            args['status'] = status
        if folderId is not None:
            args['folder'] = "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        result = HttpLib().get(self.host + "/rest/asset/v1/email/byName.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def delete_email(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/email/" + str(id) + "/delete.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def update_email(self, id, name=None, description=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if name is not None:
            args['name'] = name
        if description is not None:
            args['description'] = description
        result = HttpLib().post(self.host + "/rest/asset/v1/email/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_emails(self, maxReturn=None, status=None, folderId=None, folderType=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if maxReturn is not None:
            args['maxReturn'] = maxReturn
        else:
            maxReturn = 20
        if status is not None:
            args['status'] = status
        if folderId is not None:
            args['folder'] = "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        result_list = []
        offset = 0
        while True:
            result = HttpLib().get(self.host + "/rest/asset/v1/emails.json", args)
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            if 'result' in result:
                if len(result['result']) < maxReturn:
                    result_list.extend(result['result'])
                    break
            else:
                break
            result_list.extend(result['result'])
            offset += maxReturn
            args['offset'] = offset
        return result_list

    def get_email_content(self, id, status=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/email/" + str(id) + "/content.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def update_email_content(self, id, type, subject=None, fromName=None, fromEmail=None, replyTo=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if type is not "Text" and type is not "DynamicContent": raise ValueError("Invalid argument: type should be "
                                                                                 "'Text' or 'DynamicContent'.")
        args = {
            'access_token': self.token
        }
        if subject is not None:
            args['subject'] = '{"type":"' + type + '","value":"' + subject + '"}'
        if fromName is not None:
            args['fromName'] = '{"type":"' + type + '","value":"' + fromName + '"}'
        if fromEmail is not None:
            args['fromEmail'] = '{"type":"' + type + '","value":"' + fromEmail + '"}'
        if replyTo is not None:
            args['replyTO'] = '{"type":"' + type + '","value":"' + replyTo + '"}'
        result = HttpLib().post(self.host + "/rest/asset/v1/email/" + str(id) + "/content.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def update_email_content_in_editable_section(self, id, htmlId, type, value, textValue=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if htmlId is None: raise ValueError("Invalid argument: required argument htmlId is none.")
        if type is not "Text" and type is not "DynamicContent" and type is not "Snippet": raise ValueError(
                "Invalid argument: type should be 'Text', 'DynamicContent' or 'Snippet'.")
        if value is None: raise ValueError("Invalid argument: required argument value is none.")
        args = {
            'access_token': self.token
        }
        if isinstance(value, str):
            value = value.encode('ascii', 'xmlcharrefreplace')
        data = {
            'type': type,
            'value': value
        }
        if textValue is not None:
            data['textValue'] = textValue
        result = HttpLib().post(self.host + "/rest/asset/v1/email/" + str(id) + "/content/" + str(htmlId) +
                                ".json", args, data, mode='nojsondumps')
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_email_dynamic_content(self, id, dynamicContentId, status):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if dynamicContentId is None: raise ValueError("Invalid argument: required argument dynamicContentId is none.")
        args = {
            'access_token' : self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/email/" + str(id) + "/dynamicContent/" +
                               str(dynamicContentId) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def update_email_dynamic_content(self, id, dynamicContentId, segment, value, type):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if dynamicContentId is None: raise ValueError("Invalid argument: required argument dynamicContentId is none.")
        if segment is None: raise ValueError("Invalid argument: required argument segment is none.")
        if value is None: raise ValueError("Invalid argument: required argument value is none.")
        if type is None: raise ValueError("Invalid argument: required argument type is none.")
        args = {
            'access_token' : self.token
        }
        if isinstance(value, str):
            value = value.encode('ascii', 'xmlcharrefreplace')
        data = {
            'segment': segment,
            'value': value,
            'type': type
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/email/" + str(id) + "/dynamicContent/" +
                               str(dynamicContentId) + ".json", args, data, mode='nojsondumps')
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def approve_email(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/email/" + str(id) + "/approveDraft.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def unapprove_email(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/email/" + str(id) + "/unapprove.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def discard_email_draft(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/email/" + str(id) + "/discardDraft.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def clone_email(self, id, name, folderId, folderType, description=None, operational=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if folderId is None: raise ValueError("Invalid argument: required argument folder is none.")
        if folderType is None: raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description is not None:
            args['description'] = description
        if operational is not None:
            args['operational'] = operational
        result = HttpLib().post(self.host + "/rest/asset/v1/email/" + str(id) + "/clone.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def send_sample_email(self, id, emailAddress, textOnly=None, leadId=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if emailAddress is None: raise ValueError("Invalid argument: required argument emailAddress is none.")
        args = {
            'access_token': self.token,
            'emailAddress': emailAddress
        }
        if textOnly is not None:
            args['textOnly'] = textOnly
        if leadId is not None:
            args['leadId'] = leadId
        result = HttpLib().post(self.host + "/rest/asset/v1/email/" + str(id) + "/sendSample.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    # -------LANDING PAGES ---------#

    def create_landing_page(self, name, folderId, folderType, template, description=None, title=None, keywords=None,
                         robots=None, customHeadHTML=None, facebookOgTags=None, prefillForm=None, mobileEnabled=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if folderId is None: raise ValueError("Invalid argument: required argument folder is none.")
        if folderType is None: raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'.")
        if template is None: raise ValueError("Invalid argument: required argument template is none.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}",
            'template': template
        }
        if description is not None:
            args['description'] = description
        if title is not None:
            args['title'] = title
        if keywords is not None:
            args['keywords'] = keywords
        if robots is not None:
            args['robots'] = robots
        if customHeadHTML is not None:
            args['customHeadHTML'] = customHeadHTML
        if facebookOgTags is not None:
            args['facebookOgTags'] = facebookOgTags
        if prefillForm is not None:
            args['prefillForm'] = prefillForm
        if mobileEnabled is not None:
            args['mobileEnabled'] = mobileEnabled
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPages.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_landing_page_by_id(self, id, status=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/landingPage/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_landing_page_by_name(self, name, status=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/landingPage/byName.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def delete_landing_page(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPage/" + str(id) + "/delete.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def update_landing_page(self, id, name=None, description=None, title=None, keywords=None,
                            robots=None, customHeadHTML=None, facebookOgTags=None, prefillForm=None, mobileEnabled=None,
                            styleOverRide=None, urlPageName=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if name is not None:
            args['name'] = name
        if description is not None:
            args['description'] = description
        if title is not None:
            args['title'] = title
        if keywords is not None:
            args['keywords'] = keywords
        if robots is not None:
            args['robots'] = robots
        if customHeadHTML is not None:
            args['customHeadHTML'] = customHeadHTML
        if facebookOgTags is not None:
            args['facebookOgTags'] = facebookOgTags
        if prefillForm is not None:
            args['prefillForm'] = prefillForm
        if mobileEnabled is not None:
            args['mobileEnabled'] = mobileEnabled
        if styleOverRide is not None:
            args['styleOverRide'] = styleOverRide
        if urlPageName is not None:
            args['urlPageName'] = urlPageName
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPage/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_landing_pages(self, maxReturn=None, status=None, folderId=None, folderType=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if maxReturn is not None:
            args['maxReturn'] = maxReturn
        else:
            maxReturn = 20
        if status is not None:
            args['status'] = status
        if folderId is not None:
            args['folder'] = "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        result_list = []
        offset = 0
        while True:
            result = HttpLib().get(self.host + "/rest/asset/v1/landingPages.json", args)
            if result is None: raise Exception("Empty Response")
            #if not result['success']: raise MarketoException(result['errors'][0] + ". Request ID: " + result['requestId'])
            if not result['success']: raise MarketoException(result['errors'][0])
            if 'result' in result:
                if len(result['result']) < maxReturn:
                    result_list.extend(result['result'])
                    break
            else:
                break
            result_list.extend(result['result'])
            offset += maxReturn
            args['offset'] = offset
        return result_list

    def get_landing_page_content(self, id, status=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/landingPage/" + str(id) + "/content.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def create_landing_page_content_section(self, id, type, value, backgroundColor=None, borderColor=None,
                                            borderStyle=None, borderWidth=None, height=None, layer=None, left=None,
                                            opacity=None, top=None, width=None, hideDesktop=None, hideMobile=None,
                                            contentId=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if type is None: raise ValueError("Invalid argument: required argument type is none.")
        if value is None: raise ValueError("Invalid argument: required argument value is none.")
        args = {
            'access_token': self.token
        }
        if isinstance(value, str):
            value = value.encode('ascii', 'xmlcharrefreplace')
        data = {
            'type': type,
            'value': value
        }
        if backgroundColor is not None:
            data['backgroundColor'] = backgroundColor
        if borderColor is not None:
            data['borderColor'] = borderColor
        if borderStyle is not None:
            data['borderStyle'] = borderStyle
        if borderWidth is not None:
            data['borderWidth'] = borderWidth
        if height is not None:
            data['height'] = height
        if layer is not None:
            data['layer'] = layer
        if left is not None:
            data['left'] = left
        if opacity is not None:
            data['opacity'] = opacity
        if top is not None:
            data['top'] = top
        if width is not None:
            data['width'] = width
        if hideDesktop is not None:
            data['hideDesktop'] = hideDesktop
        if hideMobile is not None:
            data['hideMobile'] = hideMobile
        if contentId is not None:
            data['contentId'] = contentId
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPage/" + str(id) + "/content.json", args,
                                data, mode='nojsondumps')
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def update_landing_page_content_section(self, id, contentId, type, value, index=None, backgroundColor=None,
                                            borderColor=None, borderStyle=None, borderWidth=None, height=None,
                                            layer=None, left=None, opacity=None, top=None, width=None, hideDesktop=None,
                                            hideMobile=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if contentId is None: raise ValueError("Invalid argument: required argument contentId is none.")
        if type is None: raise ValueError("Invalid argument: required argument type is none.")
        if value is None: raise ValueError("Invalid argument: required argument value is none.")
        args = {
            'access_token': self.token
        }
        if isinstance(value, str):
            value = value.encode('ascii', 'xmlcharrefreplace')
        data = {
            'type': type,
            'value': value
        }
        if index is not None:
            data['index'] = index
        if backgroundColor is not None:
            data['backgroundColor'] = backgroundColor
        if borderColor is not None:
            data['borderColor'] = borderColor
        if borderStyle is not None:
            data['borderStyle'] = borderStyle
        if borderWidth is not None:
            data['borderWidth'] = borderWidth
        if height is not None:
            data['height'] = height
        if layer is not None:
            data['layer'] = layer
        if left is not None:
            data['left'] = left
        if opacity is not None:
            data['opacity'] = opacity
        if top is not None:
            data['top'] = top
        if width is not None:
            data['width'] = width
        if hideDesktop is not None:
            data['hideDesktop'] = hideDesktop
        if hideMobile is not None:
            data['hideMobile'] = hideMobile
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPage/" + str(id) + "/content/" + str(contentId) +
                                ".json", args, data, mode='nojsondumps')
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def delete_landing_page_content_section(self, id, contentId):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if contentId is None: raise ValueError("Invalid argument: required argument contentId is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPage/" + str(id) + "/content/" + str(contentId) +
                                "/delete.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_landing_page_dynamic_content(self, id, dynamicContentId, status=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if dynamicContentId is None: raise ValueError("Invalid argument: required argument dynamicContentId is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/landingPage/" + str(id) + "/dynamicContent/" +
                               str(dynamicContentId) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def update_landing_page_dynamic_content(self, id, dynamicContentId, segment, value, type, index=None,
                                            backgroundColor=None, borderColor=None, borderStyle=None, borderWidth=None,
                                            height=None, layer=None, left=None, opacity=None, top=None, width=None,
                                            hideDesktop=None, hideMobile=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if dynamicContentId is None: raise ValueError("Invalid argument: required argument dynamicContentId is none.")
        if segment is None: raise ValueError("Invalid argument: required argument segment is none.")
        if value is None: raise ValueError("Invalid argument: required argument value is none.")
        if type is None: raise ValueError("Invalid argument: required argument type is none.")
        args = {
            'access_token': self.token
        }
        if type == 'HTML':
            value = value.encode('ascii', 'xmlcharrefreplace')
        data = {
            'segment': segment,
            'value': value,
            'type': type
        }
        if index is not None:
            data['index'] = index
        if backgroundColor is not None:
            data['backgroundColor'] = backgroundColor
        if borderColor is not None:
            data['borderColor'] = borderColor
        if borderStyle is not None:
            data['borderStyle'] = borderStyle
        if borderWidth is not None:
            data['borderWidth'] = borderWidth
        if height is not None:
            data['height'] = height
        if layer is not None:
            data['layer'] = layer
        if left is not None:
            data['left'] = left
        if opacity is not None:
            data['opacity'] = opacity
        if top is not None:
            data['top'] = top
        if width is not None:
            data['width'] = width
        if hideDesktop is not None:
            data['hideDesktop'] = hideDesktop
        if hideMobile is not None:
            data['hideMobile'] = hideMobile
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPage/" + str(id) + "/dynamicContent/" +
                                str(dynamicContentId) + ".json", args, data, mode='nojsondumps')
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def approve_landing_page(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPage/" + str(id) + "/approveDraft.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def unapprove_landing_page(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPage/" + str(id) + "/unapprove.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def discard_landing_page_draft(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPage/" + str(id) + "/discardDraft.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def clone_landing_page(self, id, name, folderId, folderType, description=None, template=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if folderId is None: raise ValueError("Invalid argument: required argument folder is none.")
        if folderType is None: raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description is not None:
            args['description'] = description
        if template is not None:
            args['template'] = template
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPage/" + str(id) + "/clone.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    # --------- FORMS ---------

    def create_form(self, name, folderId, folderType, description=None, language=None, locale=None,
                    progressiveProfiling=None, labelPosition=None, fontFamily=None, fontSize=None, knownVisitor=None,
                    theme=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if folderId is None: raise ValueError("Invalid argument: required argument folder is none.")
        if folderType is None: raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description is not None:
            args['description'] = description
        if language is not None:
            args['language'] = language
        if locale is not None:
            args['locale'] = locale
        if progressiveProfiling is not None:
            args['progressiveProfiling'] = progressiveProfiling
        if labelPosition is not None:
            args['labelPosition'] = labelPosition
        if fontFamily is not None:
            args['fontFamily'] = fontFamily
        if fontSize is not None:
            args['fontSize'] = fontSize
        if knownVisitor is not None:
            args['knownVisitor'] = knownVisitor
        if theme is not None:
            args['theme'] = theme
        result = HttpLib().post(self.host + "/rest/asset/v1/forms.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_form_by_id(self, id, status=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/form/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_form_by_name(self, name, status=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/form/byName.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def delete_form(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/form/" + str(id) + "/delete.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def update_form(self, id, name=None, description=None, language = None, locale = None, progressiveProfiling = None,
                    labelPosition = None, fontFamily = None, fontSize = None, knownVisitor = None, formTheme=None,
                    customcss=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if name is not None:
            args['name'] = name
        if description is not None:
            args['description'] = description
        if language is not None:
            args['language'] = language
        if locale is not None:
            args['locale'] = locale
        if progressiveProfiling is not None:
            args['progressiveProfiling'] = progressiveProfiling
        if labelPosition is not None:
            args['labelPosition'] = labelPosition
        if fontFamily is not None:
            args['fontFamily'] = fontFamily
        if fontSize is not None:
            args['fontSize'] = fontSize
        if knownVisitor is not None:
            args['knownVisitor'] = knownVisitor
        if formTheme is not None:
            args['formTheme'] = formTheme
        if customcss is not None:
            args['customcss'] = customcss
        result = HttpLib().post(self.host + "/rest/asset/v1/form/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_forms(self, maxReturn=None, status=None, folderId=None, folderType=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if maxReturn is not None:
            args['maxReturn'] = maxReturn
        else:
            maxReturn = 20
        if status is not None:
            args['status'] = status
        if folderId is not None:
            args['folder'] = "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        result_list = []
        offset = 0
        while True:
            result = HttpLib().get(self.host + "/rest/asset/v1/forms.json", args)
            if result is None: raise Exception("Empty Response")
            if not result['success']: raise MarketoException(result['errors'][0])
            if 'result' in result:
                if len(result['result']) < maxReturn:
                    result_list.extend(result['result'])
                    break
            else:
                break
            result_list.extend(result['result'])
            offset += maxReturn
            args['offset'] = offset
        return result_list

    def get_form_fields(self, id, status=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/form/" + str(id) + "/fields.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def create_form_field(self, id, fieldId, label=None, labelWidth=None, fieldWidth=None, instructions=None,
                          required=None, formPrefill=None, initiallyChecked=None, values=None, labelToRight=None,
                          hintText=None, defaultValue=None, minValue=None, maxValue=None, multiSelect=None,
                          maxLength=None, maskInput=None, visibleLines=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if fieldId is None: raise ValueError("Invalid argument: required argument fieldId is none.")
        args = {
            'access_token': self.token,
            'fieldId': fieldId
        }
        if label is not None:
            args['label'] =  label
        if labelWidth is not None:
            args['labelWidth'] = labelWidth
        if fieldWidth is not None:
            args['fieldWidth'] = fieldWidth
        if instructions is not None:
            args['instructions'] = instructions
        if required is not None:
            args['required'] = required
        if formPrefill is not None:
            args['formPrefill'] = formPrefill
        if initiallyChecked is not None:
            args['initiallyChecked'] = initiallyChecked
        if values is not None:
            args['values'] = values
        if labelToRight is not None:
            args['labelToRight'] = labelToRight
        if hintText is not None:
            args['hintText'] = hintText
        if defaultValue is not None:
            args['defaultValue'] = defaultValue
        if minValue is not None:
            args['minValue'] = minValue
        if maxValue is not None:
            args['maxValue'] = maxValue
        if multiSelect is not None:
            args['multiSelect'] = multiSelect
        if maxLength is not None:
            args['maxLength'] = maxLength
        if maskInput is not None:
            args['maskInput'] = maskInput
        if visibleLines is not None:
            args['visibleLines'] = visibleLines
        result = HttpLib().post(self.host + "/rest/asset/v1/form/" + str(id) + "/fields.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def update_form_field(self, id, fieldId, label=None, fieldType=None, labelWidth=None, fieldWidth=None, instructions=None,
                          required=None, formPrefill=None, initiallyChecked=None, values=None, labelToRight=None,
                          hintText=None, defaultValue=None, minValue=None, maxValue=None, multiSelect=None,
                          maxLength=None, maskInput=None, visibleLines=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if fieldId is None: raise ValueError("Invalid argument: required argument fieldId is none.")
        args = {
            'access_token': self.token
        }
        data = {}
        if label is not None:
            data['label'] = label
        if fieldType is not None:
            args['fieldType'] = fieldType
        if labelWidth is not None:
            data['labelWidth'] = labelWidth
        if fieldWidth is not None:
            data['fieldWidth'] = fieldWidth
        if instructions is not None:
            data['instructions'] = instructions
        if required is not None:
            data['required'] = required
        if formPrefill is not None:
            data['formPrefill'] = formPrefill
        if initiallyChecked is not None:
            data['initiallyChecked'] = initiallyChecked
        if values is not None:
            data['values'] = values
        if labelToRight is not None:
            data['labelToRight'] = labelToRight
        if hintText is not None:
            data['hintText'] = hintText
        if defaultValue is not None:
            data['defaultValue'] = defaultValue
        if minValue is not None:
            data['minValue'] = minValue
        if maxValue is not None:
            data['maxValue'] = maxValue
        if multiSelect is not None:
            data['multiSelect'] = multiSelect
        if maxLength is not None:
            data['maxLength'] = maxLength
        if maskInput is not None:
            data['maskInput'] = maskInput
        if visibleLines is not None:
            data['visibleLines'] = visibleLines
        result = HttpLib().post(self.host + "/rest/asset/v1/form/" + str(id) + "/field/" + str(fieldId) +
                                ".json", args, data, mode='nojsondumps')
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def delete_form_field(self, id, fieldId):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if fieldId is None: raise ValueError("Invalid argument: required argument contentId is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/form/" + str(id) + "/field/" + str(fieldId) +
                                "/delete.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def approve_form(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/form/" + str(id) + "/approveDraft.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def unapprove_form(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/form/" + str(id) + "/unapprove.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def discard_form_draft(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/form/" + str(id) + "/discardDraft.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def clone_form(self, id, name, folderId, folderType, description=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if folderId is None: raise ValueError("Invalid argument: required argument folder is none.")
        if folderType is None: raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description is not None:
            args['description'] = description
        result = HttpLib().post(self.host + "/rest/asset/v1/form/" + str(id) + "/clone.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    # --------- FILES ---------

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
        result = HttpLib().post(self.host + "/rest/asset/v1/files.json", args, files=file, filename="file")
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_file_by_id(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/rest/asset/v1/file/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_file_by_name(self, name):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        args = {
            'access_token' : self.token,
            'name' : name
        }
        result = HttpLib().get(self.host + "/rest/asset/v1/file/byName.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def list_files(self, folder=None, maxReturn=None):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        if folder is not None:
            args['folder'] = folder
        if maxReturn is not None:
            args['maxReturn'] = maxReturn
        else:
            maxReturn = 20
        result_list = []
        offset = 0
        while True:
            result = HttpLib().get(self.host + "/rest/asset/v1/files.json", args)
            if result is None: raise Exception("Empty Response")
            if not result['success']: raise MarketoException(result['errors'][0])
            if 'result' in result:
                if len(result['result']) < maxReturn:
                    result_list.extend(result['result'])
                    break
            else:
                break
            result_list.extend(result['result'])
            offset += maxReturn
            args['offset'] = offset
        return result_list

    def update_file_content(self, id, file):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if file is None: raise ValueError("Invalid argument: required argument file is none.")
        args = {
            'access_token' : self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/file/" + str(id) + "/content.json", args, files=file,
                                filename="file")
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    # --------- SNIPPETS ---------------

    def create_snippet(self, name, folderId, folderType, description=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if folderId is None: raise ValueError("Invalid argument: required argument folder is none.")
        if folderType is None: raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description is not None:
            args['description'] = description
        result = HttpLib().post(self.host + "/rest/asset/v1/snippets.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_snippet_by_id(self, id, status=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/snippet/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def delete_snippet(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/snippet/" + str(id) + "/delete.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def update_snippet(self, id, name=None, description=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if name is not None:
            args['name'] = name
        if description is not None:
            args['description'] = description
        result = HttpLib().post(self.host + "/rest/asset/v1/snippet/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_snippets(self, maxReturn=None, status=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if maxReturn is not None:
            args['maxReturn'] = maxReturn
        else:
            maxReturn = 20
        if status is not None:
            args['status'] = status
        result_list = []
        offset = 0
        while True:
            result = HttpLib().get(self.host + "/rest/asset/v1/snippets.json", args)
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            if 'result' in result:
                if len(result['result']) < maxReturn:
                    result_list.extend(result['result'])
                    break
            else:
                break
            result_list.extend(result['result'])
            offset += maxReturn
            args['offset'] = offset
        return result_list

    def get_snippet_content(self, id, status=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/snippet/" + str(id) + "/content.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def update_snippet_content(self, id, type, content):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        #if type is not "Text" and type is not "DynamicContent": raise ValueError("Invalid argument: type should "
        #                                                                         "be 'Text' or 'DynamicContent'.")
        if type is None: raise ValueError("Invalid argument: required argument type is none.")
        if content is None: raise ValueError("Invalid argument: required argument content is none.")
        args = {
            'access_token': self.token,
            'type': type,
            'content': content
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/snippet/" + str(id) + "/content.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def approve_snippet(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/snippet/" + str(id) + "/approveDraft.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def unapprove_snippet(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/snippet/" + str(id) + "/unapprove.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def discard_snippet_draft(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/snippet/" + str(id) + "/discardDraft.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def clone_snippet(self, id, name, folderId, folderType, description=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if folderId is None: raise ValueError("Invalid argument: required argument folder is none.")
        if folderType is None: raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description is not None:
            args['description'] = description
        result = HttpLib().post(self.host + "/rest/asset/v1/snippet/" + str(id) + "/clone.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def update_snippet_dynamic_content(self, id, segmentId, value=None, type=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if segmentId is None: raise ValueError("Invalid argument: required argument segmentId is none.")
        args = {
            'access_token' : self.token
        }
        if value is not None:
            args['value'] = value
        if type is not None:
            args['type'] = type
        result = HttpLib().post(self.host + "/rest/asset/v1/snippet/" + str(id) + "/dynamicContent/" +
                               str(segmentId) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_snippet_dynamic_content(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/rest/asset/v1/snippet/" + str(id) + "/dynamicContent.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    # ----- SEGMENTATIONS -----

    def get_segmentations(self, status=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/segmentation.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_segments(self, id, status=None):
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/segmentation/" + str(id) + "/segments.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']


    # ----- LANDING PAGE TEMPLATES -----

    def create_landing_page_template(self, name, folderId, folderType, description=None, templateType=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if folderId is None: raise ValueError("Invalid argument: required argument folder is none.")
        if folderType is None: raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description is not None:
            args['description'] = description
        if templateType is not None:
            args['templateType'] = templateType
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPageTemplates.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_landing_page_template_by_id(self, id, status=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_landing_page_template_by_name(self, name, status=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/landingPageTemplate/byName.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def get_landing_page_templates(self, maxReturn=None, status=None, folderId=None, folderType=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if maxReturn is not None:
            args['maxReturn'] = maxReturn
        else:
            maxReturn = 20
        if status is not None:
            args['status'] = status
        if folderId is not None and folderType is not None:
            args['folder'] = "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        result_list = []
        offset = 0
        while True:
            result = HttpLib().get(self.host + "/rest/asset/v1/landingPageTemplates.json", args)
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            if 'result' in result:
                if len(result['result']) < maxReturn:
                    result_list.extend(result['result'])
                    break
            else:
                break
            result_list.extend(result['result'])
            offset += maxReturn
            args['offset'] = offset
        return result_list

    def get_landing_page_template_content(self, id, status=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = HttpLib().get(self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + "/content.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def update_landing_page_template_content(self, id, content):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if content is None: raise ValueError("Invalid argument: required argument content is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + "/content.json", args,
                                files=content, filename="content")
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def update_landing_page_template(self, id, name=None, description=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if name is not None:
            args['name'] = name
        if description is not None:
            args['description'] = description
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def delete_landing_page_template(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + "/delete.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def approve_landing_page_template(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + "/approveDraft.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def unapprove_landing_page_template(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + "/unapprove.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def discard_landing_page_template_draft(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + "/discardDraft.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def clone_landing_page_template(self, id, name, folderId, folderType):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if folderId is None: raise ValueError("Invalid argument: required argument folder is none.")
        if folderType is None: raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + "/clone.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']


    # --------- PROGRAM ---------

    def create_program(self, folderId, folderType, name, type, channel, description=None, tags=None, costs=None):
        self.authenticate()
        if folderId is None: raise ValueError("Invalid argument: required argument folderId is none.")
        if folderType is None: raise ValueError("Invalid argument: required argument folderType is none.")
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if type is None: raise ValueError("Invalid argument: required argument type is none.")
        if channel is None: raise ValueError("Invalid argument: required argument channel is none.")
        args = {
            'access_token': self.token,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}",
            'name': name,
            'type': type,
            'channel': channel
        }
        if description is not None:
            args['description'] = description
        if tags is not None:
            tags_formatted =[]
            for key, elem in tags.items():
                tag_pair = {'tagType': key, 'tagValue': elem}
                tags_formatted.append(tag_pair)
            args['tags'] = str(tags_formatted)
        if costs is not None:
            args['costs'] = str(costs)
        result = HttpLib().post(self.host + "/rest/asset/v1/programs.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_program_by_id(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().get(self.host + "/rest/asset/v1/program/" + str(id) + ".json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_program_by_name(self, name):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        result = HttpLib().get(self.host + "/rest/asset/v1/program/byName.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_program_by_tag_type(self, tagType, tagValue):
        self.authenticate()
        if tagType is None: raise ValueError("Invalid argument: required argument tagType is none.")
        if tagValue is None: raise ValueError("Invalid argument: required argument tagValue is none.")
        args = {
            'access_token': self.token,
            'tagType': tagType,
            'tagValue': tagValue
        }
        result = HttpLib().get(self.host + "/rest/asset/v1/program/byTag.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def update_program(self, id, name=None, description=None, tags=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        data=[]
        if name is not None:
            data.append(('name',name))
        if description is not None:
            data.append(('description',description))
        if tags is not None:
            tags_formatted =[]
            for key, elem in tags.items():
                tag_pair = {'tagType': key, 'tagValue': elem}
                tags_formatted.append(tag_pair)
            data.append(('tags',str(tags_formatted)))
        result = HttpLib().post(self.host + "/rest/asset/v1/program/" + str(id) + ".json", args, data, mode='nojsondumps')
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def delete_program(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/program/" + str(id) + "/delete.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def browse_programs(self, status=None, maxReturn=None):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        if status is not None:
            args['status'] = status
        if maxReturn is not None:
            args['maxReturn'] = maxReturn
        else:
            maxReturn = 20
        result_list = []
        offset = 0
        while True:
            result = HttpLib().get(self.host + "/rest/asset/v1/programs.json", args)
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            if 'result' in result:
                if len(result['result']) < maxReturn:
                    result_list.extend(result['result'])
                    break
            else:
                break
            result_list.extend(result['result'])
            offset += maxReturn
            args['offset'] = offset
        return result_list

    def clone_program(self, id, name, folderId, folderType, description=None):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if folderId is None: raise ValueError("Invalid argument: required argument folderId is none.")
        if folderType is None: raise ValueError("Invalid argument: required argument folderType is none.")
        args = {
            'access_token': self.token,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}",
            'name': name
        }
        if description is not None:
            args['description'] = description
        result = HttpLib().post(self.host + "/rest/asset/v1/program/" + str(id) + "/clone.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def approve_program(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/program/" + str(id) + "/approve.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def unapprove_program(self, id):
        self.authenticate()
        if id is None: raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = HttpLib().post(self.host + "/rest/asset/v1/program/" + str(id) + "/unapprove.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_channels(self, maxReturn=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if maxReturn is not None:
            args['maxReturn'] = maxReturn
        else:
            maxReturn = 20
        result_list = []
        offset = 0
        while True:
            result = HttpLib().get(self.host + "/rest/asset/v1/channels.json", args)
            if result is None: raise Exception("Empty Response")
            if not result['success']: raise MarketoException(result['errors'][0])
            if 'result' in result:
                if len(result['result']) < maxReturn:
                    result_list.extend(result['result'])
                    break
            else:
                break
            result_list.extend(result['result'])
            offset += maxReturn
            args['offset'] = offset
        return result_list

    def get_channel_by_name(self, name):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        result = HttpLib().get(self.host + "/rest/asset/v1/channel/byName.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_tags(self, maxReturn=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if maxReturn is not None:
            args['maxReturn'] = maxReturn
        else:
            maxReturn = 20
        result_list = []
        offset = 0
        while True:
            result = HttpLib().get(self.host + "/rest/asset/v1/tagTypes.json", args)
            if result is None: raise Exception("Empty Response")
            if not result['success']: raise MarketoException(result['errors'][0])
            if 'result' in result:
                if len(result['result']) < maxReturn:
                    result_list.extend(result['result'])
                    break
            else:
                break
            result_list.extend(result['result'])
            offset += maxReturn
            args['offset'] = offset
        return result_list

    def get_tag_by_name(self, name):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        result = HttpLib().get(self.host + "/rest/asset/v1/tagType/byName.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']


    # --------- CUSTOM OBJECTS ---------

    def get_list_of_custom_objects(self, names=None):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        if names is not None:
            args['names'] = names
        result = HttpLib().get(self.host + "/rest/v1/customobjects.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def describe_custom_object(self, name):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/rest/v1/customobjects/" + name + "/describe.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def create_update_custom_objects(self, name, input, action=None, dedupeBy=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if input is None: raise ValueError("Invalid argument: required argument input is none.")
        args = {
            'access_token' : self.token
        }
        data={
            'input': []
             }
        for record in input:
            data['input'].append(record)
        if action is not None:
            data['action'] = action
        if dedupeBy is not None:
            data['dedupeBy'] = dedupeBy
        result = HttpLib().post(self.host + "/rest/v1/customobjects/" + name + ".json", args, data)
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def delete_custom_objects(self, name, input, deleteBy=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if input is None: raise ValueError("Invalid argument: required argument input is none.")
        args = {
            'access_token' : self.token
        }
        data={
            'input': []
             }
        for record in input:
            data['input'].append(record)
        if deleteBy is not None:
            data['deleteBy'] = deleteBy
        result = HttpLib().post(self.host + "/rest/v1/customobjects/" + name + "/delete.json", args, data)
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_custom_objects(self, name, input, filterType, fields=None, batchSize=None):
        self.authenticate()
        if name is None: raise ValueError("Invalid argument: required argument name is none.")
        if input is None: raise ValueError("Invalid argument: required argument input is none.")
        if filterType is None: raise ValueError("Invalid argument: required argument filterType is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        data={
            'filterType': filterType,
            'input': input
             }
        if fields is not None:
            data['fields'] = fields
        if batchSize is not None:
            data['batchSize'] = batchSize
        result_list = []
        while True:
            result = HttpLib().post(self.host + "/rest/v1/customobjects/" + name + ".json", args, data)
            if result is None: raise Exception("Empty Response")
            if not result['success']: raise MarketoException(result['errors'][0])
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            data['nextPageToken'] = result['nextPageToken']
        return result_list

    # ------ OPPORTUNITY -------

    def describe_opportunity(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/rest/v1/opportunities/describe.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def create_update_opportunities(self, input, action=None, dedupeBy=None):
        self.authenticate()
        if input is None: raise ValueError("Invalid argument: required argument input is none.")
        args = {
            'access_token' : self.token
        }
        data={
            'input': []
             }
        for opportunity in input:
            data['input'].append(opportunity)
        if action is not None:
            data['action'] = action
        if dedupeBy is not None:
            data['dedupeBy'] = dedupeBy
        result = HttpLib().post(self.host + "/rest/v1/opportunities.json", args, data)
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def delete_opportunities(self, input, deleteBy=None):
        self.authenticate()
        if input is None: raise ValueError("Invalid argument: required argument input is none.")
        args = {
            'access_token' : self.token
        }
        data={
            'input': []
             }
        for opportunity in input:
            data['input'].append(opportunity)
        if deleteBy is not None:
            data['deleteBy'] = deleteBy
        result = HttpLib().post(self.host + "/rest/v1/opportunities/delete.json", args, data)
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_opportunities(self, filterType, filterValues=None, fields=None, batchSize=None):
        self.authenticate()
        if filterType is None: raise ValueError("Invalid argument: required argument filterType is none.")

        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        filterValues = filterValues.split() if type(filterValues) is str else filterValues
        data=[('filterValues',(',').join(filterValues)), ('filterType', filterType)]
        if fields is not None:
            data.append(('fields',fields))
        if batchSize is not None:
            data.append(('batchSize',batchSize))
        result_list = []
        while True:
            result = HttpLib().post(self.host + "/rest/v1/opportunities.json", args, data, mode='nojsondumps')
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def describe_opportunity_role(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/rest/v1/opportunities/roles/describe.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def create_update_opportunities_roles(self, input, action=None, dedupeBy=None):
        self.authenticate()
        if input is None: raise ValueError("Invalid argument: required argument input is none.")
        args = {
            'access_token' : self.token
        }
        data={
            'input': []
             }
        for opportunity in input:
            data['input'].append(opportunity)
        if action is not None:
            data['action'] = action
        if dedupeBy is not None:
            data['dedupeBy'] = dedupeBy
        result = HttpLib().post(self.host + "/rest/v1/opportunities/roles.json", args, data)
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def delete_opportunity_roles(self, input, deleteBy=None):
        self.authenticate()
        if input is None: raise ValueError("Invalid argument: required argument input is none.")
        args = {
            'access_token' : self.token
        }
        data={
            'input': []
             }
        for opportunity in input:
            data['input'].append(opportunity)
        if deleteBy is not None:
            data['deleteBy'] = deleteBy
        result = HttpLib().post(self.host + "/rest/v1/opportunities/roles/delete.json", args, data)
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_opportunity_roles(self, filterType, filterValues, fields=None, batchSize=None):
        self.authenticate()
        if filterType is None: raise ValueError("Invalid argument: required argument filterType is none.")
        if filterValues is None: raise ValueError("Invalid argument: required argument filter_values is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        filterValues = filterValues.split() if type(filterValues) is str else filterValues
        data=[('filterValues',(',').join(filterValues)), ('filterType', filterType)]
        if fields is not None:
            data.append(('fields',fields))
        if batchSize is not None:
            data.append(('batchSize',batchSize))
        result_list = []
        while True:
            result = HttpLib().post(self.host + "/rest/v1/opportunities/roles.json", args, data, mode='nojsondumps')
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list




    # --------- COMPANY ---------

    def describe_company(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/rest/v1/companies/describe.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def create_update_companies(self, input, action=None, dedupeBy=None):
        self.authenticate()
        if input is None: raise ValueError("Invalid argument: required argument input is none.")
        args = {
            'access_token' : self.token
        }
        data={
            'input': []
             }
        for company in input:
            data['input'].append(company)
        if action is not None:
            data['action'] = action
        if dedupeBy is not None:
            data['dedupeBy'] = dedupeBy
        result = HttpLib().post(self.host + "/rest/v1/companies.json", args, data)
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def delete_companies(self, input, deleteBy=None):
        self.authenticate()
        if input is None: raise ValueError("Invalid argument: required argument input is none.")
        args = {
            'access_token' : self.token
        }
        data={
            'input': []
             }
        for company in input:
            data['input'].append(company)
        if deleteBy is not None:
            data['deleteBy'] = deleteBy
        result = HttpLib().post(self.host + "/rest/v1/companies/delete.json", args, data)
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_companies(self, filterType, filterValues, fields=None, batchSize=None):
        self.authenticate()
        if filterType is None: raise ValueError("Invalid argument: required argument filterType is none.")
        if filterValues is None: raise ValueError("Invalid argument: required argument filter_values is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        filterValues = filterValues.split() if type(filterValues) is str else filterValues
        data=[('filterValues',(',').join(filterValues)), ('filterType', filterType)]
        if fields is not None:
            data.append(('fields',fields))
        if batchSize is not None:
            data.append(('batchSize',batchSize))
        result_list = []
        while True:
            result = HttpLib().post(self.host + "/rest/v1/companies.json", args, data, mode='nojsondumps')
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    # --------- SALES PERSON ---------

    def describe_sales_person(self):
        self.authenticate()
        args = {
            'access_token' : self.token
        }
        result = HttpLib().get(self.host + "/rest/v1/salespersons/describe.json", args)
        if result is None: raise Exception("Empty Response")
        if not result['success'] : raise MarketoException(result['errors'][0])
        return result['result']

    def create_update_sales_persons(self, input, action=None, dedupeBy=None):
        self.authenticate()
        if input is None: raise ValueError("Invalid argument: required argument input is none.")
        args = {
            'access_token' : self.token
        }
        data={
            'input': []
             }
        for person in input:
            data['input'].append(person)
        if action is not None:
            data['action'] = action
        if dedupeBy is not None:
            data['dedupeBy'] = dedupeBy
        result = HttpLib().post(self.host + "/rest/v1/salespersons.json", args, data)
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def delete_sales_persons(self, input, deleteBy=None):
        self.authenticate()
        if input is None: raise ValueError("Invalid argument: required argument input is none.")
        args = {
            'access_token' : self.token
        }
        data={
            'input': []
             }
        for record in input:
            data['input'].append(record)
        if deleteBy is not None:
            data['deleteBy'] = deleteBy
        result = HttpLib().post(self.host + "/rest/v1/salespersons/delete.json", args, data)
        if not result['success']: raise MarketoException(result['errors'][0])
        return result['result']

    def get_sales_persons(self, filterType, filterValues, fields=None, batchSize=None):
        self.authenticate()
        if filterType is None: raise ValueError("Invalid argument: required argument filterType is none.")
        if filterValues is None: raise ValueError("Invalid argument: required argument filter_values is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        filterValues = filterValues.split() if type(filterValues) is str else filterValues
        data=[('filterValues',(',').join(filterValues)), ('filterType', filterType)]
        if fields is not None:
            data.append(('fields',fields))
        if batchSize is not None:
            data.append(('batchSize',batchSize))
        result_list = []
        while True:
            result = HttpLib().post(self.host + "/rest/v1/salespersons.json", args, data, mode='nojsondumps')
            if result is None: raise Exception("Empty Response")
            if not result['success'] : raise MarketoException(result['errors'][0])
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list
