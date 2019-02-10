import json, os
from marketorestpython.client import MarketoClient

try:
    # Travis testing
    MUNCHKIN_ID = os.environ['munchkin_id']
    CLIENT_ID = os.environ['client_id']
    CLIENT_SECRET = os.environ['client_secret']
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
list_id = None
files_folder_id = None
bulk_lead_export_id = None


def test_create_update_leads():
    leads = [{"email": "joe@example.com", "firstName": "Joey"}, {"email": "jill@example.com", "firstName": "Jillian"}]
    response = mc.execute(method='create_update_leads', leads=leads)
    global lead_id_1
    lead_id_1 = response[0]['id']
    global lead_id_2
    lead_id_2 = response[1]['id']
    assert response[0]['status'] in ['created','updated'] and response[1]['status'] in ['created','updated']


def test_get_folder_by_name():
    global list_folder_id
    list_folder = mc.execute(method='get_folder_by_name', name='Group Lists')
    print(list_folder)
    list_folder_id = list_folder[0]['id']
    print(list_folder_id)


def test_create_list():
    global list_folder_id
    global list_id
    list = mc.execute(method='create_list', name='unit test list', folderId=list_folder_id, folderType='Folder')
    print(list)
    list_id = list[0]['id']
    assert list


def test_update_list():
    global list_id
    list = mc.execute(method='update_list', id=list_id, name='unit test list (renamed)', description='added description')
    print(list)
    assert list


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

