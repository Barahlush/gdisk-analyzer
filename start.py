"""
Scans your Google Drive and analyses files there.

"""
from __future__ import print_function
from handlers import DriveHandler
import re

credentials = '../secret/client_secret.json'

gd_handler = DriveHandler(credentials)

gd_handler.connect()

gd_handler.analyze()


'''
```
page_number = 0
files_count = 0
file_limit = None

while True:
    # Read files
    files, page_token = get_files(page_token)
    counter, names = handle_files(files)

    # Update dictionaries
    type_counter += counter
    for type, filenames in names.items():
        files_by_types[type] += filenames

    # Update counters
    page_number += 1

    print('Page - {num}.'.format(num = page_number))

    if file_limit:
        if files_count >= file_limit:
            break

    if page_token == None:
        break

# Output
print()
sum_size = 0
for type, files in files_by_types.items():
    for title, size in files:
        print(title, size)
        sum_size += int(size)
print("Summary size: {size}.\n".format(size=sum_size))
'''
