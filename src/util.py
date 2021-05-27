from os import system, name

MUSIC_DB_PATH = 'data/others/music_db.xml'

def cls():
    # for windows
    if name == 'nt':
        _ = system('cls')
  
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

def open_contents_db(path: str):
    return open('{}/{}'.format(path, MUSIC_DB_PATH), 'r', encoding='shift_jisx0213')

def content_path_valid(path: str):
    try:
        open_contents_db(path)
    except Exception:
        return False
    return True