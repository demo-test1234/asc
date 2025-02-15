import json
import base64


def jsonStringify(data):
    return json.dumps(data)


def build(data):
    jsonData = json.dumps(data)
    base64Data = base64.b64encode(jsonData.encode('utf-8')).decode('utf-8')
    return base64Data


def param(key, value):
    data = {key: value}
    print(f'Param[{jsonStringify(data)}]')
    print(f'AigcPanelRunParam[{build(data)}]')


def output(data):
    print(f'Output[{jsonStringify(data)}]')
    print(f'AigcPanelRunResult[{build(data)}]')
