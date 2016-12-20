from marketorestpython.client import MarketoClient
'''
munchkin_id = "" ### Enter Munchkin ID
client_id = "" ### enter client ID (find in Admin > LaunchPoint > view details)
client_secret = "" ### enter client secret (find in Admin > LaunchPoint > view details)

mc = MarketoClient(munchkin_id, client_id, client_secret)

segments = mc.execute(method='get_segments', id=1003)

print(segments)
'''
