"""
Scans your Google Drive and analyses files there.

"""
from __future__ import print_function
from handlers import DriveHandler
from files_tools import gb_str, mb_str
from plot import Analyzer
import sys
import os
import re

credentials = '../../secret/client_secret.json'
gig = 1024 * 1024 * 1024
def analyze():
    print('------------------------------------------')
    print('-------------|Drive Analyzer|-------------')
    print('------------------------------------------')
    #email = input("Enter your email adress: ")
    print('------------------------------------------')
    try:
        gd_handler = DriveHandler(credentials)
    except ConnectionError:
        print('Unable to connetc to the Drive. Check your connection, login and apply the permission request.')
        sys.exit(0)
    except PermissionError:
        print('Wrong credentials. Make shure you are using your recent Google API credentials.')
        sys.exit(0)

    user_id = gd_handler.get_user_id()
    analyzer = Analyzer(user_id)
    data = gd_handler.scan_drive()
    sum_size = data['sum_size'].max()
    lim, usg, drive = gd_handler.get_drive_info()
    free = (lim - usg)
    other = (usg - drive)

    main_info = analyzer.main_info(lim, usg, drive)
    types_info = analyzer.disk_types(data)
    top_folders_info = analyzer.top_folders(data)
    relevant_info = analyzer.relevant_folders(data)
    return [main_info, types_info, top_folders_info, relevant_info], user_id


    print('------------------------------------------')
