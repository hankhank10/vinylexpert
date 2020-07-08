import sys
import os.path

## Constants definition
api_key_path = sys.path[0] + '/api_key'

def get_key():
    if os.path.isfile(api_key_path):
        with open(api_key_path, 'r') as api_key_file:
            api_key = api_key_file.read()
            print (api_key)
        return (api_key)
    else:
        return ("")

def set_key(new_key):
    with open(api_key_path, 'w') as api_key_file:
        api_key_file.write (new_key)
    return ("success")