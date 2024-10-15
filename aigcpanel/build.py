import json

from .base import util

configFile = util.rootDir('aigcpanel/config.json')
config = json.load(open(configFile))

config['platformName'] = util.platformName()
config['platformArch'] = util.platformArch()

outputFile = util.rootDir('dist/server-cosyvoice/config.json')
json.dump(config, open(outputFile, 'w'), indent=4, ensure_ascii=False)

print(config['version'])