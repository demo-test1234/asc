import json
import base64


def build(data):
    jsonData = json.dumps(data)
    base64Data = base64.b64encode(jsonData.encode('utf-8')).decode('utf-8')
    return base64Data

def output(data):
    print(f'\nAigcPanelRunResult[{build(data)}]\n')