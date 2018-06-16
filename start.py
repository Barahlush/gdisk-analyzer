"""
Scans your Google Drive and analyses files there.

"""
from __future__ import print_function
from collections import Counter, defaultdict
from handlers import handle_files
from auth import auth_drive
import re

service = auth_drive()

page_token = None
type_counter = Counter()
files_by_types = defaultdict(list)

def read_page(page_token=None, page_size=1000, folder="root"):
    results = service.files().list(
        pageSize = page_size,
        orderBy = 'name',
        spaces='drive',
        fields='nextPageToken, files',
        q = '{folder} in parents'.format(folder=folder),
        pageToken=page_token).execute()
    return results

def get_files(page_token=None, page_size=1000):
    results = read_page(page_token, page_size)
    files = results.get('files', [])
    next_token = results.get('nextPageToken', None)
    return files, next_token
    

print('Reading...\n')

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
    files_count += len(files)

    print('Page - {num}.'.format(num = page_number))
    print('{num} files scanned.'.format(num = files_count))

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
for pair in type_counter.most_common():
	print("{type} - {count}".format(type=pair[0], count=pair[1]))
