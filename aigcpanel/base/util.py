import sys, os, datetime, random


def banner(param: dict):
    print('##################### MSBrick Info #####################')
    print('root:', root())
    if 'args' in param:
        print('args:', param['args'])
    print('######################################################')


def root():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.dirname(sys.executable)) + os.sep + '_dep'
    else:
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def rootDir(path):
    return root() + os.sep + path


def datetimeRandomName():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S_') + str(random.randint(1000, 9999))


def datetimeRandomNameParseTimestamp(name):
    if len(name) < 14:
        return 0
    return datetime.datetime.strptime(name[:14], '%Y%m%d%H%M%S').timestamp()
