import time

import requests

BASE_URL = "http://localhost:50000"


def test_tts():
    response = requests.post(f"{BASE_URL}/tts", json={
        "text": "我是机器人哈哈哈哈哈",
        "speaker": "中文女"
    })
    res = response.json()
    print('tts.queue', res)
    jobId = res['data']['jobId']
    for i in range(60):
        time.sleep(1)
        response = requests.post(f"{BASE_URL}/query", json={
            "jobId": jobId
        })
        res = response.json()
        print('tts.query', res)
        if res['data']['status'] == 'success' or res['data']['status'] == 'fail':
            break


def test_voiceClone():
    response = requests.post(f"{BASE_URL}/voiceClone", json={
        # "text": "我是机器人哈哈哈哈哈",
        "text": "Hello everyone, I am a robot.",
        "promptAudio": "",
        "promptText": "",
        "param": {
            "CrossLingual": True
        },
    })
    res = response.json()
    print('voiceClone.queue', res)
    jobId = res['data']['jobId']
    for i in range(60):
        time.sleep(1)
        response = requests.post(f"{BASE_URL}/query", json={
            "jobId": jobId
        })
        res = response.json()
        print('voiceClone.query', res)
        if res['data']['status'] == 'success' or res['data']['status'] == 'fail':
            break


if __name__ == "__main__":
    # test_tts()
    test_voiceClone()
