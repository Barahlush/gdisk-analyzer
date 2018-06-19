from collections import defaultdict
import pandas as pd
import re

def get_filetype(ftype):
    filetype = re.search(r'[\/\.]([a-z\-]+)$', ftype)
    return filetype.group(1) if filetype else ftype

def get_datetime(time_string):
    return pd.to_datetime(time_string, format='%Y-%m-%dT%H:%M:%S.%fZ')

def extract(items):
    data.DataFrame(columns=['id', 'name', 'mimeType', 'size', 'sum_size', 'viewedByMeTime', 'parent']).set_index('id')
    sum_size = 0
    for file in items:
        file_attributes = defaultdict(None)

        file_attributes['id'] = ['"{}"'.format(file['id'])]
        file_attributes['name'] = [file['name'] if 'name' in file else None]
        file_attributes['size'] = [file['size'] if 'size' in file else 0]
        file_attributes['viewedByMeTime'] = [get_datetime(file['viewedByMeTime']) if 'viewedByMeTime' in file else None]
        file_attributes['mimeType'] = [get_filetype(file['mimeType']) if 'mimeType' in file else None]
        file_attributes['parent'] = ['"{}"'.format(file['parents'][0]) if 'parents' in file else None]
        file_attributes['sum_size'] = [file_attributes['size']]
        rec = pd.DataFrame.from_dict(file_attributes).set_index('id')
        data = pd.concat([data, rec])

        sum_size += int(file_attributes['size'][0])

    return data, sum_size
