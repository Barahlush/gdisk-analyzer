"""
Scans your Google Drive and analyses files there.

"""
from __future__ import print_function
from collections import Counter, defaultdict
from handlers import handle_files
from auth import auth_drive
import re


# Call the Drive v3 API

service = auth_drive()

page_token = None
type_counter = Counter()
files_list = defaultdict(list)

page_number = 0
files_count = 0
page_size = 1000

print('Reading...')
while True:
    print('Page - {num}.'.format(num = page_number))
    print('{num} files scanned.'.format(num = files_count))
    results = service.files().list(
        pageSize = page_size,
        spaces='drive',
        fields='nextPageToken, files(id, name, mimeType)',
        pageToken=page_token).execute()

    files = results.get('files', [])
    counter, names = handle_files(files)
    type_counter += counter
    for type, filenames in names.items():
        files_list[type] += filenames

    page_number += 1
    files_count += page_size

    page_token = results.get('nextPageToken', None)
    if page_token == None:
        break

print()
for pair in type_counter.most_common():
	print("{type} - {count}".format(type=pair[0], count=pair[1]))
