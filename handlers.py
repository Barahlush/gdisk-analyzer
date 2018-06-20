from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from files_tools import extract, get_filetype, gb_str   , mb_str
import pandas as pd
import sqlite3
import os

gig = 1024 * 1024 * 1024

class DriveHandler():
#
#   Main class to handle with Drive. Connects and recieves the information from Drive.
#   Use scan_drive to get a pd.DataFrame with all files records.
#
    root = '"root"'
    def __init__(self, credential_path, email):
        self.db_handler = DataBaseHandler(email)
        self.user_id = self.db_handler.get_user_id(email)

        self.cred_path = credential_path
        self.local_cred_name = 'credentials_{}.json'.format(self.user_id)
        self.permissions = 'https://www.googleapis.com/auth/drive.metadata.readonly'

        self.service = None
        self.connect()


        self.buffer = pd.DataFrame(
            data=[['"root"', 'root', 'folder', 'folder', 0, 0, 0, None, '"root"']],
            columns=['id', 'name', 'mimeType',  'type', 'size', 'sum_size', 'files', 'viewedByMeTime', 'parent']
        ).set_index('id')

        self.folder_handler = FolderHandler()
        self.folder_handler.set_service(self.service)

        self.changes_handler = ChangesHandler(self.user_id)
        self.changes_handler.set_service(self.service)


    def connect(self):
        store = file.Storage(self.local_cred_name)
        creds = store.get()

        print("Getting credentials...")
        if not creds or creds.invalid:
            try:
                flow = client.flow_from_clientsecrets(self.cred_path, self.permissions)
                creds = tools.run_flow(flow, store)
            except:
                raise PermissionError()

        print("Connecting...")
        try:
            service = build('drive', 'v3', http=creds.authorize(Http()))
        except:
            print('Unable to get the service.')
            raise ConnectionError()

        self.service = service

        print("Succesfully authentificated!\n")

    def get_user_id(self):
        return self.user_id

    def get_drive_info(self):
        info = self.service.about().get(fields="user, storageQuota").execute()

        usr = info['user']
        email = usr['emailAddress']
        storage = info['storageQuota']
        limit = int(storage['limit'])
        usage = int(storage['usage'])
        in_drive = int(storage['usageInDrive'])

        print("\nLimit: {lim}\n".format(email=email, lim=gb_str(limit)))
        return (limit, usage, in_drive)


    def unload_buffer(self, reset_table=False):
        if reset_table:
            self.db_handler.reset_user_table(self.buffer)
        else:
            self.db_handler.upload_files(self.buffer)
        self.buffer = pd.DataFrame(
            columns=['id', 'name', 'mimeType', 'type', 'size', 'sum_size', 'files', 'viewedByMeTime', 'parent']
        ).set_index('id')

    def analyze_folder(self, folder):
        data, sum_size = self.folder_handler.scan_folder(folder)
        files = len(data[data['mimeType'] != 'folder'])
        self.buffer = pd.concat([self.buffer, data])

        self.buffer.loc[folder, 'sum_size'] += sum_size
        self.buffer.loc[folder, 'files'] += files

        if folder == '"root"' and len(data) > 1:
            self.root = data.iloc[1]['parent']
            self.buffer.rename(index={'"root"' : self.root}, inplace=True)
            self.buffer.loc[self.root, 'parent'] = self.root
            folder = self.root
        indexes = list(data[data['mimeType'] == 'folder'].index.values)
        for id in indexes:
            cur_sum_size, cur_files = self.analyze_folder(id)

            self.buffer.loc[folder, 'sum_size'] += cur_sum_size
            self.buffer.loc[folder, 'files'] += cur_files

            sum_size += cur_sum_size
            files += cur_files

        print("{0} size: {1}".format(self.buffer.loc[folder, 'name'] if folder != DriveHandler.root else "Summary", gb_str(sum_size) if sum_size > gig else mb_str(sum_size)))
        return sum_size, files


    def scan_drive(self):
        if self.changes_handler.drive_changed() or self.db_handler.db_is_new():
            print('Updating the database...')
            self.analyze_folder(DriveHandler.root)
            self.unload_buffer(reset_table=True)
        print('Saved information found!')
        return self.db_handler.get_user_table()


class ChangesHandler():
#
# Handles changes in the Drive, so you can keep your DB up to date.
# Track changes via "changes page token", reading it, you can get last changes.
# The token is stored in a csv file, using it you can see last modifications.
#
# drive_changed method returns True if there are some modifications in the Drive.
#
    def __init__(self, user_id):
        self.user_id = user_id
        self.changes_token_file = 'change_tokens.csv'
        self.changes_token = None
        self.service = None

