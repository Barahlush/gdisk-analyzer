"""
Scans your Google Drive and analyses files there.

"""
from __future__ import print_function
from handlers import DriveHandler
from files_tools import gb_str, mb_str
from plot import Analyzer
import re

credentials = '../secret/client_secret.json'
gig = 1024 * 1024 * 1024
if __name__ == "__main__":
    print('------------------------------------------')
    print('-------------|Drive Analyzer|-------------')
    print('------------------------------------------')
    email = input("Enter your email adress: ")
    print('------------------------------------------')
    try:
        gd_handler = DriveHandler(credentials, email)
    except ConnectionError:
        print('Unable to connetc to the Drive. Check your connection, login and apply the permission request.')
        sys.exit(0)
    except PermissionError:
        print('Wrong credentials. Make shure you are using your recent Google API credentials.')

    user_id = gd_handler.get_user_id()
    analyzer = Analyzer(user_id)
    data = gd_handler.scan_drive()
    sum_size = data['sum_size'].max()
    lim, usg, drive = gd_handler.get_drive_info()
    free = (lim - usg)
    other = (usg - drive)
    main_info = [free, drive, other]
    analyzer.main_info(lim, usg, drive)
    analyzer.disk_types(data)
    analyzer.top_folders(data)
    analyzer.relevant_folders(data)

    print('------------------------------------------')
