import time
from datetime import datetime
import pytz
import json
from marketorestpython.helper.http_lib import HttpLib
from marketorestpython.helper.exceptions import MarketoException


def has_empty_warning(result):
    if 'result' not in result \
            and 'warnings' in result \
            and len(result['warnings']) \
            and result['warnings'][0] == 'No assets found for the given search criteria.':
        return True

    return False


class MarketoClient:
    expires_in = None
    token_type = None
    scope = None
    last_request_id = None  # intended to save last request id, but not used right now

    def __init__(self, munchkin_id, client_id=None, client_secret=None, api_limit=None, max_retry_time=300,
                 access_token=None, requests_timeout=None):
        assert(munchkin_id is not None)
        assert((client_id and client_secret) or access_token)
        self.valid_until = None
        self.host = "https://" + munchkin_id + ".mktorest.com"
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = access_token
        self.API_CALLS_MADE = 0
        self.API_LIMIT = api_limit
        self.max_retry_time = max_retry_time
        if requests_timeout is not None:
            error_message = "requests_timeout must be a positive float or int, or a two-element tuple of positive " \
                            "floats or ints"
            if isinstance(requests_timeout, int) or isinstance(requests_timeout, float):
                assert requests_timeout > 0, error_message
                self.requests_timeout = requests_timeout
            elif isinstance(requests_timeout, tuple):
                assert (
                        len(requests_timeout) == 2 and
                        all(isinstance(x, int) or isinstance(x, float) for x in requests_timeout) and
                        all(x > 0 for x in requests_timeout)
                ), error_message
                self.requests_timeout = requests_timeout
            else:
                raise AssertionError(error_message)
        else:
            self.requests_timeout = None

    def _api_call(self, method, endpoint, *args, **kwargs):
        request = HttpLib(max_retry_time_conf=self.max_retry_time, requests_timeout=self.requests_timeout)
        result = getattr(request, method)(endpoint, *args, **kwargs)
        self.API_CALLS_MADE += 1
        if self.API_LIMIT and self.API_CALLS_MADE >= self.API_LIMIT:
            raise Exception({'message': '# of API Calls exceeded the limit as specified in the Python script: '
                                        + str(self.API_LIMIT), 'code': '416'})
        return result

    def execute(self, method, *args, **kargs):
        result = None

        '''
            max 10 rechecks
        '''
        for i in range(0, 10):
            try:

                method_map = {
                    'get_lead_by_id': self.get_lead_by_id,
                    'get_multiple_leads_by_filter_type': self.get_multiple_leads_by_filter_type,
                    'get_multiple_leads_by_list_id': self.get_multiple_leads_by_list_id,
                    'get_multiple_leads_by_list_id_yield': self.get_multiple_leads_by_list_id_yield,
                    'get_multiple_leads_by_program_id': self.get_multiple_leads_by_program_id,
                    'get_multiple_leads_by_program_id_yield': self.get_multiple_leads_by_program_id_yield,
                    'change_lead_program_status': self.change_lead_program_status,
                    'sync_program_member_data': self.sync_program_member_data,
                    'create_update_leads': self.create_update_leads,
                    'associate_lead': self.associate_lead,
                    'push_lead': self.push_lead,
                    'merge_lead': self.merge_lead,
                    'get_smart_campaigns_by_lead_id': self.get_smart_campaigns_by_lead_id,
                    'get_lead_partitions': self.get_lead_partitions,
                    'create_list': self.create_list,
                    'update_list': self.update_list,
                    'delete_list': self.delete_list,
                    'get_list_by_id': self.get_list_by_id,
                    'get_list_by_name': self.get_list_by_name,
                    'get_multiple_lists': self.get_multiple_lists,
                    'browse_lists': self.browse_lists,
                    'browse_lists_yield': self.browse_lists_yield,
                    'add_leads_to_list': self.add_leads_to_list,
                    'remove_leads_from_list': self.remove_leads_from_list,
                    'member_of_list': self.member_of_list,
                    'get_smart_list_by_id': self.get_smart_list_by_id,
                    'get_smart_list_by_name': self.get_smart_list_by_name,
                    'get_smart_lists': self.get_smart_lists,
                    'delete_smart_list': self.delete_smart_list,
                    'clone_smart_list': self.clone_smart_list,
                    'get_smart_campaign_by_id': self.get_smart_campaign_by_id,
                    'get_smart_campaign_by_name': self.get_smart_campaign_by_name,
                    'get_smart_campaigns': self.get_smart_campaigns,
                    'get_campaign_by_id': self.get_campaign_by_id,
                    'get_multiple_campaigns': self.get_multiple_campaigns,
                    'schedule_campaign': self.schedule_campaign,
                    'request_campaign': self.request_campaign,
                    'activate_smart_campaign': self.activate_smart_campaign,
                    'deactivate_smart_campaign': self.deactivate_smart_campaign,
                    'create_smart_campaign': self.create_smart_campaign,
                    'update_smart_campaign': self.update_smart_campaign,
                    'clone_smart_campaign': self.clone_smart_campaign,
                    'delete_smart_campaign': self.delete_smart_campaign,
                    'get_smart_list_by_smart_campaign_id': self.get_smart_list_by_smart_campaign_id,
                    'import_lead': self.import_lead,
                    'get_import_lead_status': self.get_import_lead_status,
                    'get_import_failure_file': self.get_import_failure_file,
                    'get_import_warning_file': self.get_import_warning_file,
                    'describe': self.describe,
                    'describe2': self.describe2,
                    'describe_program_member': self.describe_program_member,
                    'get_activity_types': self.get_activity_types,
                    'get_paging_token': self.get_paging_token,
                    'get_lead_activities': self.get_lead_activities,
                    'get_lead_activities_yield': self.get_lead_activities_yield,
                    'get_lead_changes': self.get_lead_changes,
                    'get_lead_changes_yield': self.get_lead_changes_yield,
                    'add_custom_activities': self.add_custom_activities,
                    'get_daily_usage': self.get_daily_usage,
                    'get_last_7_days_usage': self.get_last_7_days_usage,
                    'get_daily_errors': self.get_daily_errors,
                    'get_last_7_days_errors': self.get_last_7_days_errors,
                    'delete_lead': self.delete_lead,
                    'get_deleted_leads': self.get_deleted_leads,
                    'update_leads_partition': self.update_leads_partition,
                    'submit_form': self.submit_form,
                    'create_folder': self.create_folder,
                    'get_folder_by_id': self.get_folder_by_id,
                    'get_folder_by_name': self.get_folder_by_name,
                    'get_folder_contents': self.get_folder_contents,
                    'update_folder': self.update_folder,
                    'delete_folder': self.delete_folder,
                    'browse_folders': self.browse_folders,
                    'browse_folders_yield': self.browse_folders_yield,
                    'create_token': self.create_token,
                    'get_tokens': self.get_tokens,
                    'delete_tokens': self.delete_tokens,
                    'create_email_template': self.create_email_template,
                    'get_email_template_by_id': self.get_email_template_by_id,
                    'get_email_template_by_name': self.get_email_template_by_name,
                    'update_email_template': self.update_email_template,
                    'delete_email_template': self.delete_email_template,
                    'get_email_templates': self.get_email_templates,
                    'get_email_templates_yield': self.get_email_templates_yield,
                    'get_email_template_used_by': self.get_email_template_used_by,
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
                    'get_emails_yield': self.get_emails_yield,
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
                    'get_email_full_content': self.get_email_full_content,
                    'update_email_full_content': self.update_email_full_content,
                    'get_email_variables': self.get_email_variables,
                    'update_email_variable': self.update_email_variable,
                    'create_landing_page': self.create_landing_page,
                    'get_landing_page_by_id': self.get_landing_page_by_id,
                    'get_landing_page_by_name': self.get_landing_page_by_name,
                    'delete_landing_page': self.delete_landing_page,
                    'update_landing_page': self.update_landing_page,
                    'get_landing_pages': self.get_landing_pages,
                    'get_landing_pages_yield': self.get_landing_pages_yield,
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
                    'get_landing_page_variables': self.get_landing_page_variables,
                    'get_landing_page_full_content': self.get_landing_page_full_content,
                    'get_landing_page_redirect_rules': self.get_landing_page_redirect_rules,
                    'get_landing_page_domains': self.get_landing_page_domains,
                    'create_form': self.create_form,
                    'get_form_by_id': self.get_form_by_id,
                    'get_form_by_name': self.get_form_by_name,
                    'delete_form': self.delete_form,
                    'update_form': self.update_form,
                    'get_forms': self.get_forms,
                    'get_forms_yield': self.get_forms_yield,
                    'get_form_fields': self.get_form_fields,
                    'create_form_field': self.create_form_field,
                    'update_form_field': self.update_form_field,
                    'delete_form_field': self.delete_form_field,
                    'approve_form': self.approve_form,
                    'unapprove_form': self.unapprove_form,
                    'discard_form_draft': self.discard_form_draft,
                    'clone_form': self.clone_form,
                    'get_thank_you_page_by_form_id': self.get_thank_you_page_by_form_id,
                    'create_file': self.create_file,
                    'get_file_by_id': self.get_file_by_id,
                    'get_file_by_name': self.get_file_by_name,
                    'list_files': self.list_files,
                    'get_files_yield': self.get_files_yield,
                    'update_file_content': self.update_file_content,
                    'create_snippet': self.create_snippet,
                    'get_snippet_by_id': self.get_snippet_by_id,
                    'delete_snippet': self.delete_snippet,
                    'update_snippet': self.update_snippet,
                    'get_snippets': self.get_snippets,
                    'get_snippets_yield': self.get_snippets_yield,
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
                    'get_landing_page_templates_yield': self.get_landing_page_templates_yield,
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
                    'get_programs_yield': self.get_programs_yield,
                    'clone_program': self.clone_program,
                    'approve_program': self.approve_program,
                    'unapprove_program': self.unapprove_program,
                    'get_smart_list_by_program_id': self.get_smart_list_by_program_id,
                    'get_channels': self.get_channels,
                    'get_channel_by_name': self.get_channel_by_name,
                    'get_tags': self.get_tags,
                    'get_tag_by_name': self.get_tag_by_name,
                    'create_update_custom_object_type': self.create_update_custom_object_type,
                    'delete_custom_object_type': self.delete_custom_object_type,
                    'approve_custom_object_type': self.approve_custom_object_type,
                    'discard_custom_object_type': self.discard_custom_object_type,
                    'get_list_of_custom_object_types': self.get_list_of_custom_object_types,
                    'describe_custom_object_type': self.describe_custom_object_type,
                    'add_field_custom_object_type': self.add_field_custom_object_type,
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
                    'get_sales_persons': self.get_sales_persons,
                    'get_custom_activity_types': self.get_custom_activity_types,
                    'describe_custom_activity_type': self.describe_custom_activity_type,
                    'create_custom_activity_type': self.create_custom_activity_type,
                    'update_custom_activity_type': self.update_custom_activity_type,
                    'approve_custom_activity_type': self.approve_custom_activity_type,
                    'create_custom_activity_type_attribute': self.create_custom_activity_type_attribute,
                    'discard_custom_activity_type_draft': self.discard_custom_activity_type_draft,
                    'delete_custom_activity_type': self.delete_custom_activity_type,
                    'update_custom_activity_type_attribute': self.update_custom_activity_type_attribute,
                    'delete_custom_activity_type_attribute': self.delete_custom_activity_type_attribute,
                    'get_leads_export_jobs_list': self.get_leads_export_jobs_list,
                    'get_activities_export_jobs_list': self.get_activities_export_jobs_list,
                    'get_custom_objects_export_jobs_list': self.get_custom_objects_export_jobs_list,
                    'get_program_members_export_jobs_list': self.get_program_members_export_jobs_list,
                    'create_leads_export_job': self.create_leads_export_job,
                    'create_activities_export_job': self.create_activities_export_job,
                    'create_custom_objects_export_job': self.create_custom_objects_export_job,
                    'create_program_members_export_job': self.create_program_members_export_job,
                    'enqueue_leads_export_job': self.enqueue_leads_export_job,
                    'enqueue_activities_export_job': self.enqueue_activities_export_job,
                    'enqueue_custom_objects_export_job': self.enqueue_custom_objects_export_job,
                    'enqueue_program_members_export_job': self.enqueue_program_members_export_job,
                    'cancel_leads_export_job': self.cancel_leads_export_job,
                    'cancel_activities_export_job': self.cancel_activities_export_job,
                    'cancel_custom_objects_export_job': self.cancel_custom_objects_export_job,
                    'cancel_program_members_export_job': self.cancel_program_members_export_job,
                    'get_leads_export_job_status': self.get_leads_export_job_status,
                    'get_activities_export_job_status': self.get_activities_export_job_status,
                    'get_custom_objects_export_job_status': self.get_custom_objects_export_job_status,
                    'get_program_members_export_job_status': self.get_program_members_export_job_status,
                    'get_leads_export_job_file': self.get_leads_export_job_file,
                    'get_activities_export_job_file': self.get_activities_export_job_file,
                    'get_custom_objects_export_job_file': self.get_custom_objects_export_job_file,
                    'get_program_members_export_job_file': self.get_program_members_export_job_file,
                    'get_named_accounts': self.get_named_accounts,
                    'sync_named_accounts': self.sync_named_accounts,
                    'delete_named_accounts': self.delete_named_accounts,
                    'describe_named_accounts': self.describe_named_accounts,
                    'get_named_account_list_members': self.get_named_account_list_members,
                    'add_named_account_list_members': self.add_named_account_list_members,
                    'remove_named_account_list_members': self.remove_named_account_list_members,
                    'get_named_account_lists': self.get_named_account_lists,
                    'sync_named_account_lists': self.sync_named_account_lists,
                    'delete_named_account_lists': self.delete_named_account_lists
                }
                result = method_map[method](*args, **kargs)
            except MarketoException as e:
                '''
                601 -> auth token not valid
                602 -> auth token expired
                '''
                if e.code in ['601', '602'] and self.client_secret:
                    self.authenticate()
                    continue
                else:
                    raise Exception({'message': e.message, 'code': e.code})
            break
        return result

    def authenticate(self):
        if (self.valid_until is not None and self.valid_until - time.time() >= 60) or not self.client_secret:
            return
        args = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        data = self._api_call('get', self.host + "/identity/oauth/token", args,
            mode='accesstoken')
        if data is None:
            raise Exception("Empty Response")
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
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if fields is not None:
            args['fields'] = fields
        result = self._api_call(
            'get', self.host + "/rest/v1/lead/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_multiple_leads_by_filter_type(self, filterType, filterValues, fields=None, batchSize=None):
        self.authenticate()
        if filterType is None:
            raise ValueError(
                "Invalid argument: required argument filterType is none.")
        if filterValues is None:
            raise ValueError(
                "Invalid argument: required argument filter_values is none.")
        filterValues = filterValues.split() if type(
            filterValues) is str else filterValues
        data = {
            'access_token': self.token,
            '_method': 'GET',
            'filterValues': ','.join(filterValues),
            'filterType': filterType
        }
        if fields is not None:
            data['fields'] = fields
        if batchSize is not None:
            data['batchSize'] = batchSize
        result_list = []
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            data['access_token'] = self.token
            result = self._api_call(
                'post', self.host + "/rest/v1/leads.json", args=None, data=data, mode='nojsondumps')
            if result is None:
                raise Exception("Empty Response")
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            data['nextPageToken'] = result['nextPageToken']
        return result_list

    def get_multiple_leads_by_list_id(self, listId, fields=None, batchSize=None):
        self.authenticate()
        if listId is None:
            raise ValueError(
                "Invalid argument: required argument listId is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        data = []
        if fields is not None:
            data.append(('fields', fields))
        if batchSize is not None:
            data.append(('batchSize', batchSize))
        result_list = []
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('post', self.host + "/rest/v1/list/" +
                                    str(listId) + "/leads.json", args, data, mode='nojsondumps')
            if result is None:
                raise Exception("Empty Response")
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def get_multiple_leads_by_list_id_yield(self, listId, fields=None, batchSize=None, nextPageToken=None,
                                            return_full_result=False):
        self.authenticate()
        if listId is None:
            raise ValueError(
                "Invalid argument: required argument listId is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        if nextPageToken:
            args['nextPageToken'] = nextPageToken
        data = []
        if fields is not None:
            data.append(('fields', fields))
        if batchSize is not None:
            data.append(('batchSize', batchSize))
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('post', self.host + "/rest/v1/list/" +
                                    str(listId) + "/leads.json", args, data, mode='nojsondumps')
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) == 0 or 'nextPageToken' not in result:
                    break
                else:
                    args['nextPageToken'] = result['nextPageToken']

    def get_multiple_leads_by_program_id(self, programId, fields=None, batchSize=None):
        self.authenticate()
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        data = []
        if fields is not None:
            data.append(('fields', fields))
        if batchSize is not None:
            data.append(('batchSize', batchSize))
        result_list = []
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('post', self.host + "/rest/v1/leads/programs/" + str(programId) + ".json", args, data,
                                    mode='nojsondumps')
            if result is None:
                raise Exception("Empty Response")
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def get_multiple_leads_by_program_id_yield(self, programId, fields=None, batchSize=None, nextPageToken=None,
                                               return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        if nextPageToken:
            args['nextPageToken'] = nextPageToken
        data = []
        if fields is not None:
            data.append(('fields', fields))
        if batchSize is not None:
            data.append(('batchSize', batchSize))
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('post', self.host + "/rest/v1/leads/programs/" + str(programId) + ".json", args, data,
                                    mode='nojsondumps')
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) == 0 or 'nextPageToken' not in result:
                    break
                else:
                    args['nextPageToken'] = result['nextPageToken']

    def change_lead_program_status(self, id, leadIds, status):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if leadIds is None:
            raise ValueError(
                "Invalid argument: required argument input is none.")
        if status is None:
            raise ValueError(
                "Invalid argument: required argument status is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'status': status,
            'input': []
        }
        for leadId in leadIds:
            data['input'].append({'id': leadId})
        result = self._api_call(
            'post', self.host + "/rest/v1/leads/programs/" + str(id) + "/status.json", args, data)
        return result['result']

    def sync_program_member_data(self, id, input):
        """
        :param id: program ID
        :param input: example payload
        [
            {
                "leadId": 1789,
                "registrationCode": "dcff5f12-a7c7-11eb-bcbc-0242ac130002"
            },
            {
                "leadId": 1790,
                "registrationCode": "c0404b78-d3fd-47bf-82c4-d16f3852ab3a"
            }
        ]
        """
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if input is None:
            raise ValueError(
                "Invalid argument: required argument input is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'input': input
        }
        result = self._api_call(
            'post', self.host + "/rest/v1/programs/{}/members.json".format(id), args, data)
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
        result = self._api_call(
            'post', self.host + "/rest/v1/leads.json", args, data)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def associate_lead(self, id, cookie):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if cookie is None:
            raise ValueError(
                "Invalid argument: required argument cookie is none.")
        args = {
            'access_token': self.token,
            'id': id,
            'cookie': cookie
        }
        result = self._api_call(
            'post', self.host + "/rest/v1/leads/" + str(id) + "/associate.json", args)
        if result is None:
            raise Exception("Empty Response")
        # there is no 'result' node returned in this call
        return result['success']

    def push_lead(self, leads, programName, lookupField=None, programStatus=None, partitionName=None, source=None,
                  reason=None):
        self.authenticate()
        if leads is None:
            raise ValueError(
                "Invalid argument: required argument 'leads' is None.")
        if programName is None:
            raise ValueError(
                "Invalid argument: required argument 'programName' is None.")
        args = {
            'access_token': self.token
        }
        data = {
            'input': leads,
            'programName': programName
        }
        if lookupField is not None:
            data['lookupField'] = lookupField
        if programStatus is not None:
            data['programStatus'] = programStatus
        if partitionName is not None:
            data['partitionName'] = partitionName
        if source is not None:
            data['source'] = source
        if reason is not None:
            data['reason'] = reason
        result = self._api_call(
            'post', self.host + "/rest/v1/leads/push.json", args, data)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def merge_lead(self, id, leadIds, mergeInCRM=False):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if leadIds is None:
            raise ValueError(
                "Invalid argument: required argument leadIds is none.")
        leadstr = ','.join(map(str, leadIds))
        args = {
            'access_token': self.token,
            'leadIds': leadstr,
            'mergeInCRM': mergeInCRM
        }
        result = self._api_call('post', self.host + "/rest/v1/leads/" +
                                str(id) + "/merge.json", args, mode='merge_lead')
        if result is None:
            raise Exception("Empty Response")
        # there is no 'result' node returned in this call
        return result['success']

    def get_smart_campaigns_by_lead_id(self, lead_id, batchSize=None, earliestUpdatedAt=None, latestUpdatedAt=None):
        self.authenticate()
        if lead_id is None:
            raise ValueError("Invalid argument: required argument lead_id is none.")
        args = {
            'access_token': self.token
        }
        if batchSize is not None:
            args['batchSize'] = batchSize
        if earliestUpdatedAt is not None:
            args['earliestUpdatedAt'] = earliestUpdatedAt
        if latestUpdatedAt is not None:
            args['latestUpdatedAt'] = latestUpdatedAt
        result_list = []
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', '{}/rest/v1/leads/{}/smartCampaignMembership.json'.format(self.host, lead_id), args)
            if result is None:
                raise Exception("Empty Response")
            result_list.extend(result['result'])
            if result['moreResult'] is False:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    # --------- LEAD PARTITIONS ---------

    def get_lead_partitions(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/leads/partitions.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    # --------- LISTS ---------

    def create_list(self, name, folderId, folderType, description=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        data = {
            'name': name,
            'folder': json.dumps({'id': folderId, 'type': folderType})
        }
        if description is not None:
            data['description'] = description
        result = self._api_call('post', self.host + "/rest/asset/v1/staticLists.json", args, data, mode='nojsondumps')
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_list(self, id, name=None, description=None):
        self.authenticate()
        assert name or description
        args = {
            'access_token': self.token
        }
        data = {}
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        result = self._api_call('post', self.host + "/rest/asset/v1/staticList/{}.json".format(id), args, data,
                                mode='nojsondumps')
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_list(self, id):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call('post', self.host + "/rest/asset/v1/staticList/{}/delete.json".format(id), args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_list_by_id(self, id):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/staticList/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_list_by_name(self, name):
        self.authenticate()
        args = {
            'access_token': self.token,
            'name': name
        }
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/staticList/byName.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_multiple_lists(self, id=None, name=None, programName=None, workspaceName=None, batchSize=None):
        self.authenticate()
        args = {
            'access_token': self.token
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
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/v1/lists.json", args)
            if result is None:
                raise Exception("Empty Response")
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def browse_lists(self, folderId=None, folderType=None, offset=None, maxReturn=None, earliestUpdatedAt =None,
                     latestUpdatedAt=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if folderId and folderType:
            args['folder'] = json.dumps({'id': folderId, 'type': folderType})
        if offset:
            args['offset'] = offset
        else:
            offset = 0
        if maxReturn:
            args['maxReturn'] = maxReturn
        else:
            maxReturn = 20
        if earliestUpdatedAt:
            args['earliestUpdatedAt'] = earliestUpdatedAt
        if latestUpdatedAt:
            args['latestUpdatedAt'] = latestUpdatedAt
        result_list = []
        while True:
            self.authenticate()
            args['access_token'] = self.token
            result = self._api_call('get', self.host + "/rest/asset/v1/staticLists.json", args)
            if result is None:
                raise Exception("Empty Response")
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

    def browse_lists_yield(self, folderId=None, folderType=None, offset=0, maxReturn=20, earliestUpdatedAt =None,
                           latestUpdatedAt=None, return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'maxReturn': maxReturn,
            'offset': offset
        }
        if folderId and folderType:
            args['folder'] = json.dumps({'id': folderId, 'type': folderType})
        if earliestUpdatedAt:
            args['earliestUpdatedAt'] = earliestUpdatedAt
        if latestUpdatedAt:
            args['latestUpdatedAt'] = latestUpdatedAt
        while True:
            self.authenticate()
            args['access_token'] = self.token
            result = self._api_call('get', self.host + "/rest/asset/v1/staticLists.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) < maxReturn:
                    break
            else:
                break
            offset += maxReturn
            args['offset'] = offset

    def add_leads_to_list(self, listId, id):
        self.authenticate()
        if listId is None:
            raise ValueError(
                "Invalid argument: required argument listId is none.")
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        leads_list = [{'id': items} for items in id]
        data = {
            'input': leads_list
        }
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/v1/lists/" + str(listId) + "/leads.json", args, data)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def remove_leads_from_list(self, listId, id):
        self.authenticate()
        if listId is None:
            raise ValueError(
                "Invalid argument: required argument listId is none.")
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        leads_list = [{'id': items} for items in id]
        data = {
            'input': leads_list
        }
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'delete', self.host + "/rest/v1/lists/" + str(listId) + "/leads.json", args, data)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def member_of_list(self, listId, id):
        self.authenticate()
        if listId is None:
            raise ValueError(
                "Invalid argument: required argument listId is none.")
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        leads_list = [{'id': items} for items in id]
        data = {
            'input': leads_list
        }
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        result = self._api_call('post', self.host + "/rest/v1/lists/" +
                                str(listId) + "/leads/ismember.json", args, data)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    # --------- SMART LISTS ---------

    def get_smart_list_by_id(self, id, includeRules=False, return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if includeRules:
            args['includeRules'] = includeRules
        result = self._api_call('get', self.host + "/rest/asset/v1/smartList/{}.json".format(id), args)
        if result is None:
            raise Exception("Empty Response")
        if return_full_result:
            return result
        else:
            return result['result']

    def get_smart_list_by_name(self, name, return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'name': name
        }
        result = self._api_call('get', self.host + "/rest/asset/v1/smartList/byName.json".format(id), args)
        if result is None:
            raise Exception("Empty Response")
        if return_full_result:
            return result
        else:
            return result['result']

    def get_smart_lists(self, earliestUpdatedAt=None, latestUpdatedAt=None, folderId=None, folderType=None,
                        maxReturn=200, offset=0, return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'maxReturn': maxReturn,
            'offset': offset,
        }
        if earliestUpdatedAt:
            args['earliestUpdatedAt'] = earliestUpdatedAt
        if latestUpdatedAt:
            args['latestUpdatedAt'] = latestUpdatedAt
        if folderId and folderType:
            args['folder'] = json.dumps({'id': folderId, 'type': folderType})
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('get', self.host + "/rest/asset/v1/smartLists.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) < maxReturn:
                    break
            else:
                break
            offset += maxReturn
            args['offset'] = offset

    def delete_smart_list(self, id, return_full_result=False):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/smartList/" + str(id) + "/delete.json", args)
        if result is None:
            raise Exception("Empty Response")
        if return_full_result:
            return result
        else:
            return result['result']

    def clone_smart_list(self, id, name, folderId, folderType, return_full_result=False, description=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError(
                "Invalid argument: required argument folder is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description:
            args['description'] = description
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/smartList/" + str(id) + "/clone.json", args)
        if result is None:
            raise Exception("Empty Response")
        if return_full_result:
            return result
        else:
            return result['result']

    # --------- SMART CAMPAIGNS ---------

    def get_smart_campaign_by_id(self, id):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call('get', self.host + "/rest/asset/v1/smartCampaign/{}.json".format(id), args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_smart_campaign_by_name(self, name):
        self.authenticate()
        if name is None:
            raise ValueError("Invalid argument: required argument 'name' is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        result = self._api_call('get', self.host + "/rest/asset/v1/smartCampaign/byName.json".format(id), args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_smart_campaigns(self, earliestUpdatedAt=None, latestUpdatedAt=None, folderId=None, folderType=None,
                            maxReturn=200, offset=0, return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'maxReturn': maxReturn,
            'offset': offset
        }
        if earliestUpdatedAt:
            args['earliestUpdatedAt'] = earliestUpdatedAt
        if latestUpdatedAt:
            args['latestUpdatedAt'] = latestUpdatedAt
        if folderId and folderType:
            args['folder'] = json.dumps({'id': folderId, 'type': folderType})
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('get', self.host + "/rest/asset/v1/smartCampaigns.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) < maxReturn:
                    break
            else:
                break
            offset += maxReturn
            args['offset'] = offset

    def get_campaign_by_id(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token,
            'id': id
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/campaigns/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_multiple_campaigns(self, id=None, name=None, programName=None, workspaceName=None, batchSize=None):
        self.authenticate()
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        if id is not None:
            data = [('id', items) for items in id]
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
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'post', self.host + "/rest/v1/campaigns.json", args, data, mode='nojsondumps')
            if result is None:
                raise Exception("Empty Response")
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def schedule_campaign(self, id, runAt=None, cloneToProgramName=None, tokens=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
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
            token_list = [{'name': '{{' + k + '}}', 'value': v}
                          for k, v in tokens.items()]
            data['input']['tokens'] = token_list
        result = self._api_call(
            'post', self.host + "/rest/v1/campaigns/" + str(id) + "/schedule.json", args, data)
        return result['success']

    def request_campaign(self, id, leads, tokens=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if leads is None:
            raise ValueError(
                "Invalid argument: required argument leads is none.")
        args = {
            'access_token': self.token
        }
        leads_list = [{'id': items} for items in leads]
        if tokens is not None:
            token_list = [{'name': '{{' + k + '}}', 'value': v}
                          for k, v in tokens.items()]
            data = {
                'input': {'leads':
                          leads_list,
                          'tokens':
                          token_list
                          }
            }
        else:
            data = {
                'input': {'leads':
                          leads_list
                          }
            }
        result = self._api_call(
            'post', self.host + "/rest/v1/campaigns/" + str(id) + "/trigger.json", args, data)
        return result['success']

    def activate_smart_campaign(self, id):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call('post', self.host + "/rest/asset/v1/smartCampaign/{}/activate.json".format(id), args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def deactivate_smart_campaign(self, id):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call('post', self.host + "/rest/asset/v1/smartCampaign/{}/deactivate.json".format(id), args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def create_smart_campaign(self, name, folderId, folderType, description=None):
        self.authenticate()
        if name is None:
            raise ValueError("Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError("Invalid argument: required argument folderId is none.")
        if folderType not in ['Folder', 'Program']:
            raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'")
        args = {
            'access_token': self.token
        }
        data = {
            'name': name,
            'folder': json.dumps({
                'id': folderId,
                'type': folderType
            })
        }
        if description is not None:
            data['description'] = description
        result = self._api_call('post', self.host + "/rest/asset/v1/smartCampaigns.json", args, data,
                                mode='nojsondumps')
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_smart_campaign(self, id, name, description=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument 'id' is none.")
        if name is None:
            raise ValueError("Invalid argument: required argument 'name' is none.")
        args = {
            'access_token': self.token,
        }
        data = {
            'name': name
        }
        if description is not None:
            data['description'] = description
        result = self._api_call('post', self.host + "/rest/asset/v1/smartCampaign/{}.json".format(id), args, data,
                                mode='nojsondumps')
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def clone_smart_campaign(self, id, folderId, folderType, name, isExecutable=False, description=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument 'id' is none.")
        if name is None:
            raise ValueError("Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError("Invalid argument: required argument folderId is none.")
        if folderType not in ['Folder', 'Program']:
            raise ValueError("Invalid argument: folderType should be 'Folder' or 'Program'")
        args = {
            'access_token': self.token,
        }
        data = {
            'name': name,
            'folder': json.dumps({
                'id': folderId,
                'type': folderType
            })
        }
        if description is not None:
            data['description'] = description
        if isExecutable:
            data['isExecutable'] = isExecutable
        result = self._api_call('post', self.host + "/rest/asset/v1/smartCampaign/{}/clone.json".format(id), args, data,
                                mode='nojsondumps')
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_smart_campaign(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument 'id' is none.")
        args = {
            'access_token': self.token,
        }
        result = self._api_call('post', self.host + "/rest/asset/v1/smartCampaign/{}/delete.json".format(id), args,
                                mode='nojsondumps')
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_smart_list_by_smart_campaign_id(self, id, includeRules=True, return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'includeRules': includeRules
        }
        result = self._api_call('get', self.host + "/rest/asset/v1/smartCampaign/{}/smartList.json".format(id), args)
        if result is None:
            raise Exception("Empty Response")
        if return_full_result:
            return result
        else:
            return result['result']

    # --------- IMPORT LEADS ---------

    def import_lead(self, format, file, lookupField=None, listId=None, partitionName=None):
        self.authenticate()
        if format is None:
            raise ValueError(
                "Invalid argument: required argument format is none.")
        if file is None:
            raise ValueError(
                "Invalid argument: required argument file is none.")
        args = {
            'access_token': self.token,
            'format': format
        }
        if lookupField is not None:
            args['lookupField'] = lookupField
        if listId is not None:
            args['listId'] = listId
        if partitionName is not None:
            args['partitionName'] = partitionName
        result = self._api_call(
            'post', self.host + "/bulk/v1/leads.json", args, files=file, filename="file")
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_import_lead_status(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/bulk/v1/leads/batch/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_import_failure_file(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call('get', self.host + "/bulk/v1/leads/batch/" +
                                str(id) + "/failures.json", args, mode='nojson')
        if result is None:
            raise Exception("Empty Response")
        return result.text

    def get_import_warning_file(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call('get', self.host + "/bulk/v1/leads/batch/" +
                                str(id) + "/warnings.json", args, mode='nojson')
        if result is None:
            raise Exception("Empty Response")
        return result.text

    # --------- DESCRIBE ---------

    def describe(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/leads/describe.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def describe2(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/leads/describe2.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def describe_program_member(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/programs/members/describe.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    # --------- ACTIVITIES ---------

    def get_activity_types(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/activities/types.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_paging_token(self, sinceDatetime):
        self.authenticate()
        args = {
            'access_token': self.token,
            'sinceDatetime': sinceDatetime
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/activities/pagingtoken.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['nextPageToken']

    def process_lead_activity_until_datetime(self, result, untilDatetime):
        latest_until_date = result[len(result)-1]['activityDate']
        result_until = datetime.strptime(latest_until_date, '%Y-%m-%dT%H:%M:%SZ')
        try:
            specified_until = datetime.strptime(untilDatetime, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            try:
                specified_until = datetime.strptime(untilDatetime, '%Y-%m-%d')
            except ValueError:
                if ":" == untilDatetime[-3]:  # in Python 3.6 and earlier a colon is not allowed in timezone offset
                    untilDatetime = untilDatetime[:-3] + untilDatetime[-2:]
                specified_until = datetime.strptime(untilDatetime, '%Y-%m-%dT%H:%M:%S%z')
                utc = pytz.UTC
                result_until = utc.localize(result_until)
        if result_until > specified_until:
            partial_result = []
            for record in result:
                try:
                    if datetime.strptime(record['activityDate'], '%Y-%m-%dT%H:%M:%SZ') <= specified_until:
                        partial_result.append(record)
                except TypeError as e:
                    utc = pytz.UTC
                    if utc.localize(datetime.strptime(record['activityDate'], '%Y-%m-%dT%H:%M:%SZ')) <= specified_until:
                        partial_result.append(record)
            return partial_result
        return result

    def get_lead_activities(self, activityTypeIds, nextPageToken=None, sinceDatetime=None, untilDatetime=None,
                            batchSize=None, listId=None, leadIds=None, assetIds=None):
        self.authenticate()
        if activityTypeIds is None:
            raise ValueError(
                "Invalid argument: required argument activityTypeIds is none.")
        if nextPageToken is None and sinceDatetime is None:
            raise ValueError(
                "Either nextPageToken or sinceDatetime needs to be specified.")
        activityTypeIds = activityTypeIds.split() if type(
            activityTypeIds) is str else activityTypeIds
        args = {
            'access_token': self.token,
            'activityTypeIds': ",".join(activityTypeIds),
        }
        if listId is not None:
            args['listId'] = listId
        if leadIds is not None:
            args['leadIds'] = leadIds
        if assetIds:
            args['assetIds'] = assetIds
        if batchSize is not None:
            args['batchSize'] = batchSize
        if nextPageToken is None:
            nextPageToken = self.get_paging_token(sinceDatetime=sinceDatetime)
        args['nextPageToken'] = nextPageToken
        result_list = []
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/v1/activities.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result and result['result']:
                if untilDatetime is not None:
                    new_result = self.process_lead_activity_until_datetime(result['result'], untilDatetime)
                    if new_result:
                        result_list.extend(new_result)
                        if len(new_result) < len(result['result']):
                            break  # in case only some of the results meet the datetime criteria (most common)
                    else:
                        break  # in case none of the results meet the datetime criteria
                else:
                    result_list.extend(result['result'])
            if result['moreResult'] is False:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def get_lead_activities_yield(self, activityTypeIds, nextPageToken=None, sinceDatetime=None, untilDatetime=None,
                                  batchSize=None, listId=None, leadIds=None, assetIds=None, return_full_result=False,
                                  max_empty_more_results=None):
        self.authenticate()
        if activityTypeIds is None:
            raise ValueError(
                "Invalid argument: required argument activityTypeIds is none.")
        if nextPageToken is None and sinceDatetime is None:
            raise ValueError(
                "Either nextPageToken or sinceDatetime needs to be specified.")
        activityTypeIds = activityTypeIds.split() if type(
            activityTypeIds) is str else activityTypeIds
        args = {
            'access_token': self.token,
            'activityTypeIds': ",".join(activityTypeIds),
        }
        if listId is not None:
            args['listId'] = listId
        if leadIds is not None:
            args['leadIds'] = leadIds
        if assetIds:
            args['assetIds'] = assetIds
        if batchSize is not None:
            args['batchSize'] = batchSize
        if nextPageToken is None:
            nextPageToken = self.get_paging_token(sinceDatetime=sinceDatetime)
        args['nextPageToken'] = nextPageToken
        empty_more_results_count = 0  # counts how many times moreResults=True without results
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/v1/activities.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result and result['result']:
                if untilDatetime is not None:
                    new_result = self.process_lead_activity_until_datetime(result['result'], untilDatetime)
                    if new_result:
                        if return_full_result:
                            result['result'] = new_result
                            yield result
                        else:
                            yield new_result
                        if len(new_result) < len(result['result']):
                            break  # in case only some of the results meet the datetime criteria (most common)
                    else:
                        break  # in case none of the results meet the datetime criteria
                else:
                    if return_full_result:
                        yield result
                    else:
                        yield result['result']
                empty_more_results_count = 0
            elif result['moreResult']:
                empty_more_results_count += 1
            if result['moreResult'] is False:
                break
            if max_empty_more_results and empty_more_results_count >= max_empty_more_results:
                # if maxResults=True but there are no results yet, this is a way to interrupt the loop after x loops
                break
            args['nextPageToken'] = result['nextPageToken']

    def get_lead_changes(self, fields, nextPageToken=None, sinceDatetime=None, untilDatetime=None, batchSize=None,
                         listId=None):
        self.authenticate()
        if fields is None:
            raise ValueError(
                "Invalid argument: required argument fields is none.")
        if nextPageToken is None and sinceDatetime is None:
            raise ValueError(
                "Either nextPageToken or sinceDatetime needs to be specified.")
        fields = fields.split() if type(fields) is str else fields
        args = {
            'access_token': self.token,
            'fields': ",".join(fields),
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
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/v1/activities/leadchanges.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result and result['result']:
                if untilDatetime is not None:
                    new_result = self.process_lead_activity_until_datetime(result['result'], untilDatetime)
                    if new_result:
                        result_list.extend(new_result)
                        if len(new_result) < len(result['result']):
                            break  # in case only some of the results meet the datetime criteria (most common)
                    else:
                        break  # in case none of the results meet the datetime criteria
                else:
                    result_list.extend(result['result'])
            if result['moreResult'] is False:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def get_lead_changes_yield(self, fields, nextPageToken=None, sinceDatetime=None, untilDatetime=None, batchSize=None,
                               listId=None, leadIds=None, return_full_result=False, max_empty_more_results=None):
        self.authenticate()
        if fields is None:
            raise ValueError(
                "Invalid argument: required argument fields is none.")
        if nextPageToken is None and sinceDatetime is None:
            raise ValueError(
                "Either nextPageToken or sinceDatetime needs to be specified.")
        fields = fields.split() if type(fields) is str else fields
        args = {
            'access_token': self.token,
            'fields': ",".join(fields),
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
        empty_more_results_count = 0  # counts how many times moreResults=True without results
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/v1/activities/leadchanges.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result and result['result']:
                if untilDatetime is not None:
                    new_result = self.process_lead_activity_until_datetime(
                        result['result'], untilDatetime)
                    if new_result:
                        if return_full_result:
                            result['result'] = new_result
                            yield result
                        else:
                            yield new_result
                        if len(new_result) < len(result['result']):
                            break  # in case only some of the results meet the datetime criteria (most common)
                    else:
                        break  # in case none of the results meet the datetime criteria
                else:
                    if return_full_result:
                        yield result
                    else:
                        yield result['result']
                empty_more_results_count = 0
            elif result['moreResult']:
                empty_more_results_count += 1
            if result['moreResult'] is False:
                break
            if max_empty_more_results and empty_more_results_count >= max_empty_more_results:
                # if maxResults=True but there are no results yet, this is a way to interrupt the loop after x loops
                break
            args['nextPageToken'] = result['nextPageToken']

    def add_custom_activities(self, input):
        self.authenticate()
        if input is None:
            raise ValueError(
                "Invalid argument: required argument input is none.")
        args = {
            'access_token': self.token
        }
        data = {
            "input": input
        }
        result = self._api_call(
            'post', self.host + "/rest/v1/activities/external.json", args, data)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    # --------- USAGE ---------

    def get_daily_usage(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/stats/usage.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_last_7_days_usage(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/stats/usage/last7days.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_daily_errors(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/stats/errors.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_last_7_days_errors(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/stats/errors/last7days.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    # --------- VARIOUS ---------

    def delete_lead(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        leads_list = [{'id': items} for items in id]
        data = {
            'input': leads_list
        }
        args = {
            'access_token': self.token
        }
        result = self._api_call('delete', self.host +
                                "/rest/v1/leads.json", args, data)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_deleted_leads(self, nextPageToken=None, sinceDatetime=None, batchSize=None):
        self.authenticate()
        if nextPageToken is None and sinceDatetime is None:
            raise ValueError(
                "Either nextPageToken or sinceDatetime needs to be specified.")
        args = {
            'access_token': self.token
        }
        if batchSize is not None:
            args['batchSize'] = batchSize
        if nextPageToken is None:
            nextPageToken = self.get_paging_token(sinceDatetime=sinceDatetime)
        args['nextPageToken'] = nextPageToken
        result_list = []
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/v1/activities/deletedleads.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                result_list.extend(result['result'])
            if result['moreResult'] is False:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def update_leads_partition(self, input):
        self.authenticate()
        if input is None:
            raise ValueError(
                "Invalid argument: required argument input is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'input': []
        }
        for lead in input:
            data['input'].append(lead)
        result = self._api_call(
            'post', self.host + "/rest/v1/leads/partitions.json", args, data)
        return result['result']

    def submit_form(self, formId, input):
        self.authenticate()
        if formId is None:
            raise ValueError("Invalid argument: required argument formId is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'formId': int(formId),
            'input': [
                input
            ],
        }
        result = self._api_call('post', self.host +
                                "/rest/v1/leads/submitForm.json", args, data)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    # --------- FOLDERS ---------

    def create_folder(self, name, parentId, parentType, description=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if parentId is None:
            raise ValueError(
                "Invalid argument: required argument parentId is none.")
        if parentType is None:
            raise ValueError(
                "Invalid argument: parentType should be 'Folder' or 'Parent'")
        args = {
            'access_token': self.token,
            'name': name,
            'parent': "{'id': " + str(parentId) + ", 'type': " + parentType + "}"
        }
        if description is not None:
            args['description'] = description
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/folders.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_folder_by_id(self, id, type):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if type is None:
            raise ValueError(
                "Invalid argument: required argument type is none.")
        args = {
            'access_token': self.token,
            'type': type
        }
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/folder/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_folder_by_name(self, name, type=None, root=None, workSpace=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        if type is not None:
            args['type'] = type
        if root is not None:
            args['root'] = root
        if workSpace is not None:
            args['workSpace'] = workSpace
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/folder/byName.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_folder_contents(self, id, type, maxReturn=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if type is None:
            raise ValueError(
                "Invalid argument: required argument type is none.")
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
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/asset/v1/folder/" + str(id) + "/content.json", args)
            if result is None:
                raise Exception("Empty Response")
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
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
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
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/folder/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_folder(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token,
            'type': 'Folder'
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/folder/" + str(id) + "/delete.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def browse_folders(self, root=None, maxDepth=None, maxReturn=None, workSpace=None):
        self.authenticate()
        args = {
            'access_token': self.token,
            'root': root
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
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/asset/v1/folders.json", args)
            if result is None:
                raise Exception("Empty Response")
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

    def browse_folders_yield(self, root=None, maxDepth=None, maxReturn=20, workSpace=None, offset=0,
                             return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'root': root,
            'offset': offset,
            'maxReturn': maxReturn
        }
        if maxDepth is not None:
            args['maxDepth'] = maxDepth
        if workSpace is not None:
            args['workSpace'] = workSpace
        while True:
            self.authenticate()
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/asset/v1/folders.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) < maxReturn:
                    break
            else:
                break
            offset += maxReturn
            args['offset'] = offset

    # --------- TOKENS ---------

    def create_token(self, id, folderType, type, name, value):
        self.authenticate()
        assert id and folderType and type and name and value
        args = {
            'access_token': self.token
        }
        data = {
            'folderType': folderType,
            'type': type,
            'name': name,
            'value': value
        }
        result = self._api_call(
            'post',
            "{}/rest/asset/v1/folder/{}/tokens.json".format(self.host, id),
            args, data, mode="nojsondumps")
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_tokens(self, id, folderType):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'folderType': folderType
        }
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/folder/" + str(id) + "/tokens.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_tokens(self, id, folderType, name, type):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: folderType should be 'Folder' or 'Program'.")
        if type is None:
            raise ValueError(
                "Invalid argument: required argument type is none.")
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'folderType': folderType,
            'name': name,
            'type': type
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/folder/" + str(id) + "/tokens/delete.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    # --------- EMAIL TEMPLATES ---------

    def create_email_template(self, name, folderId, folderType, content, description=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError(
                "Invalid argument: required argument folder is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: folderType should be 'Folder' or 'Program'.")
        if content is None:
            raise ValueError(
                "Invalid argument: required argument content is none.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description is not None:
            args['description'] = description
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/emailTemplates.json", args, files=content, filename="content")
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_email_template_by_id(self, id, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/emailTemplate/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_email_template_by_name(self, name, status=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/emailTemplate/byName.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_email_template(self, id, name=None, description=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if name is not None:
            args['name'] = name
        if description is not None:
            args['description'] = description
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/emailTemplate/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_email_template(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/emailTemplate/" + str(id) + "/delete.json", args)
        if result is None:
            raise Exception("Empty Response")
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
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/asset/v1/emailTemplates.json", args)
            if result is None:
                raise Exception("Empty Response")
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

    def get_email_templates_yield(self, offset=0, maxReturn=20, status=None, return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'maxReturn': maxReturn,
            'offset': offset
        }
        if status is not None:
            args['status'] = status
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('get', self.host + "/rest/asset/v1/emailTemplates.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) < maxReturn:
                    break
            else:
                break
            offset += maxReturn
            args['offset'] = offset

    def get_email_template_used_by(self, id, maxReturn=None):
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
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/asset/v1/emailTemplates/" + str(id) + "/usedBy.json", args)
            if result is None:
                raise Exception("Empty Response")
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
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/emailTemplate/" + str(id) + "/content", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_email_template_content(self, id, content):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if content is None:
            raise ValueError(
                "Invalid argument: required argument content is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call('post', self.host + "/rest/asset/v1/emailTemplate/" + str(id) + "/content.json", args,
                                files=content, filename="content")
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def approve_email_template(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/emailTemplate/" + str(id) + "/approveDraft.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def unapprove_email_template(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/emailTemplate/" + str(id) + "/unapprove.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def discard_email_template_draft(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/emailTemplate/" + str(id) + "/discardDraft.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def clone_email_template(self, id, name, folderId, folderType):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError(
                "Invalid argument: required argument folder is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/emailTemplate/" + str(id) + "/clone.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    # --------- EMAILS ---------

    def create_email(self, name, folderId, folderType, template, description=None, subject=None, fromName=None,
                     fromEmail=None, replyEmail=None, operational=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError(
                "Invalid argument: required argument folder is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: folderType should be 'Folder' or 'Program'.")
        if template is None:
            raise ValueError(
                "Invalid argument: required argument template is none.")
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
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/emails.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_email_by_id(self, id, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/email/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_email_by_name(self, name, status=None, folderId=None, folderType=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        if status is not None:
            args['status'] = status
        if folderId is not None:
            args['folder'] = "{'id': " + \
                str(folderId) + ", 'type': " + folderType + "}"
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/email/byName.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_email(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/email/" + str(id) + "/delete.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_email(self, id, name=None, description=None, preHeader=None, operational=None, published=None, textOnly=None, webView=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if name is not None:
            args['name'] = name
        if description is not None:
            args['description'] = description
        if preHeader is not None:
            args['preHeader'] = preHeader
        if operational is not None:
            args['operational'] = operational
        if published is not None:
            args['published'] = published
        if textOnly is not None:
            args['textOnly'] = textOnly
        if webView is not None:
            args['webView'] = webView
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/email/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
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
            args['folder'] = "{'id': " + \
                str(folderId) + ", 'type': " + folderType + "}"
        result_list = []
        offset = 0
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/asset/v1/emails.json", args)
            if result is None:
                raise Exception("Empty Response")
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

    def get_emails_yield(self, offset=0, maxReturn=20, status=None, folderId=None, folderType=None,
                         return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'maxReturn': maxReturn,
            'offset': offset
        }
        if status:
            args['status'] = status
        if folderId and folderType:
            args['folder'] = json.dumps({'id': folderId, 'type': folderType})
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('get', self.host + "/rest/asset/v1/emails.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
            else:
                break
            offset += maxReturn
            args['offset'] = offset

    def get_email_content(self, id, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/email/" + str(id) + "/content.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_email_content(self, id, type, subject=None, fromName=None, fromEmail=None, replyTo=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if type != "Text" and type != "DynamicContent":
            raise ValueError("Invalid argument: type should be "
                             "'Text' or 'DynamicContent'.")
        args = {
            'access_token': self.token
        }
        if subject is not None:
            args['subject'] = '{"type":"' + type + \
                '","value":"' + str(subject) + '"}'
        if fromName is not None:
            args['fromName'] = '{"type":"' + type + \
                '","value":"' + str(fromName) + '"}'
        if fromEmail is not None:
            args['fromEmail'] = '{"type":"' + type + \
                '","value":"' + str(fromEmail) + '"}'
        if replyTo is not None:
            args['replyTO'] = '{"type":"' + type + \
                '","value":"' + str(replyTo) + '"}'
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/email/" + str(id) + "/content.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_email_content_in_editable_section(self, id, htmlId, type, value, textValue=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if htmlId is None:
            raise ValueError(
                "Invalid argument: required argument htmlId is none.")
        if type != "Text" and type != "DynamicContent" and type != "Snippet":
            raise ValueError(
                "Invalid argument: type should be 'Text', 'DynamicContent' or 'Snippet'.")
        if value is None:
            raise ValueError(
                "Invalid argument: required argument value is none.")
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
        result = self._api_call('post', self.host + "/rest/asset/v1/email/" + str(id) + "/content/" + str(htmlId) +
                                ".json", args, data, mode='nojsondumps')
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_email_dynamic_content(self, id, dynamicContentId, status):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if dynamicContentId is None:
            raise ValueError(
                "Invalid argument: required argument dynamicContentId is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call('get', self.host + "/rest/asset/v1/email/" + str(id) + "/dynamicContent/" +
                                str(dynamicContentId) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_email_dynamic_content(self, id, dynamicContentId, segment, value, type, data_method='data'):
        # including the parameters as form fields has encoding issues for plain text and for the subject/from name, etc.
        # including them as URL arguments doesn't have those encoding issues; need to fix this issue in a better way
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if dynamicContentId is None:
            raise ValueError(
                "Invalid argument: required argument dynamicContentId is none.")
        if segment is None:
            raise ValueError(
                "Invalid argument: required argument segment is none.")
        if value is None:
            raise ValueError(
                "Invalid argument: required argument value is none.")
        if type is None:
            raise ValueError(
                "Invalid argument: required argument type is none.")
        args = {
            'access_token': self.token
        }
        if data_method == 'args':
            args['segment'] = segment
            args['value'] = value
            args['type'] = type
            data = None
        else:
            if isinstance(value, str):
                value = value.encode('ascii', 'xmlcharrefreplace')
            data = {
                'segment': segment,
                'value': value,
                'type': type
            }
        result = self._api_call('post', self.host + "/rest/asset/v1/email/" + str(id) + "/dynamicContent/" +
                                str(dynamicContentId) + ".json", args, data, mode='nojsondumps')
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def approve_email(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/email/" + str(id) + "/approveDraft.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def unapprove_email(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/email/" + str(id) + "/unapprove.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def discard_email_draft(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/email/" + str(id) + "/discardDraft.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def clone_email(self, id, name, folderId, folderType, description=None, operational=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError(
                "Invalid argument: required argument folder is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description is not None:
            args['description'] = description
        if operational is not None:
            args['operational'] = operational
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/email/" + str(id) + "/clone.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def send_sample_email(self, id, emailAddress, textOnly=None, leadId=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if emailAddress is None:
            raise ValueError(
                "Invalid argument: required argument emailAddress is none.")
        args = {
            'access_token': self.token,
            'emailAddress': emailAddress
        }
        if textOnly is not None:
            args['textOnly'] = textOnly
        if leadId is not None:
            args['leadId'] = leadId
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/email/" + str(id) + "/sendSample.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_email_full_content(self, id, status=None, leadId=None, type=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        if leadId is not None:
            args['leadId'] = leadId
        if type is not None:
            args['type'] = type
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/email/" + str(id) + "/fullContent.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_email_full_content(self, id, content):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if content is None:
            raise ValueError("Invalid argument: required argument content is none.")
        args = {
            'access_token': self.token,
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/email/" + str(id) + "/fullContent.json", args, files=content, filename="content")
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_email_variables(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/email/" + str(id) + "/variables.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result.get('result')

    def update_email_variable(self, id, name, value, moduleId):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if name is None:
            raise ValueError("Invalid argument: required argument name is none.")
        if value is None:
            raise ValueError("Invalid argument: required argument 'value' is none.")
        if moduleId is None:
            raise ValueError("Invalid argument: required argument moduleId is none.")
        args = {
            'access_token': self.token,
        }
        data = {
            'value': value,
            'moduleId': moduleId
        }
        result = self._api_call('post', self.host + "/rest/asset/v1/email/" + str(id) + "/variable/" + name + ".json",
                                args, data, mode='nojsondumps')
        if result is None:
            raise Exception("Empty Response")
        return result['result']


    # -------LANDING PAGES ---------#

    def create_landing_page(self, name, folderId, folderType, template, description=None, title=None, keywords=None,
                            robots=None, customHeadHTML=None, facebookOgTags=None, prefillForm=None, mobileEnabled=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError(
                "Invalid argument: required argument folder is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: folderType should be 'Folder' or 'Program'.")
        if template is None:
            raise ValueError(
                "Invalid argument: required argument template is none.")
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
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/landingPages.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_landing_page_by_id(self, id, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/landingPage/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_landing_page_by_name(self, name, status=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/landingPage/byName.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_landing_page(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/landingPage/" + str(id) + "/delete.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_landing_page(self, id, name=None, description=None, title=None, keywords=None,
                            robots=None, customHeadHTML=None, facebookOgTags=None, prefillForm=None, mobileEnabled=None,
                            styleOverRide=None, urlPageName=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
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
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/landingPage/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
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
            args['folder'] = "{'id': " + \
                str(folderId) + ", 'type': " + folderType + "}"
        result_list = []
        offset = 0
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/asset/v1/landingPages.json", args)
            if result is None:
                raise Exception("Empty Response")
            #if not result['success']: raise MarketoException(result['errors'][0] + ". Request ID: " + result['requestId'])
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

    def get_landing_pages_yield(self, offset=0, maxReturn=20, status=None, folderId=None, folderType=None,
                                return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'maxReturn': maxReturn,
            'offset': offset
        }
        if status is not None:
            args['status'] = status
        if folderId is not None:
            args['folder'] = json.dumps({'id': folderId, 'type': folderType})
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('get', self.host + "/rest/asset/v1/landingPages.json", args)
            if result is None:
                raise Exception("Empty Response")
            #if not result['success']: raise MarketoException(result['errors'][0] + ". Request ID: " + result['requestId'])
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) < maxReturn:
                    break
            else:
                break
            offset += maxReturn
            args['offset'] = offset

    def get_landing_page_content(self, id, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/landingPage/" + str(id) + "/content.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def create_landing_page_content_section(self, id, type, value, backgroundColor=None, borderColor=None,
                                            borderStyle=None, borderWidth=None, height=None, zIndex=None, left=None,
                                            opacity=None, top=None, width=None, hideDesktop=None, hideMobile=None,
                                            contentId=None, imageOpenNewWindow=None, linkUrl=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if type is None:
            raise ValueError(
                "Invalid argument: required argument type is none.")
        if value is None:
            raise ValueError(
                "Invalid argument: required argument value is none.")
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
        if zIndex is not None:
            data['layer'] = zIndex
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
        if imageOpenNewWindow is not None:
            data['imageOpenNewWindow'] = imageOpenNewWindow
        if linkUrl is not None:
            data['linkUrl'] = linkUrl
        result = self._api_call('post', self.host + "/rest/asset/v1/landingPage/" + str(id) + "/content.json", args,
                                data, mode='nojsondumps')
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_landing_page_content_section(self, id, contentId, type, value, index=None, backgroundColor=None,
                                            borderColor=None, borderStyle=None, borderWidth=None, height=None,
                                            zIndex=None, left=None, opacity=None, top=None, width=None, hideDesktop=None,
                                            hideMobile=None, imageOpenNewWindow=None, linkUrl=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if contentId is None:
            raise ValueError(
                "Invalid argument: required argument contentId is none.")
        if type is None:
            raise ValueError(
                "Invalid argument: required argument type is none.")
        if value is None:
            raise ValueError(
                "Invalid argument: required argument value is none.")
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
        if zIndex is not None:
            data['layer'] = zIndex
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
        if imageOpenNewWindow is not None:
            data['imageOpenNewWindow'] = imageOpenNewWindow
        if linkUrl is not None:
            data['linkUrl'] = linkUrl
        result = self._api_call('post', self.host + "/rest/asset/v1/landingPage/" + str(id) + "/content/" + str(contentId) +
                                ".json", args, data, mode='nojsondumps')
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_landing_page_content_section(self, id, contentId):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if contentId is None:
            raise ValueError(
                "Invalid argument: required argument contentId is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call('post', self.host + "/rest/asset/v1/landingPage/" + str(id) + "/content/" + str(contentId) +
                                "/delete.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_landing_page_dynamic_content(self, id, dynamicContentId, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if dynamicContentId is None:
            raise ValueError(
                "Invalid argument: required argument dynamicContentId is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call('get', self.host + "/rest/asset/v1/landingPage/" + str(id) + "/dynamicContent/" +
                                str(dynamicContentId) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_landing_page_dynamic_content(self, id, dynamicContentId, segment, value, type, index=None,
                                            backgroundColor=None, borderColor=None, borderStyle=None, borderWidth=None,
                                            height=None, zIndex=None, left=None, opacity=None, top=None, width=None,
                                            hideDesktop=None, hideMobile=None, imageOpenNewWindow=None, linkUrl=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if dynamicContentId is None:
            raise ValueError(
                "Invalid argument: required argument dynamicContentId is none.")
        if segment is None:
            raise ValueError(
                "Invalid argument: required argument segment is none.")
        if value is None:
            raise ValueError(
                "Invalid argument: required argument value is none.")
        if type is None:
            raise ValueError(
                "Invalid argument: required argument type is none.")
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
        if zIndex is not None:
            data['layer'] = zIndex
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
        if imageOpenNewWindow is not None:
            data['imageOpenNewWindow'] = imageOpenNewWindow
        if linkUrl is not None:
            data['linkUrl'] = linkUrl
        result = self._api_call('post', self.host + "/rest/asset/v1/landingPage/" + str(id) + "/dynamicContent/" +
                                str(dynamicContentId) + ".json", args, data, mode='nojsondumps')
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def approve_landing_page(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/landingPage/" + str(id) + "/approveDraft.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def unapprove_landing_page(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/landingPage/" + str(id) + "/unapprove.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def discard_landing_page_draft(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/landingPage/" + str(id) + "/discardDraft.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def clone_landing_page(self, id, name, folderId, folderType, description=None, template=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError(
                "Invalid argument: required argument folder is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description is not None:
            args['description'] = description
        if template is not None:
            args['template'] = template
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/landingPage/" + str(id) + "/clone.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_landing_page_variables(self, id, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/landingPage/" + str(id) + "/variables.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result.get('result')

    def get_landing_page_full_content(self, id, leadId=None, segmentation=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if leadId is not None:
            args['leadId'] = leadId
        if segmentation is not None:
            args['segmentation'] = segmentation
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/landingPage/" + str(id) + "/fullContent.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_landing_page_redirect_rules(self, maxReturn=20, offset=0, redirectTolandingPageId=None,
                                        redirectToPath=None, earliestUpdatedAt=None, latestUpdatedAt=None,
                                        return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'maxReturn': maxReturn,
            'offset': offset
        }
        if redirectTolandingPageId is not None:
            args['redirectTolandingPageId'] = redirectTolandingPageId
        if redirectToPath is not None:
            args['redirectToPath'] = redirectToPath
        if earliestUpdatedAt is not None:
            args['earliestUpdatedAt'] = earliestUpdatedAt
        if latestUpdatedAt is not None:
            args['latestUpdatedAt'] = latestUpdatedAt
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('get', self.host + "/rest/asset/v1/redirectRules.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) < maxReturn:
                    break
            else:
                break
            offset += maxReturn
            args['offset'] = offset

    def get_landing_page_domains(self, maxReturn=20, offset=0, return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'maxReturn': maxReturn,
            'offset': offset
        }
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('get', self.host + "/rest/asset/v1/landingPageDomains.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) < maxReturn:
                    break
            else:
                break
            offset += maxReturn
            args['offset'] = offset

    # --------- FORMS ---------

    def create_form(self, name, folderId, folderType, description=None, language=None, locale=None,
                    progressiveProfiling=None, labelPosition=None, fontFamily=None, fontSize=None, knownVisitor=None,
                    theme=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError(
                "Invalid argument: required argument folder is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: folderType should be 'Folder' or 'Program'.")
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
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/forms.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_form_by_id(self, id, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/form/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_form_by_name(self, name, status=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/form/byName.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_form(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/form/" + str(id) + "/delete.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_form(self, id, name=None, description=None, language=None, locale=None, progressiveProfiling=None,
                    labelPosition=None, fontFamily=None, fontSize=None, knownVisitor=None, formTheme=None,
                    customcss=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
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
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/form/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
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
            args['folder'] = "{'id': " + \
                str(folderId) + ", 'type': " + folderType + "}"
        result_list = []
        offset = 0
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/asset/v1/forms.json", args)
            if result is None:
                raise Exception("Empty Response")
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

    def get_forms_yield(self, offset=0, maxReturn=20, status=None, folderId=None, folderType=None,
                        return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'maxReturn': maxReturn,
            'offset': offset
        }
        if status is not None:
            args['status'] = status
        if folderId is not None:
            args['folder'] = json.dumps({'id': folderId, 'type': folderType})
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('get', self.host + "/rest/asset/v1/forms.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) < maxReturn:
                    break
            else:
                break
            offset += maxReturn
            args['offset'] = offset

    def get_form_fields(self, id, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/form/" + str(id) + "/fields.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def create_form_field(self, id, fieldId, label=None, labelWidth=None, fieldWidth=None, instructions=None,
                          required=None, formPrefill=None, initiallyChecked=None, values=None, labelToRight=None,
                          hintText=None, defaultValue=None, minValue=None, maxValue=None, multiSelect=None,
                          maxLength=None, maskInput=None, visibleLines=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if fieldId is None:
            raise ValueError(
                "Invalid argument: required argument fieldId is none.")
        args = {
            'access_token': self.token,
            'fieldId': fieldId
        }
        if label is not None:
            args['label'] = label
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
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/form/" + str(id) + "/fields.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_form_field(self, id, fieldId, label=None, fieldType=None, labelWidth=None, fieldWidth=None, instructions=None,
                          required=None, formPrefill=None, initiallyChecked=None, values=None, labelToRight=None,
                          hintText=None, defaultValue=None, minValue=None, maxValue=None, multiSelect=None,
                          maxLength=None, maskInput=None, visibleLines=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if fieldId is None:
            raise ValueError(
                "Invalid argument: required argument fieldId is none.")
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
        result = self._api_call('post', self.host + "/rest/asset/v1/form/" + str(id) + "/field/" + str(fieldId) +
                                ".json", args, data, mode='nojsondumps')
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_form_field(self, id, fieldId):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if fieldId is None:
            raise ValueError(
                "Invalid argument: required argument contentId is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call('post', self.host + "/rest/asset/v1/form/" + str(id) + "/field/" + str(fieldId) +
                                "/delete.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def approve_form(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/form/" + str(id) + "/approveDraft.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def unapprove_form(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/form/" + str(id) + "/unapprove.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def discard_form_draft(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/form/" + str(id) + "/discardDraft.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def clone_form(self, id, name, folderId, folderType, description=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError(
                "Invalid argument: required argument folder is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description is not None:
            args['description'] = description
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/form/" + str(id) + "/clone.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_thank_you_page_by_form_id(self, id, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/form/" + str(id) + "/thankYouPage.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']


    # --------- FILES ---------

    def create_file(self, name, file, folder, description=None, insertOnly=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if file is None:
            raise ValueError(
                "Invalid argument: required argument file is none.")
        if folder is None:
            raise ValueError(
                "Invalid argument: required argument folder is none.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': folder
        }
        if description is not None:
            args['description'] = description
        if insertOnly is not None:
            args['insertOnly'] = insertOnly
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/files.json", args, files=file, filename="file")
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_file_by_id(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/file/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_file_by_name(self, name):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/file/byName.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def list_files(self, folder=None, maxReturn=None):
        self.authenticate()
        args = {
            'access_token': self.token
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
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/asset/v1/files.json", args)
            if result is None:
                raise Exception("Empty Response")
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

    def get_files_yield(self, offset=0, maxReturn=20, folderId=None, folderType=None, return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'maxReturn': maxReturn,
            'offset': offset
        }
        if folderId is not None:
            args['folder'] = json.dumps({'id': folderId, 'type': folderType})
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('get', self.host + "/rest/asset/v1/files.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) < maxReturn:
                    break
            else:
                break
            offset += maxReturn
            args['offset'] = offset

    def update_file_content(self, id, file):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if file is None:
            raise ValueError(
                "Invalid argument: required argument file is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call('post', self.host + "/rest/asset/v1/file/" + str(id) + "/content.json", args, files=file,
                                filename="file")
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    # --------- SNIPPETS ---------------

    def create_snippet(self, name, folderId, folderType, description=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError(
                "Invalid argument: required argument folder is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description is not None:
            args['description'] = description
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/snippets.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_snippet_by_id(self, id, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/snippet/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_snippet(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/snippet/" + str(id) + "/delete.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_snippet(self, id, name=None, description=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if name is not None:
            args['name'] = name
        if description is not None:
            args['description'] = description
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/snippet/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
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
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/asset/v1/snippets.json", args)
            if result is None:
                raise Exception("Empty Response")
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

    def get_snippets_yield(self, offset=0, maxReturn=20, status=None, return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'maxReturn': maxReturn,
            'offset': offset
        }
        if status is not None:
            args['status'] = status
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('get', self.host + "/rest/asset/v1/snippets.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) < maxReturn:
                    break
            else:
                break
            offset += maxReturn
            args['offset'] = offset

    def get_snippet_content(self, id, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/snippet/" + str(id) + "/content.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_snippet_content(self, id, type, content):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if type is None:
            raise ValueError(
                "Invalid argument: required argument type is none.")
        if content is None:
            raise ValueError(
                "Invalid argument: required argument content is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'type': type,
            'content': content
        }
        result = self._api_call('post', self.host + "/rest/asset/v1/snippet/" + str(id) + "/content.json", args, data,
                                mode='nojsondumps')
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def approve_snippet(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/snippet/" + str(id) + "/approveDraft.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def unapprove_snippet(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/snippet/" + str(id) + "/unapprove.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def discard_snippet_draft(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/snippet/" + str(id) + "/discardDraft.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def clone_snippet(self, id, name, folderId, folderType, description=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError(
                "Invalid argument: required argument folder is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description is not None:
            args['description'] = description
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/snippet/" + str(id) + "/clone.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_snippet_dynamic_content(self, id, segmentId, value=None, type=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if segmentId is None:
            raise ValueError(
                "Invalid argument: required argument segmentId is none.")
        args = {
            'access_token': self.token
        }
        if value is not None:
            args['value'] = value
        if type is not None:
            args['type'] = type
        result = self._api_call('post', self.host + "/rest/asset/v1/snippet/" + str(id) + "/dynamicContent/" +
                                str(segmentId) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_snippet_dynamic_content(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/snippet/" + str(id) + "/dynamicContent.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    # ----- SEGMENTATIONS -----

    def get_segmentations(self, status=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/segmentation.json", args)
        if result is None:
            raise Exception("Empty Response")
        if has_empty_warning(result):
            return []
        return result['result']

    def get_segments(self, id, maxReturn=200, status=None):
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        self.authenticate()
        args = {
            'access_token': self.token,
            'maxReturn': maxReturn
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/segmentation/" + str(id) + "/segments.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    # ----- LANDING PAGE TEMPLATES -----

    def create_landing_page_template(self, name, folderId, folderType, description=None, templateType=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError(
                "Invalid argument: required argument folder is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        if description is not None:
            args['description'] = description
        if templateType is not None:
            args['templateType'] = templateType
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/landingPageTemplates.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_landing_page_template_by_id(self, id, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_landing_page_template_by_name(self, name, status=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/landingPageTemplate/byName.json", args)
        if result is None:
            raise Exception("Empty Response")
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
            args['folder'] = "{'id': " + \
                str(folderId) + ", 'type': " + folderType + "}"
        result_list = []
        offset = 0
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/asset/v1/landingPageTemplates.json", args)
            if result is None:
                raise Exception("Empty Response")
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

    def get_landing_page_templates_yield(self, offset=0, maxReturn=20, status=None, folderId=None, folderType=None,
                                         return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'maxReturn': maxReturn,
            'offset': offset
        }
        if status is not None:
            args['status'] = status
        if folderId is not None and folderType is not None:
            args['folder'] = json.dumps({'id': folderId, 'type': folderType})
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('get', self.host + "/rest/asset/v1/landingPageTemplates.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) < maxReturn:
                    break
            else:
                break
            offset += maxReturn
            args['offset'] = offset

    def get_landing_page_template_content(self, id, status=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if status is not None:
            args['status'] = status
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + "/content.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_landing_page_template_content(self, id, content):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if content is None:
            raise ValueError(
                "Invalid argument: required argument content is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call('post', self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + "/content.json", args,
                                files=content, filename="content")
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_landing_page_template(self, id, name=None, description=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        if name is not None:
            args['name'] = name
        if description is not None:
            args['description'] = description
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_landing_page_template(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + "/delete.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def approve_landing_page_template(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + "/approveDraft.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def unapprove_landing_page_template(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + "/unapprove.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def discard_landing_page_template_draft(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + "/discardDraft.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def clone_landing_page_template(self, id, name, folderId, folderType):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError(
                "Invalid argument: required argument folder is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: folderType should be 'Folder' or 'Program'.")
        args = {
            'access_token': self.token,
            'name': name,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}"
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/landingPageTemplate/" + str(id) + "/clone.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    # --------- PROGRAM ---------

    def create_program(self, folderId, folderType, name, type, channel, description=None, tags=None, costs=None):
        self.authenticate()
        if folderId is None:
            raise ValueError(
                "Invalid argument: required argument folderId is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: required argument folderType is none.")
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if type is None:
            raise ValueError(
                "Invalid argument: required argument type is none.")
        if channel is None:
            raise ValueError(
                "Invalid argument: required argument channel is none.")
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
            tags_formatted = []
            for key, elem in tags.items():
                tag_pair = {'tagType': key, 'tagValue': elem}
                tags_formatted.append(tag_pair)
            args['tags'] = str(tags_formatted)
        if costs is not None:
            args['costs'] = str(costs)
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/programs.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_program_by_id(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/program/" + str(id) + ".json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_program_by_name(self, name):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/program/byName.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_program_by_tag_type(self, tagType, tagValue, maxReturn=20):
        self.authenticate()
        if tagType is None:
            raise ValueError(
                "Invalid argument: required argument tagType is none.")
        if tagValue is None:
            raise ValueError(
                "Invalid argument: required argument tagValue is none.")
        args = {
            'access_token': self.token,
            'tagType': tagType,
            'tagValue': tagValue,
            'maxReturn': maxReturn
        }
        result_list = []
        offset = 0
        while True:
            self.authenticate()
            args['access_token'] = self.token
            result = self._api_call('get', self.host + "/rest/asset/v1/program/byTag.json", args)
            if result is None:
                raise Exception("Empty Response")
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

    def update_program(self, id, name=None, description=None, tags=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        data = []
        if name is not None:
            data.append(('name', name))
        if description is not None:
            data.append(('description', description))
        if tags is not None:
            tags_formatted = []
            for key, elem in tags.items():
                tag_pair = {'tagType': key, 'tagValue': elem}
                tags_formatted.append(tag_pair)
            data.append(('tags', str(tags_formatted)))
        result = self._api_call('post', self.host + "/rest/asset/v1/program/" +
                                str(id) + ".json", args, data, mode='nojsondumps')
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_program(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/program/" + str(id) + "/delete.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def browse_programs(self, maxReturn=20, status=None, earliestUpdatedAt=None, latestUpdatedAt=None):
        self.authenticate()
        args = {
            'access_token': self.token,
            'maxReturn': maxReturn
        }
        if status:
            args['status'] = status
        if earliestUpdatedAt:
            args['earliestUpdatedAt'] = earliestUpdatedAt
        if latestUpdatedAt:
            args['latestUpdatedAt'] = latestUpdatedAt
        result_list = []
        offset = 0
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/asset/v1/programs.json", args)
            if result is None:
                raise Exception("Empty Response")
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

    def get_programs_yield(self, offset=0, maxReturn=20, status=None, earliestUpdatedAt=None, latestUpdatedAt=None,
                           filterType=None, filterValues=None, return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'maxReturn': maxReturn,
            'offset': offset
        }
        if status is not None:
            args['status'] = status
        if earliestUpdatedAt:
            args['earliestUpdatedAt'] = earliestUpdatedAt
        if latestUpdatedAt:
            args['latestUpdatedAt'] = latestUpdatedAt
        if filterType and filterValues:
            args['filterType'] = filterType
            args['filterValues'] = filterValues
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('get', self.host + "/rest/asset/v1/programs.json", args)
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) < maxReturn:
                    break
            else:
                break
            offset += maxReturn
            args['offset'] = offset

    def clone_program(self, id, name, folderId, folderType, description=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if folderId is None:
            raise ValueError(
                "Invalid argument: required argument folderId is none.")
        if folderType is None:
            raise ValueError(
                "Invalid argument: required argument folderType is none.")
        args = {
            'access_token': self.token,
            'folder': "{'id': " + str(folderId) + ", 'type': " + folderType + "}",
            'name': name
        }
        if description is not None:
            args['description'] = description
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/program/" + str(id) + "/clone.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def approve_program(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/program/" + str(id) + "/approve.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def unapprove_program(self, id):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/asset/v1/program/" + str(id) + "/unapprove.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_smart_list_by_program_id(self, id, includeRules=True, return_full_result=False):
        self.authenticate()
        args = {
            'access_token': self.token,
            'includeRules': includeRules
        }
        result = self._api_call('get', self.host + "/rest/asset/v1/program/{}/smartList.json".format(id), args)
        if result is None:
            raise Exception("Empty Response")
        if return_full_result:
            return result
        else:
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
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/asset/v1/channels.json", args)
            if result is None:
                raise Exception("Empty Response")
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
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/channel/byName.json", args)
        if result is None:
            raise Exception("Empty Response")
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
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + "/rest/asset/v1/tagTypes.json", args)
            if result is None:
                raise Exception("Empty Response")
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
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token,
            'name': name
        }
        result = self._api_call(
            'get', self.host + "/rest/asset/v1/tagType/byName.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    # --------- CUSTOM OBJECT TYPES ---------

    def create_update_custom_object_type(self, apiName, displayName, action='createOrUpdate', pluralName=None,
            description=None, showInLeadDetail=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        data = {
            'action': action,
            'apiName': apiName,
            'displayName': displayName
        }
        if pluralName is not None:
            data['pluralName'] = pluralName
        if description is not None:
            data['description'] = description
        if showInLeadDetail is not None:
            data['showInLeadDetail'] = showInLeadDetail
        result = self._api_call(
            'post', self.host + "/rest/v1/customobjects/schema.json", args, data)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_custom_object_type(self, apiName):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/v1/customobjects/schema/"+ str(apiName) +"/delete.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def approve_custom_object_type(self, apiName):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/v1/customobjects/schema/"+ str(apiName) +"/approve.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def discard_custom_object_type(self, apiName):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + "/rest/v1/customobjects/schema/"+ str(apiName) +"/discardDraft.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def add_field_custom_object_type(self, apiName, fields):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        data = {
            'input': fields
        }
        result = self._api_call(
            'post', self.host + "/rest/v1/customobjects/schema/" + str(apiName) + "/addField.json", args, data)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_list_of_custom_object_types(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/customobjects/schema.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def describe_custom_object_type(self, apiName):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/customobjects/schema/" + str(apiName) + "/describe.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    # --------- CUSTOM OBJECTS ---------

    def get_list_of_custom_objects(self, names=None):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if names is not None:
            args['names'] = names
        result = self._api_call(
            'get', self.host + "/rest/v1/customobjects.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def describe_custom_object(self, name):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/customobjects/" + name + "/describe.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def create_update_custom_objects(self, name, input, action=None, dedupeBy=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if input is None:
            raise ValueError(
                "Invalid argument: required argument input is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'input': []
        }
        for record in input:
            data['input'].append(record)
        if action is not None:
            data['action'] = action
        if dedupeBy is not None:
            data['dedupeBy'] = dedupeBy
        result = self._api_call(
            'post', self.host + "/rest/v1/customobjects/" + name + ".json", args, data)
        return result['result']

    def delete_custom_objects(self, name, input, deleteBy=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if input is None:
            raise ValueError(
                "Invalid argument: required argument input is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'input': []
        }
        for record in input:
            data['input'].append(record)
        if deleteBy is not None:
            data['deleteBy'] = deleteBy
        result = self._api_call(
            'post', self.host + "/rest/v1/customobjects/" + name + "/delete.json", args, data)
        return result['result']

    def get_custom_objects(self, name, input, filterType, fields=None, batchSize=None):
        self.authenticate()
        if name is None:
            raise ValueError(
                "Invalid argument: required argument name is none.")
        if input is None:
            raise ValueError(
                "Invalid argument: required argument input is none.")
        if filterType is None:
            raise ValueError(
                "Invalid argument: required argument filterType is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        data = {
            'filterType': filterType,
            'input': input
        }
        if fields is not None:
            data['fields'] = fields
        if batchSize is not None:
            data['batchSize'] = batchSize
        result_list = []
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'post', self.host + "/rest/v1/customobjects/" + name + ".json", args, data)
            if result is None:
                raise Exception("Empty Response")
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            data['nextPageToken'] = result['nextPageToken']
        return result_list

    # ------ OPPORTUNITY -------

    def describe_opportunity(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/opportunities/describe.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def create_update_opportunities(self, input, action=None, dedupeBy=None):
        self.authenticate()
        if input is None:
            raise ValueError(
                "Invalid argument: required argument input is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'input': []
        }
        for opportunity in input:
            data['input'].append(opportunity)
        if action is not None:
            data['action'] = action
        if dedupeBy is not None:
            data['dedupeBy'] = dedupeBy
        result = self._api_call(
            'post', self.host + "/rest/v1/opportunities.json", args, data)
        return result['result']

    def delete_opportunities(self, input, deleteBy=None):
        self.authenticate()
        if input is None:
            raise ValueError(
                "Invalid argument: required argument input is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'input': []
        }
        for opportunity in input:
            data['input'].append(opportunity)
        if deleteBy is not None:
            data['deleteBy'] = deleteBy
        result = self._api_call(
            'post', self.host + "/rest/v1/opportunities/delete.json", args, data)
        return result['result']

    def get_opportunities(self, filterType, filterValues, fields=None, batchSize=None):
        self.authenticate()
        if filterType is None:
            raise ValueError(
                "Invalid argument: required argument filterType is none.")
        if filterValues is None:
            raise ValueError(
                "Invalid argument: required argument filter_values is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        filterValues = filterValues.split() if type(
            filterValues) is str else filterValues
        data = [('filterValues', (',').join(filterValues)),
                ('filterType', filterType)]
        if fields is not None:
            data.append(('fields', fields))
        if batchSize is not None:
            data.append(('batchSize', batchSize))
        result_list = []
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'post', self.host + "/rest/v1/opportunities.json", args, data, mode='nojsondumps')
            if result is None:
                raise Exception("Empty Response")
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def describe_opportunity_role(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/opportunities/roles/describe.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def create_update_opportunities_roles(self, input, action=None, dedupeBy=None):
        self.authenticate()
        if input is None:
            raise ValueError(
                "Invalid argument: required argument input is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'input': []
        }
        for opportunity in input:
            data['input'].append(opportunity)
        if action is not None:
            data['action'] = action
        if dedupeBy is not None:
            data['dedupeBy'] = dedupeBy
        result = self._api_call(
            'post', self.host + "/rest/v1/opportunities/roles.json", args, data)
        return result['result']

    def delete_opportunity_roles(self, input, deleteBy=None):
        self.authenticate()
        if input is None:
            raise ValueError(
                "Invalid argument: required argument input is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'input': []
        }
        for opportunity in input:
            data['input'].append(opportunity)
        if deleteBy is not None:
            data['deleteBy'] = deleteBy
        result = self._api_call(
            'post', self.host + "/rest/v1/opportunities/roles/delete.json", args, data)
        return result['result']

    def get_opportunity_roles(self, filterType, filterValues, fields=None, batchSize=None):
        self.authenticate()
        if filterType is None:
            raise ValueError(
                "Invalid argument: required argument filterType is none.")
        if filterValues is None:
            raise ValueError(
                "Invalid argument: required argument filter_values is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        filterValues = filterValues.split() if type(
            filterValues) is str else filterValues
        data = [('filterValues', (',').join(filterValues)),
                ('filterType', filterType)]
        if fields is not None:
            data.append(('fields', fields))
        if batchSize is not None:
            data.append(('batchSize', batchSize))
        result_list = []
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'post', self.host + "/rest/v1/opportunities/roles.json", args, data, mode='nojsondumps')
            if result is None:
                raise Exception("Empty Response")
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    # --------- COMPANY ---------

    def describe_company(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/companies/describe.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def create_update_companies(self, input, action=None, dedupeBy=None):
        self.authenticate()
        if input is None:
            raise ValueError(
                "Invalid argument: required argument input is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'input': []
        }
        for company in input:
            data['input'].append(company)
        if action is not None:
            data['action'] = action
        if dedupeBy is not None:
            data['dedupeBy'] = dedupeBy
        result = self._api_call(
            'post', self.host + "/rest/v1/companies.json", args, data)
        return result['result']

    def delete_companies(self, input, deleteBy=None):
        self.authenticate()
        if input is None:
            raise ValueError(
                "Invalid argument: required argument input is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'input': []
        }
        for company in input:
            data['input'].append(company)
        if deleteBy is not None:
            data['deleteBy'] = deleteBy
        result = self._api_call(
            'post', self.host + "/rest/v1/companies/delete.json", args, data)
        return result['result']

    def get_companies(self, filterType, filterValues, fields=None, batchSize=None):
        self.authenticate()
        if filterType is None:
            raise ValueError(
                "Invalid argument: required argument filterType is none.")
        if filterValues is None:
            raise ValueError(
                "Invalid argument: required argument filter_values is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        filterValues = filterValues.split() if type(
            filterValues) is str else filterValues
        data = [('filterValues', (',').join(filterValues)),
                ('filterType', filterType)]
        if fields is not None:
            data.append(('fields', fields))
        if batchSize is not None:
            data.append(('batchSize', batchSize))
        result_list = []
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'post', self.host + "/rest/v1/companies.json", args, data, mode='nojsondumps')
            if result is None:
                raise Exception("Empty Response")
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    # --------- SALES PERSON ---------

    def describe_sales_person(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/salespersons/describe.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def create_update_sales_persons(self, input, action=None, dedupeBy=None):
        self.authenticate()
        if input is None:
            raise ValueError(
                "Invalid argument: required argument input is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'input': []
        }
        for person in input:
            data['input'].append(person)
        if action is not None:
            data['action'] = action
        if dedupeBy is not None:
            data['dedupeBy'] = dedupeBy
        result = self._api_call(
            'post', self.host + "/rest/v1/salespersons.json", args, data)
        return result['result']

    def delete_sales_persons(self, input, deleteBy=None):
        self.authenticate()
        if input is None:
            raise ValueError(
                "Invalid argument: required argument input is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'input': []
        }
        for record in input:
            data['input'].append(record)
        if deleteBy is not None:
            data['deleteBy'] = deleteBy
        result = self._api_call(
            'post', self.host + "/rest/v1/salespersons/delete.json", args, data)
        return result['result']

    def get_sales_persons(self, filterType, filterValues, fields=None, batchSize=None):
        self.authenticate()
        if filterType is None:
            raise ValueError(
                "Invalid argument: required argument filterType is none.")
        if filterValues is None:
            raise ValueError(
                "Invalid argument: required argument filter_values is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        filterValues = filterValues.split() if type(
            filterValues) is str else filterValues
        data = [('filterValues', (',').join(filterValues)),
                ('filterType', filterType)]
        if fields is not None:
            data.append(('fields', fields))
        if batchSize is not None:
            data.append(('batchSize', batchSize))
        result_list = []
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'post', self.host + "/rest/v1/salespersons.json", args, data, mode='nojsondumps')
            if result is None:
                raise Exception("Empty Response")
            result_list.extend(result['result'])
            if len(result['result']) == 0 or 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def get_custom_activity_types(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'get', self.host + "/rest/v1/activities/external/types.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def describe_custom_activity_type(self, apiName, draft=None):
        if apiName is None:
            raise ValueError("Required argument apiName is none.")
        self.authenticate()
        args = {
            'access_token': self.token
        }
        if draft:
            args['draft'] = draft
        result = self._api_call('get', self.host + "/rest/v1/activities/external/type/" + apiName + "/describe.json",
                                args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def create_custom_activity_type(self, apiName, name, triggerName, filterName, primaryAttributeApiName,
                                    primaryAttributeName, primaryAttributeDescription=None, description=None):
        self.authenticate()
        if apiName is None:
            raise ValueError("Required argument 'apiName' is none.")
        if name is None:
            raise ValueError("Required argument 'name' is none.")
        if triggerName is None:
            raise ValueError("Required argument 'triggerName' is none")
        if filterName is None:
            raise ValueError("Required argument 'filterName' is none.")
        if primaryAttributeApiName is None:
            raise ValueError(
                "Required argument 'primaryAttributeApiName' is none.")
        if primaryAttributeName is None:
            raise ValueError(
                "Required argument 'primaryAttributeName' is none.")
        #if primaryAttributeDescription is None: raise ValueError("Required argument 'primaryAttributeDescription' is none.")
        args = {
            'access_token': self.token
        }
        data = {
            'apiName': apiName,
            'name': name,
            'triggerName': triggerName,
            'filterName': filterName,
            'primaryAttribute': {
                'apiName': primaryAttributeApiName,
                'name': primaryAttributeName
            }
        }
        if description is not None:
            data['description'] = description
        if primaryAttributeDescription is not None:
            data['primaryAttribute']['description'] = primaryAttributeDescription
        result = self._api_call(
            'post', self.host + "/rest/v1/activities/external/type.json", args, data)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_custom_activity_type(self, apiName, name=None, triggerName=None, filterName=None,
                                    primaryAttributeApiName=None, primaryAttributeName=None,
                                    primaryAttributeDescription=None, description=None):
        self.authenticate()
        if apiName is None:
            raise ValueError("Required argument 'apiName' is none.")
        args = {
            'access_token': self.token
        }
        data = {}
        if name is not None:
            data['name'] = name
        if triggerName is not None:
            data['triggerName'] = triggerName
        if filterName is not None:
            data['filterName'] = filterName
        if description is not None:
            data['description'] = description
        if primaryAttributeApiName or primaryAttributeName or primaryAttributeDescription:
            data['primaryAttribute'] = {}
        if primaryAttributeApiName:
            data['primaryAttribute']['apiName'] = primaryAttributeApiName
        if primaryAttributeName:
            data['primaryAttribute']['name'] = primaryAttributeName
        if primaryAttributeDescription:
            data['primaryAttribute']['description'] = primaryAttributeDescription
        result = self._api_call(
            'post', self.host + "/rest/v1/activities/external/type/" + apiName + ".json", args, data)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def approve_custom_activity_type(self, apiName):
        self.authenticate()
        if apiName is None:
            raise ValueError("Required argument 'apiName' is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call('post',
                                self.host + "/rest/v1/activities/external/type/" + apiName + "/approve.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def discard_custom_activity_type_draft(self, apiName):
        self.authenticate()
        if apiName is None:
            raise ValueError("Required argument 'apiName' is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call('post',
                                self.host + "/rest/v1/activities/external/type/" + apiName + "/discardDraft.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_custom_activity_type(self, apiName):
        self.authenticate()
        if apiName is None:
            raise ValueError("Required argument 'apiName' is none.")
        args = {
            'access_token': self.token
        }
        result = self._api_call('post',
                                self.host + "/rest/v1/activities/external/type/" + apiName + "/delete.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def create_custom_activity_type_attribute(self, apiName, attributes):
        self.authenticate()
        if apiName is None:
            raise ValueError("Required argument 'apiName' is none.")
        if attributes is None:
            raise ValueError("Required argument 'attributes' is none.")
        args = {
            'access_token': self.token
        }
        data = {
            "attributes": attributes
        }
        result = self._api_call('post',
                                self.host + "/rest/v1/activities/external/type/" +
                                apiName + "/attributes/create.json",
                                args, data)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def update_custom_activity_type_attribute(self, apiName, attributes):
        self.authenticate()
        if apiName is None:
            raise ValueError("Required argument 'apiName' is none.")
        if attributes is None:
            raise ValueError("Required argument 'attributes' is none.")
        args = {
            'access_token': self.token
        }
        data = {
            "attributes": attributes
        }
        result = self._api_call('post',
                                self.host + "/rest/v1/activities/external/type/" +
                                apiName + "/attributes/update.json",
                                args, data)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def delete_custom_activity_type_attribute(self, apiName, attributes):
        self.authenticate()
        if apiName is None:
            raise ValueError("Required argument 'apiName' is none.")
        if attributes is None:
            raise ValueError("Required argument 'attributes' is none.")
        args = {
            'access_token': self.token
        }
        data = {
            "attributes": attributes
        }
        result = self._api_call('post',
                                self.host + "/rest/v1/activities/external/type/" + apiName +
                                "/attributes/delete.json", args, data)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    # --------- BULK EXTRACT LEADS & ACTIVITIES ---------

    def _get_export_jobs_list(self, entity, object_name=None):
        if entity == 'customobjects':
            assert object_name is not None, 'Invalid argument: required field object_name is none.'
            entity = '{}/{}'.format(entity, object_name)
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result_list = []
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call(
                'get', self.host + '/bulk/v1/{}/export.json'.format(entity), args)
            if result is None:
                raise Exception("Empty Response")
            result_list.extend(result['result'])
            if 'nextPageToken' not in result:
                break
            args['nextPageToken'] = result['nextPageToken']
        return result_list

    def _create_bulk_export_job(self, entity, fields=None, filters=None, format='CSV', columnHeaderNames=None,
                                object_name=None):
        assert entity is not None, 'Invalid argument: required field entity is none.'
        if entity in ['leads', 'program/members', 'customobjects']:
            assert fields is not None, 'Invalid argument: required field fields is none.'
        assert filters is not None, 'Invalid argument: required field filters is none.'
        if entity == 'customobjects':
            assert object_name is not None, 'Invalid argument: required field object_name is none.'
            entity = '{}/{}'.format(entity, object_name)
        data = {'fields': fields, 'format': format, 'filter': filters}
        if columnHeaderNames is not None:
            data['columnHeaderNames'] = columnHeaderNames
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call(
            'post', self.host + '/bulk/v1/{}/export/create.json'.format(entity), args, data)
        return result['result']

    def _export_job_state_machine(self, entity, state, job_id, object_name=None, stream=False):
        assert entity is not None, 'Invalid argument: required field "entity" is none.'
        assert state is not None, 'Invalid argument: required field "state" is none.'
        assert job_id is not None, 'Invalid argument: required field "job_id" is none.'
        if entity == 'customobjects':
            assert object_name is not None, 'Invalid argument: required field "object_name" is none.'
            entity = '{}/{}'.format(entity, object_name)
        state_info = {
            'enqueue': {'suffix': '/enqueue.json', 'method': 'post', 'mode': None},
            'cancel': {'suffix': '/cancel.json', 'method': 'post', 'mode': None},
            'status': {'suffix': '/status.json', 'method': 'get', 'mode': None},
            'file': {'suffix': '/file.json', 'method': 'get', 'mode': 'nojson'}
        }
        self.authenticate()
        url = '{}/bulk/v1/{}/export/{}{}'.format(self.host, entity, job_id, state_info[state]['suffix'])
        args = {
            'access_token': self.token
        }
        result = self._api_call(state_info[state]['method'], url, args, mode=state_info[state]['mode'], stream=stream)
        if state == 'file' and result.status_code == 200:
            if not stream:
                return result.content
            return result
        return result['result']

    def get_leads_export_job_file(self, *args, **kargs):
        return self._export_job_state_machine('leads', 'file', *args, **kargs)

    def get_activities_export_job_file(self, *args, **kargs):
        return self._export_job_state_machine('activities', 'file', *args, **kargs)

    def get_custom_objects_export_job_file(self, *args, **kargs):
        return self._export_job_state_machine('customobjects', 'file', *args, **kargs)

    def get_program_members_export_job_file(self, *args, **kargs):
        return self._export_job_state_machine('program/members', 'file', *args, **kargs)

    def get_leads_export_job_status(self, *args, **kargs):
        return self._export_job_state_machine('leads', 'status', *args, **kargs)

    def get_activities_export_job_status(self, *args, **kargs):
        return self._export_job_state_machine('activities', 'status', *args, **kargs)

    def get_custom_objects_export_job_status(self, *args, **kargs):
        return self._export_job_state_machine('customobjects', 'status', *args, **kargs)

    def get_program_members_export_job_status(self, *args, **kargs):
        return self._export_job_state_machine('program/members', 'status', *args, **kargs)

    def cancel_leads_export_job(self, *args, **kargs):
        return self._export_job_state_machine('leads', 'cancel', *args, **kargs)

    def cancel_activities_export_job(self, *args, **kargs):
        return self._export_job_state_machine('activities', 'cancel', *args, **kargs)

    def cancel_custom_objects_export_job(self, *args, **kargs):
        return self._export_job_state_machine('customobjects', 'cancel', *args, **kargs)

    def cancel_program_members_export_job(self, *args, **kargs):
        return self._export_job_state_machine('program/members', 'cancel', *args, **kargs)

    def enqueue_leads_export_job(self, *args, **kargs):
        return self._export_job_state_machine('leads', 'enqueue', *args, **kargs)

    def enqueue_activities_export_job(self, *args, **kargs):
        return self._export_job_state_machine('activities', 'enqueue', *args, **kargs)

    def enqueue_custom_objects_export_job(self, *args, **kargs):
        return self._export_job_state_machine('customobjects', 'enqueue', *args, **kargs)

    def enqueue_program_members_export_job(self, *args, **kargs):
        return self._export_job_state_machine('program/members', 'enqueue', *args, **kargs)

    def create_leads_export_job(self, *args, **kargs):
        return self._create_bulk_export_job('leads', *args, **kargs)

    def create_activities_export_job(self, *args, **kargs):
        return self._create_bulk_export_job('activities', *args, **kargs)

    def create_custom_objects_export_job(self, *args, **kargs):
        return self._create_bulk_export_job('customobjects', *args, **kargs)

    def create_program_members_export_job(self, *args, **kargs):
        return self._create_bulk_export_job('program/members', *args, **kargs)

    def get_leads_export_jobs_list(self):
        return self._get_export_jobs_list('leads')

    def get_activities_export_jobs_list(self):
        return self._get_export_jobs_list('activities')

    def get_custom_objects_export_jobs_list(self, object_name):
        return self._get_export_jobs_list('customobjects', object_name)

    def get_program_members_export_jobs_list(self):
        return self._get_export_jobs_list('program/members')

    # --- NAMED ACCOUNTS ---

    def get_named_accounts(self, filterType, filterValues, fields=None, batchSize=None, return_full_result=False,
                           nextPageToken=None):
        self.authenticate()
        if filterType is None:
            raise ValueError("Invalid argument: required argument filterType is none.")
        if filterValues is None:
            raise ValueError("Invalid argument: required argument filter_values is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        filterValues = filterValues.split() if type(
            filterValues) is str else filterValues
        data = [('filterValues', (',').join(filterValues)),
                ('filterType', filterType)]
        if fields is not None:
            data.append(('fields', fields))
        if batchSize is not None:
            data.append(('batchSize', batchSize))
        if nextPageToken:
            args['nextPageToken'] = nextPageToken
        result_list = []
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('post', self.host + "/rest/v1/namedaccounts.json", args, data, mode='nojsondumps')
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) == 0 or 'nextPageToken' not in result:
                    break
                else:
                    args['nextPageToken'] = result['nextPageToken']

    def sync_named_accounts(self):
        pass

    def delete_named_accounts(self):
        pass

    def describe_named_accounts(self):
        self.authenticate()
        args = {
            'access_token': self.token
        }
        result = self._api_call('get', self.host + "/rest/v1/namedaccounts/describe.json", args)
        if result is None:
            raise Exception("Empty Response")
        return result['result']

    def get_named_account_list_members(self, id, fields=None, batchSize=None, return_full_result=False,
                                       nextPageToken=None):
        self.authenticate()
        if id is None:
            raise ValueError("Invalid argument: required argument id is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        data = []
        if fields is not None:
            data.append(('fields', fields))
        if batchSize is not None:
            data.append(('batchSize', batchSize))
        if nextPageToken:
            args['nextPageToken'] = nextPageToken
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('post', self.host + "/rest/v1/namedAccountList/" +
                                    str(id) + "/namedAccounts.json", args, data, mode='nojsondumps')
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) == 0 or 'nextPageToken' not in result:
                    break
                else:
                    args['nextPageToken'] = result['nextPageToken']

    def add_named_account_list_members(self):
        pass

    def remove_named_account_list_members(self):
        pass

    def get_named_account_lists(self, filterType, filterValues, batchSize=None, return_full_result=False,
                                nextPageToken=None):
        self.authenticate()
        if filterType is None:
            raise ValueError("Invalid argument: required argument filterType is none.")
        if filterValues is None:
            raise ValueError("Invalid argument: required argument filter_values is none.")
        args = {
            'access_token': self.token,
            '_method': 'GET'
        }
        filterValues = filterValues.split() if type(
            filterValues) is str else filterValues
        data = [('filterValues', (',').join(filterValues)),
                ('filterType', filterType)]
        if batchSize is not None:
            data.append(('batchSize', batchSize))
        if nextPageToken:
            args['nextPageToken'] = nextPageToken
        result_list = []
        while True:
            self.authenticate()
            # for long-running processes, this updates the access token
            args['access_token'] = self.token
            result = self._api_call('post', self.host + "/rest/v1/namedAccountLists.json", args, data,
                                    mode='nojsondumps')
            if result is None:
                raise Exception("Empty Response")
            if 'result' in result:
                if return_full_result:
                    yield result
                else:
                    yield result['result']
                if len(result['result']) == 0 or 'nextPageToken' not in result:
                    break
                else:
                    args['nextPageToken'] = result['nextPageToken']

    def sync_named_account_lists(self):
        pass

    def delete_named_account_lists(self):
        pass
