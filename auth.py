from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


# Setup the Drive v3 API
def auth_drive(credential_path):
    SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
    store = file.Storage('credentials.json')
    creds = store.get()
    print("Getting credentials...")
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(credential_path, SCOPES)
        creds = tools.run_flow(flow, store)
    print("Connecting...")
    service = build('drive', 'v3', http=creds.authorize(Http()))
    print("Succesfully authentificated!\n")
    return service
