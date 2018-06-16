from collections import Counter, defaultdict
import re

def handle_files(items):
    type_counter = Counter()
    names = defaultdict(list)
    if not items:
        raise Exception('No files found!')
    else:
        for item in items:
            try:
                name = item['name']
            except:
                name = 'unknown'
            try:
                filetype = re.search(r'[\/\.]([a-z\-]+)$', item['mimeType'])
                if (filetype == None):
                    filetype = item['mimeType']
                else:
                    filetype = filetype.group(1)
            except:
                filetype = 'unknown'

            type_counter[filetype] += 1
            names[filetype].append(name)

        return (type_counter, names)
