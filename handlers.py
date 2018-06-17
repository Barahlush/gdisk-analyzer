from collections import Counter, defaultdict
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import re

class DriveHandler():

    def __init__(self, credential_path=None):
        self.local_cred_name = 'credentials.json'
        self.permissions = 'https://www.googleapis.com/auth/drive.metadata.readonly'

        self.cred_path = credential_path
        self.service = None

        self.folder_handler = FolderHandler()
        self.analyzer = Analyzer()

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
            return None
        self.service = service
        self.folder_handler.set_service(service)
        print("Succesfully authentificated!\n")


    def get_info(self):
        info = self.service.about().get(fields="user, storageQuota").execute()
        usr = info['user']
        storage = info['storageQuota']
        print("""Email: {email}\nLimit: {lim}\nUsage: {usg}""".format(email=usr['emailAddress'], lim=storage['limit'], usg=storage['usageInDrive']))
        limit = int(storage['limit'])
        usage = int(storage['usage'])
        inDrive = int(storage['usageInDrive'])
        other = usage - inDrive
        free = limit - usage
        return [free, inDrive, other]

    def analyze(self, folder='"root"'):
        folder_files = self.folder_handler.scan_folder(folder)
        if folder_files != None:
            type_counter, names, folders = self.analyzer.process_files(folder_files, True)
        else:
            pass

        for pair in type_counter.most_common():
        	print("{type} - {count}".format(type=pair[0], count=pair[1]))
        for id, name in folders:
            print('\nStarting to scan the folder {folder_name}...\n'.format(folder_name = name))
            self.analyze(id)


class FolderHandler():
    def __init__(self, service=None):
        self.service = service

    def set_service(self, service):
        self.service = service

    def read_page(self, folder='"root"', page_token=None, page_size=1000):
        results = self.service.files().list(
            pageSize = page_size,
            orderBy = 'name',
            spaces='drive',
            fields='nextPageToken, files',
            q = '{folder} in parents'.format(folder=folder),
            pageToken=page_token).execute()
        return results

    def get_files(self, folder='"root"', page_token=None, page_size=1000):
        results = self.read_page(folder, page_token, page_size)
        files = results.get('files', [])
        next_token = results.get('nextPageToken', None)
        return files, next_token

    def scan_folder(self, folder='"root"'):
        page_token = None
        file_counter = 0
        folder_files = []
        while page_token != None or file_counter == 0:
            files, page_token = self.get_files(folder, page_token)
            folder_files += files
            file_counter += len(files)
            print('{num} files scanned.'.format(num = file_counter))
            if len(files) == 0:
                break
        print('The folder has been scanned.')
        print()
        return folder_files

class Analyzer():
    def process_files(self, items, get_folders=True):
        type_counter = Counter()
        names = defaultdict(list)
        folders = [] if get_folders else None
        for item in items:
            if 'name' in item:
                name = item['name']
            else:
                name = 'unknown'

            if 'mimeType' in item:
                filetype = re.search(r'[\/\.]([a-z\-]+)$', item['mimeType'])
                if (filetype == None):
                    filetype = item['mimeType']
                else:
                    filetype = filetype.group(1)
            else:
                filetype = 'unknown'

            if 'size' in item:
                size = item['size']
            else:
                size = 0

            type_counter[filetype] += 1
            names[filetype].append((name, size))
            if get_folders:
                if filetype == "folder":
                    folders.append(('"{}"'.format(item['id']), name))

        return (type_counter, names, folders)
