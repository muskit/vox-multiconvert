from os import system, name

MUSIC_DB_PATH = 'data/others/music_db.xml'
VERSION_GAME = {
    '1': "SOUND VOLTEX BOOTH",
    '2': "SOUND VOLTEX II -infinite infection-",
    '3': "SOUND VOLTEX III GRAVITY WARS",
    '4': "SOUND VOLTEX IV HEAVENLY HAVEN",
    '5': "SOUND VOLTEX VIVID WAVE",
    '6': "SOUND VOLTEX EXCEED GEAR"
}

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