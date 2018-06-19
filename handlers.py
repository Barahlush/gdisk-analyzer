from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from analytics import Analyzer
from filewrappers import File, Folder, extract, get_filetype
import pandas as pd


class DriveHandler():
    root = '"root"'
    def __init__(self, user_id=0, credential_path=None):

        self.user_id = user_id
        self.local_cred_name = 'credentials.json'
        self.permissions = 'https://www.googleapis.com/auth/drive.metadata.readonly'

        self.cred_path = credential_path
        self.service = None

        self.folder_handler = FolderHandler()
        self.analyzer = Analyzer()

        self.data = None



    def set_credentials(self, credential_path):
        self.cred_path = credential_path


    def connect(self):
        SCOPES = self.permissions
        store = file.Storage(self.local_cred_name)
        creds = store.get()

        print("Getting credentials...")
        if not creds or creds.invalid:
            try:
                flow = client.flow_from_clientsecrets(self.cred_path, SCOPES)
                creds = tools.run_flow(flow, store)
            except:
                print("Wrong credentials.")

        print("Connecting...")
        try:
            service = build('drive', 'v3', http=creds.authorize(Http()))
        except:
            print('Unable to get the service.')
            raise Exception('Check your connection.')

        self.service = service
        self.folder_handler.set_service(service)
        print("Succesfully authentificated!\n")


    def get_drive_info(self):
        info = self.service.about().get(fields="user, storageQuota").execute()

        usr = info['user']
        storage = info['storageQuota']
        limit = int(storage['limit'])
        usage = int(storage['usage'])
        in_drive = int(storage['usageInDrive'])

        print("""Email: {email}\nLimit: {lim}\nUsage: {usg}""".format(email=usr['emailAddress'], lim=limit, usg=in_drive))

        other = usage - inDrive
        free = limit - usage
        return [free, in_drive, other]


    def analyze_folder(self, folder):
        data, sum_size = self.folder_handler.scan_folder(folder)
        self.data = pd.concat([self.data, data])

        indexes = list(data[data['mimeType'] == 'folder'].index.values)
        for id in indexes:
            print("scanning {}...".format(data.loc[id]['name']))
            sum_size += self.analyze_folder(id)
        if folder != DriveHandler.root:
            self.data.loc[folder]['sum_size'] += sum_size
        print("{0} size: {1} MB".format(self.data.loc[folder]['name'] if folder != DriveHandler.root else "Summary ", sum_size/1024/1024))
        return sum_size


    def analyze_drive(self):
        self.data = pd.DataFrame(columns=['name', 'mimeType', 'size', 'sum_size', 'viewedByMeTime', 'parent', 'id']).set_index('id')
        sum_size = self.analyze_folder(DriveHandler.root)

        return self.data, sum_size


class FolderHandler():
    root = '"root"'


    def __init__(self, service=None):
        self.service = service


    def set_service(self, service):
        self.service = service


    def read_page(self, folder=root, page_token=None, page_size=1000):
        page = self.service.files().list(
            pageSize = page_size,
            orderBy = 'name',
            spaces='drive',
            fields='nextPageToken, files',
            q = '{folder} in parents'.format(folder=folder),
            pageToken=page_token).execute()
        return page


    def get_files(self, folder=root, page_token=None, page_size=1000):
        page = self.read_page(folder, page_token, page_size)

        files = page.get('files', [])
        next_token = page.get('nextPageToken', None)

        return files, next_token


    def scan_folder(self, folder=root):
        page_token = None
        file_counter = 0
        files = []
        while page_token != None or file_counter == 0:

            cur_files, page_token = self.get_files(folder, page_token)
            file_counter += len(cur_files)
            files += cur_files

            print('{num} files scanned.'.format(num = file_counter))

            if len(cur_files) == 0:
                break

        data, sum_size = extract(files)
        return data, sum_size
