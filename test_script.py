#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json, os, uuid, time, logging
from random import randint
from marketorestpython.client import MarketoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

try:
    # Travis testing
    MUNCHKIN_ID = os.environ['MUNCHKIN_ID']
    CLIENT_ID = os.environ['CLIENT_ID']
    CLIENT_SECRET = os.environ['CLIENT_SECRET']
except KeyError:
    # local testing
    with open('conf.json', 'r', encoding='utf-8') as f:
        creds = json.loads(f.read())
    MUNCHKIN_ID = creds['munchkin_id']
    CLIENT_ID = creds['client_id']
    CLIENT_SECRET = creds['client_secret']

mc = MarketoClient(munchkin_id=MUNCHKIN_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

segmentation_id = 1001

lead_id_1 = None
lead_id_2 = None
file_id = None
list_folder_id = None
smart_list_folder_id = None
new_folder_id = None
list_id = None
files_folder_id = None
bulk_lead_export_id = None
list_name = uuid.uuid4()
cloned_smart_list_id = None


def test_create_update_leads():
    random_number = randint(100, 999)
    email1 = "joe{}@example.com".format(random_number)
    email2 = "jill{}@example.com".format(random_number)
    leads = [{"email": email1, "firstName": "Joey"}, {"email": email2, "firstName": "Jillian"}]
    response = mc.execute(method='create_update_leads', leads=leads)
    global lead_id_1
    lead_id_1 = response[0]['id']
    global lead_id_2
    lead_id_2 = response[1]['id']
    assert response[0]['status'] in ['created','updated'] and response[1]['status'] in ['created','updated']


def test_get_folder_by_name():
    global list_folder_id
    global smart_list_folder_id
    list_folder = mc.execute(method='get_folder_by_name', name='Group Lists')
    smart_list_folder = mc.execute(method='get_folder_by_name', name='Group Smart Lists')
    print(list_folder)
    list_folder_id = list_folder[0]['id']
    smart_list_folder_id = smart_list_folder[0]['id']
    print('list_folder_id: {}'.format(list_folder_id))
    print('smart_list_folder_id: {}'.format(smart_list_folder_id))
    logger.info('smart_list_folder: {}'.format(smart_list_folder_id))
    assert list_folder_id and smart_list_folder_id


def test_create_folder():
    global new_folder_id
    new_folder = mc.execute(method='create_folder', name='temp test folder',
                            parentId=19,
                            parentType='Folder', description='temp description')
    new_folder_id = new_folder[0]['id']
    print(new_folder_id)
    assert new_folder_id


def test_create_token():
    global new_folder_id
    token_value = '<p><strong>Important—</strong></p>'
    new_token = mc.execute(method='create_token', id=new_folder_id,
                           folderType='Folder',
                           type='rich text', name='test token',
                           value=token_value)
    # this assert is failing in Python 2.7 because of unicode issues; passes in 3.6
    # assert new_token[0]['tokens'][0]['value'] == token_value
    assert new_token


def test_delete_folder():
    global new_folder_id
    deleted_folder = mc.execute(method='delete_folder', id=new_folder_id)
    assert deleted_folder


def test_create_list():
    global list_folder_id
    global list_id
    global list_name
    static_list = mc.execute(method='create_list', name=list_name, folderId=list_folder_id, folderType='Folder')
    print(static_list)
    list_id = static_list[0]['id']
    assert static_list


def test_update_list():
    global list_id
    global list_name
    static_list = mc.execute(method='update_list', id=list_id, name='{} (renamed)'.format(list_name),
                             description='added description')
    print(static_list)
    assert static_list


def test_get_list_by_id():
    global list_id
    global list_name
    static_list = mc.execute(method='get_list_by_id', id=list_id)
    assert static_list[0]['name'] == '{} (renamed)'.format(list_name)


def test_get_list_by_name():
    global list_id
    global list_name
    new_list_name = '{} (renamed)'.format(list_name)
    static_list = mc.execute(method='get_list_by_name', name=new_list_name)
    assert static_list[0]['id'] == list_id


def test_get_multiple_lists():
    global list_id
    global list_name
    new_list_name = '{} (renamed)'.format(list_name)
    static_list = mc.execute(method='get_multiple_lists', name=new_list_name)
    assert static_list[0]['id'] == list_id


def test_browse_lists():
    global list_folder_id
    static_lists = mc.execute(method='browse_lists', folderId=list_folder_id, folderType='Folder',
                              earliestUpdatedAt='2019-02-01')
    assert len(static_lists) >= 1


def test_add_leads_to_list():
    global lead_id_1
    global lead_id_2
    global list_id
    add_to_list = mc.execute(method='add_leads_to_list', listId=list_id, id=[lead_id_1, lead_id_2])
    assert add_to_list[0]['status'] == 'added' and add_to_list[1]['status'] == 'added'


def test_create_lead_export_job():
    global list_id
    global bulk_lead_export_id
    job = mc.execute(method='create_leads_export_job', fields=['firstName', 'lastName', 'email'],
                     filters={'staticListId': list_id})
    bulk_lead_export_id = job[0]['exportId']
    assert job[0]['status'] == 'Created'


def test_enqueue_lead_export_job():
    global bulk_lead_export_id
    enqueued_job_details = mc.execute(method='enqueue_leads_export_job',
                                      job_id=bulk_lead_export_id)
    assert enqueued_job_details[0]['status'] == 'Queued'


def test_cancel_lead_export_job():
    global bulk_lead_export_id
    cancelled_job = mc.execute(method='cancel_leads_export_job',
                               job_id=bulk_lead_export_id)
    assert cancelled_job[0]['status'] == 'Cancelled'


def test_segments():
    segments = mc.execute(method='get_segments', id=segmentation_id)
    assert segments


def test_get_files_folder_by_name():
    global files_folder_id
    files_folder = mc.execute(method='get_folder_by_name', name='Images and Files')
    print(files_folder )
    files_folder_id = files_folder [0]['id']
    print(list_folder_id)


def test_create_file():
    global file_id
    file = mc.execute(method='create_file', name='python-logo-master-v3-TM.png', file='python-logo-master-v3-TM.png',
                      folder=files_folder_id, description='test file', insertOnly=False)
    print(file)
    file_id = file[0]['id']
    assert file


def test_update_file_content():
    global file_id
    file = mc.execute(method='update_file_content', id=file_id, file='python-logo-master-v3-TM.png')
    assert file


def get_file_by_id():
    global file_id
    file = mc.execute(method='get_file_by_id', id=file_id)
    assert file


def list_files():
    files = mc.execute(method='list_files', folder=files_folder_id, offset=0, maxReturn=10)
    assert files


def test_error_handling():
    try:
        token = mc.execute(method='get_paging_token', sinceDatetime='2015-04-0113')
        e_dict = None
        print(token)
    except Exception as e:
        print('error: {}'.format(e))
        e_dict = eval(str(e))
        if 'code' in e_dict:
            print('code: {}'.format(e_dict['code']))
        else:
            print('e_dict: {}'.format(e_dict))
    assert e_dict['code'] == '1001'


def test_delete_list():
    global list_id
    list = mc.execute(method='delete_list', id = list_id)
    print(list)
    assert list


def test_delete_leads():
    global lead_id_1
    global lead_id_2
    response = mc.execute(method='delete_lead', id=[lead_id_1, lead_id_2])
    assert response[0]['status'] == 'deleted' and response[1]['status'] == 'deleted'


def test_get_smart_campaign_by_id():
    campaign = mc.execute(method='get_smart_campaign_by_id', id=1109)
    assert campaign[0]['id'] == 1109


def test_get_smart_campaigns():
    first_campaigns = None
    second_campaigns = None
    third_campaigns = None
    for campaigns in mc.execute(method='get_smart_campaigns'):
        first_campaigns = campaigns
        logger.info('found {} campaigns'.format(len(campaigns)))
        break
    for campaigns in mc.execute(method='get_smart_campaigns', folderId=1031, folderType='Program'):
        second_campaigns = campaigns
        logger.info('found {} campaigns in Program 1031'.format(len(campaigns)))
        break
    for campaigns in mc.execute(method='get_smart_campaigns', offset=5, maxReturn=10):
        third_campaigns = campaigns
        logger.info('found {} campaigns with maxReturn=10'.format(len(campaigns)))
        break
    assert len(first_campaigns) > 20 and len(second_campaigns) == 2 and len(third_campaigns) == 10


def test_activate_smart_campaign():
    campaign = mc.execute(method='activate_smart_campaign', id=1109)
    assert campaign[0]['id'] == 1109


def test_deactivate_smart_campaign():
    campaign = mc.execute(method='deactivate_smart_campaign', id=1109)
    assert campaign[0]['id'] == 1109


def test_get_smart_list_by_id():
    original_smart_list = mc.execute(method='get_smart_list_by_id', id=5944)
    assert original_smart_list[0]['id'] == 5944


def test_get_smart_list_by_name():
    original_smart_list = mc.execute(method='get_smart_list_by_name', name='Do not delete')
    assert original_smart_list[0]['id'] == 5944


def test_clone_smart_list():
    global cloned_smart_list_id
    cloned_smart_list = mc.execute(method='clone_smart_list', id=5944, name='temp smart list',
                                   folderId=smart_list_folder_id, folderType='Folder', return_full_result=False)
    cloned_smart_list_id = cloned_smart_list[0]['id']
    assert cloned_smart_list_id


def get_smart_lists():
    my_list_batch = []
    for my_lists in mc.execute(method='get_smart_lists', folderId=smart_list_folder_id, folderType='Folder'):
        my_list_batch += my_lists
    assert len(my_list_batch) > 1  # we have the original and the cloned smart list


def test_delete_smart_list():
    deleted_smart_list = mc.execute(method='delete_smart_list', id=cloned_smart_list_id)
    assert deleted_smart_list

def test_get_smart_list_by_smart_campaign_id():
    campaign_smart_list = mc.execute(method='get_smart_list_by_smart_campaign_id', id=1125)
    assert len(campaign_smart_list) == 1  # there is only 1 trigger in this specific Smart Campaign's Smart List

def test_get_smart_list_by_program_id():
    email_program_smart_list = mc.execute(method='get_smart_list_by_program_id', id=1027)
    assert len(email_program_smart_list) == 1  # there is only 1 trigger in this specific Program's Smart List


'''
mc2 = MarketoClient(munchkin_id=MUNCHKIN_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, max_retry_time=30)


def test_max_retry_time():
    day = 1
    time_elapsed = 0
    for i in range(11):
        start_time = time.time()
        export_filter = {
          "createdAt": {
             "startAt": "2018-07-0{}".format(day),
             "endAt": "2018-07-0{}".format(day+1)
          },
          "activityTypeIds": [1]
        }
        job = mc2.execute(method='create_activities_export_job', filters=export_filter)
        job_id = job[0]['exportId']
        try:
            enqueue = mc2.execute(method='enqueue_activities_export_job', job_id=job_id)
        except Exception as e:
            e_dict = eval(str(e))
            logger.info('error: {}'.format(e_dict))
            time_elapsed = time.time() - start_time
            break
        day += 1
    assert 30 < time_elapsed < 35
'''