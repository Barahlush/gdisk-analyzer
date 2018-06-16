from collections import Counter, defaultdict
import re

def handle_files(items):
    type_counter = Counter()
    names = defaultdict(list)
    if not items:
        raise Exception('No files found!')
    else:
        for item in items:
            if 'name' in item:
                name = item['name']
            else:
                name = 'unknown'

            if 'mimeType' in item:
                filetype = re.search(r'[\/\.]([a-z\-]+)$', item['mimeType'])
                if (filetype == None):
                    filetype = item['mimeType']
                else:
                    filetype = filetype.group(1)
            else:
                filetype = 'unknown'

            if 'size' in item:
                size = item['size']
            else:
                size = 0

            type_counter[filetype] += 1
            names[filetype].append((name, size))

        return (type_counter, names)
