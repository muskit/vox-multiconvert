from os.path import exists
import configparser

global confParser
global contentPath
global exportPath
global ffmpegPath

def parse_conf():
    ret = configparser.ConfigParser()
    ret['PATHS'] = {
        'contentPath': '',
        'exportPath': '',
        'ffmpegPath': ''
    }
    if exists('config.ini'):
        fileObj = open('config.ini', 'r')
        ret.read_file(fileObj)
        fileObj.close()
    return ret

# load config; create if doesn't exist
def init():
    global confParser
    global contentPath
    global exportPath
    global ffmpegPath
    confParser = parse_conf()
    contentPath = confParser['PATHS']['contentPath']
    exportPath = confParser['PATHS']['exportPath']
    ffmpegPath = confParser['PATHS']['ffmpegPath']



def save():
    print('Saving...')
    confParser['PATHS']['contentPath'] = contentPath
    confParser['PATHS']['exportPath'] = exportPath
    confParser['PATHS']['ffmpegPath'] = ffmpegPath

    fileObj = open('config.ini', 'w')
    confParser.write(fileObj)
    fileObj.close()