#
# Should be initialized by set_service before using.
#
    def set_service(self, service):
        self.service = service
        new = self.check_changes_token()
        if new:
            self.create_changes_token(new)

#
# Read a stored token or return 'file' if there is not csv file
#                           and 'token' if there is a csv file but user's token is not stored.
#
    def check_changes_token(self):
        token_file_exists = os.path.isfile(self.changes_token_file)
        new = None
        if token_file_exists:
            users_with_tokens = pd.read_csv(self.changes_token_file, header=0, index_col='user_id').index
            if self.user_id in users_with_tokens:
                self.changes_token = pd.read_csv(self.changes_token_file, header=0, index_col='user_id').loc[self.user_id, 'token']
            else:
                new = 'token'
        else:
            new = 'file'
        return new
#
# Creates/appends a csv file with user's token.
#
    def create_changes_token(self, new):
        self.changes_token = self.service.changes().getStartPageToken().execute().get('startPageToken')
        mode = 'w' if new == 'file' else 'a'
        df = pd.DataFrame(data=[[self.user_id, self.changes_token]], columns=['user_id', 'token']).set_index('user_id')
        header = 'columns_names' if new == 'file' else False
        df.to_csv(self.changes_token_file, header=header, mode=mode)
#
# Shows if the Drive has recent modifications.
#
    def drive_changed(self):
        if self.changes_token:
            response = self.service.changes().list(pageToken=self.changes_token, spaces='drive', restrictToMyDrive=True).execute()
            if 'newStartPageToken' in response:
                self.changes_token = response.get('newStartPageToken')
                tokens = pd.read_csv(self.changes_token_file, header=0, index_col='user_id')
                tokens.loc[self.user_id, 'token'] = self.changes_token
                tokens.to_csv(self.changes_token_file, header='column_names', mode='w')
        else:
            return True
        return len(response.get('changes')) > 0



class DataBaseHandler():
#
# The DB has table Users with id/email mappings.
# For each user there is a table User_{user_id} which contains information about the Drive.
#
    def __init__(self, email):
        self.db_name = "database.db"
        self.ids_table_name = "Users"

        self.new = not os.path.isfile(self.db_name)
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS {0} (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL)""".format(self.ids_table_name))

        self.user_id = self.get_user_id(email)
        self.user_table_name = "User_{}".format(self.user_id)


    def __del__(self):
        self.cursor.close()
        self.connection.close()
#
# If exists, returns an user id. Creates one otherwise.
#
    def get_user_id(self, email):
        self.cursor.execute("SELECT id FROM {0} WHERE email = ?".format(self.ids_table_name), (email, ))
        data = self.cursor.fetchone()
        if data == None:
            self.cursor.execute("INSERT INTO {0}(email) VALUES(?)".format(self.ids_table_name), (email, ))
            self.new = True
        else:
            return data[0]
        self.cursor.execute("SELECT id FROM {0} WHERE email = ?".format(self.ids_table_name), (email, ))
        return self.cursor.fetchone()[0]

#
# If the user's Table wasn't created, returns True. False otherwise.
#
    def db_is_new(self):
        if self.new:
            print("New database.")
        return self.new

#
# Uploads a pd.DataFrame to the existing table.
#
    def upload_files(self, data):
        data.to_sql(self.user_table_name, self.connection, if_exists='append')
        self.new = False

#
# Drops table and creates a new onem using data (pd.DataFrame).
#
    def reset_user_table(self, data):
        print("Database reseted.")
        data.to_sql(self.user_table_name, self.connection, if_exists='replace')
        self.new = False
#
# Returns pd.DataFrame of the user's table.
#
    def get_user_table(self):
        return pd.read_sql_query('SELECT * FROM {0}'.format(self.user_table_name),
                                self.connection,
                                index_col='id')


class FolderHandler():
#
# Recieves files from a Drive folder and calculates the folder's size.
#
    root = '"root"'

    def __init__(self, service=None):
        self.service = service

#
# Should be initialized with set_service before using.
#
    def set_service(self, service):
        self.service = service

#
# read_page and get_files get files from the folder, page by page.
#
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

#
# Returns pd.DataFrame with all the files in the folder and their summary size.
#
    def scan_folder(self, folder=root):
        page_token = None
        files = []
        while page_token != None or len(files) == 0:

            cur_files, page_token = self.get_files(folder, page_token)
            files += cur_files

            if len(cur_files) == 0:
                break

        data, sum_size = extract(files)
        return data, sum_size
