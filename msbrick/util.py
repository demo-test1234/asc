import sys, os


def banner(param: dict):
    print('##################### MSBrick Info #####################')
    print('root:', root())
    if 'args' in param:
        print('args:', param['args'])
    print('######################################################')


def root():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable) + os.sep + '_dep'
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rootDir(path):
    return root() + os.sep + path
