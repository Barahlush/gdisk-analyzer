from collections import defaultdict
import pandas as pd

import re

def get_filetype(ftype):
    filetype = re.search(r'[\/\.]([a-z\-]+)$', ftype)
    return filetype.group(1) if filetype else ftype

def get_datetime(time_string):
    return pd.to_datetime(time_string, format='%Y-%m-%dT%H:%M:%S.%fZ')

def get_simple_type(ftype):
    keywords = {
        'folder' : ['folder'],
        'video' : ['webm', 'video', 'quicktime'],
        'image' : ['jpg', 'jpeg', 'gif', 'bmp'],
        'doc' : ['text', 'plain', 'document', 'djvu', 'pdf', 'msword']}

    for key, words in keywords.items():
        for word in words:
            if word in ftype:
                return key
    return 'other'

def gb_str(bytes):
    return "{0:.2f} GB".format(bytes/1024/1024/1024)

def mb_str(bytes):
    return "{0:.2f} MB".format(bytes/1024/1024)

def get_file_path(data, file):
    path = [data.loc[file, 'name']]
    parent = data.loc[file, 'parent']
    while data.loc[parent, 'parent'] != parent: # - root feature
        path.append(data.loc[parent, 'name'])
        parent = data.loc[parent, 'parent']
    return '/' + '/'.join(list(reversed(path)))

def extract(items):
    data = pd.DataFrame(columns=['id', 'name', 'mimeType', 'type', 'size', 'sum_size', 'files', 'viewedByMeTime', 'parent']).set_index('id')
    sum_size = 0
    for file in items:
        file_attributes = defaultdict(None)

        file_attributes['id'] = ['"{}"'.format(file['id'])]
        file_attributes['name'] = [file['name'] if 'name' in file else None]
        file_attributes['size'] = [int(file['size']) if 'size' in file else 0]
        file_attributes['viewedByMeTime'] = [file['viewedByMeTime'] if 'viewedByMeTime' in file else None]
        file_attributes['mimeType'] = [get_filetype(file['mimeType']) if 'mimeType' in file else 'other']
        file_attributes['type'] = [get_simple_type(get_filetype(file['mimeType'])) if 'mimeType' in file else 'other']
        file_attributes['parent'] = ['"{}"'.format(file['parents'][0]) if 'parents' in file else None]
        file_attributes['sum_size'] = 0
        file_attributes['files'] = 0

        rec = pd.DataFrame.from_dict(file_attributes).set_index('id')
        data = pd.concat([data, rec])

        sum_size += int(file_attributes['size'][0])

    return data, sum_size
