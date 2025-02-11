import json
import os
import sys

import _aigcpanel.base.file
import _aigcpanel.base.util
import _aigcpanel.base.result

if len(sys.argv) != 2:
    print("Usage: python aigcpanelrun.py <config_url>")
    exit(-1)

###### 模型数据开始 ######
import torch
import numpy as np
import soundfile
import librosa

useGpu = torch.cuda.is_available()
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["GRADIO_SHARE"] = "false"
os.environ["GRADIO_ANALYTICS_ENABLED"] = "false"
os.environ["MODELSCOPE_CACHE"] = os.path.join(ROOT_DIR, '_cache', 'modelscope')
sys.path.append('{}/third_party/Matcha-TTS'.format(ROOT_DIR))
from cosyvoice.cli.cosyvoice import CosyVoice
from cosyvoice.utils.common import set_all_random_seed
from cosyvoice.utils.file_utils import load_wav

sys.path.append('{}/binary'.format(ROOT_DIR))


def main():
    config = _aigcpanel.base.file.contentJson(sys.argv[1])
    print('config', config)
    modelConfig = config['modelConfig']
    model_dir = _aigcpanel.base.util.rootDir('aigcpanelmodels/CosyVoice-300M')
    cosyvoice = CosyVoice(model_dir)
    prompt_sr, target_sr = 16000, 22050
    default_data = np.zeros(target_sr)
    if modelConfig['type'] == 'tts':
        print('tts', modelConfig)
        set_all_random_seed(modelConfig['seed'])
        audio_data = []
        for i in cosyvoice.inference_sft(modelConfig['text'],
                                         modelConfig['speakerId'],
                                         stream=False,
                                         speed=modelConfig['speed']):
            print('tts.i', i)
            audio_data.append(i['tts_speech'].numpy().flatten())
        audio_data = np.concatenate(audio_data)
        filePath = _aigcpanel.base.file.localCacheRandomPath('wav')
        soundfile.write(filePath, audio_data, 22050)
        url = _aigcpanel.base.file.uploadToRandom(config['uploadConfig'], filePath)
        _aigcpanel.base.result.output({'url': url})
    elif modelConfig['type'] == 'soundClone':
        print('soundClone', modelConfig)
        set_all_random_seed(modelConfig['seed'])
        modelConfig['_promptAudio'] = _aigcpanel.base.file.localCache(modelConfig['promptAudio'])
        prompt_speech_16k = postprocess(load_wav(modelConfig['_promptAudio'], 16000))
        audio_data = []
        if modelConfig['crossLingual']:
            # 跨语种复刻
            for i in cosyvoice.inference_cross_lingual(modelConfig['text'],
                                                       prompt_speech_16k,
                                                       stream=False, speed=modelConfig['speed']):
                audio_data.append(i['tts_speech'].numpy().flatten())
        else:
            # 3s极速复刻
            for i in cosyvoice.inference_zero_shot(modelConfig['text'],
                                                   modelConfig['promptText'],
                                                   prompt_speech_16k,
                                                   stream=False, speed=modelConfig['speed']):
                audio_data.append(i['tts_speech'].numpy().flatten())
        audio_data = np.concatenate(audio_data)
        filePath = _aigcpanel.base.file.localCacheRandomPath('wav')
        soundfile.write(filePath, audio_data, 22050)
        url = _aigcpanel.base.file.uploadToRandom(config['uploadConfig'], filePath)
        _aigcpanel.base.result.output({'url': url})
    else:
        raise Exception('Unknown model type:', modelConfig['type'])


max_val = 0.8


def postprocess(speech, top_db=60, hop_length=220, win_length=440):
    speech, _ = librosa.effects.trim(
        speech, top_db=top_db,
        frame_length=win_length,
        hop_length=hop_length
    )
    if speech.abs().max() > max_val:
        speech = speech / speech.abs().max() * max_val
    speech = torch.concat([speech, torch.zeros(1, int(22050 * 0.2))], dim=1)
    return speech


main()

###### 模型数据结束 ######
