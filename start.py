"""
Scans your Google Drive and analyses files there.

"""
from __future__ import print_function
from handlers import DriveHandler
import re

credentials = '../secret/client_secret.json'

gd_handler = DriveHandler(credentials)

gd_handler.connect()

data, sum_size = gd_handler.analyze_drive()
print("Summary size: {size:.2f} MB.".format(size = sum_size / 1024 / 1024))
print(data.head())

print(gd_handler.get_drive_info())

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
