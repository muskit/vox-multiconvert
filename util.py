from os import system, name

MUSIC_DB_PATH = 'data/others/music_db.xml'
MUSIC_PATH = 'data/music'
VERSION_GAME = {
    '1': "SOUND VOLTEX BOOTH",
    '2': "SOUND VOLTEX II -infinite infection-",
    '3': "SOUND VOLTEX III GRAVITY WARS",
    '4': "SOUND VOLTEX IV HEAVENLY HAVEN",
    '5': "SOUND VOLTEX VIVID WAVE",
    '6': "SOUND VOLTEX EXCEED GEAR"
}
DIFF_VOX2KSH = {
    'novice': 'light',
    'advanced': 'challenge',
    'exhaust': 'extended',
    'infinite': 'infinite',
    'maximum': 'infinite'
}

DIFF_ABBRV = {
    'novice': 'nov',
    'advanced': 'adv',
    'exhaust': 'exh',
    'infinite': 'inf',
    'maximum': 'mxm'
}

SONGID_BLACKLIST = ('1438', '1259')

def open_contents_db(path: str):
    return open('{}/{}'.format(path, MUSIC_DB_PATH), 'r', encoding='shift_jisx0213')

def content_path_valid(path: str):
    try:
        open_contents_db(path)
    except Exception:
        return False
    return True

def cls():
    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')