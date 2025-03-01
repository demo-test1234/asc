import os
import sys

import _aigcpanel.base.file
import _aigcpanel.base.result
import _aigcpanel.base.util
import _aigcpanel.base.log

if len(sys.argv) != 2:
    print("Usage: python -u -m aigcpanelrun <config_url>")
    exit(-1)

###### 模型数据开始 ######
import torch
import numpy as np
import soundfile
import librosa

useCuda = torch.cuda.is_available()
_aigcpanel.base.log.info('开始运行', {'UseCuda': useCuda})
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["MODELSCOPE_CACHE"] = os.path.join(ROOT_DIR, '_cache', 'modelscope')
sys.path.append('{}/third_party/Matcha-TTS'.format(ROOT_DIR))
from cosyvoice.cli.cosyvoice import CosyVoice
from cosyvoice.utils.common import set_all_random_seed
from cosyvoice.utils.file_utils import load_wav

sys.path.append('{}/binary'.format(ROOT_DIR))


def main():
    config = _aigcpanel.base.file.contentJson(sys.argv[1])
    _aigcpanel.base.log.info('config', config, sys.argv)
    if not 'id' in config:
        _aigcpanel.base.log.info('config.id not found')
        exit(-1)
    _aigcpanel.base.result.result(config, {'UseCuda': useCuda})
    if not 'mode' in config:
        config['mode'] = 'local'
    modelConfig = config['modelConfig']
    model_dir = _aigcpanel.base.util.rootDir('aigcpanelmodels/CosyVoice-300M')
    cosyvoice = CosyVoice(model_dir)
    prompt_sr, target_sr = 16000, 22050
    default_data = np.zeros(target_sr)

    if modelConfig['type'] == 'tts':
        _aigcpanel.base.log.info('tts', modelConfig)
        set_all_random_seed(modelConfig['seed'])
        audio_data = []
        for i in cosyvoice.inference_sft(modelConfig['text'],
                                         modelConfig['speakerId'],
                                         stream=False,
                                         speed=modelConfig['speed']):
            _aigcpanel.base.log.info('tts.i', i)
            audio_data.append(i['tts_speech'].numpy().flatten())
        audio_data = np.concatenate(audio_data)
        url = _aigcpanel.base.file.localCacheRandomPath('wav')
        soundfile.write(url, audio_data, 22050)
        _aigcpanel.base.result.result(config, {'url': _aigcpanel.base.file.urlForResult(config, url)})
        return

    if modelConfig['type'] == 'soundClone':
        _aigcpanel.base.log.info('soundClone', modelConfig)
        set_all_random_seed(modelConfig['seed'])
        modelConfig['_promptAudio'] = _aigcpanel.base.file.localCache(modelConfig['promptAudio'])
        prompt_speech_16k = postprocess(load_wav(modelConfig['_promptAudio'], 16000))
        audio_data = []
        if modelConfig['crossLingual']:
            # 跨语种复刻
            for i in cosyvoice.inference_cross_lingual(modelConfig['text'],
                                                       prompt_speech_16k,
                                                       stream=False,
                                                       speed=modelConfig['speed']):
                audio_data.append(i['tts_speech'].numpy().flatten())
        else:
            # 3s极速复刻
            for i in cosyvoice.inference_zero_shot(modelConfig['text'],
                                                   modelConfig['promptText'],
                                                   prompt_speech_16k,
                                                   stream=False,
                                                   speed=modelConfig['speed']):
                audio_data.append(i['tts_speech'].numpy().flatten())
        audio_data = np.concatenate(audio_data)
        url = _aigcpanel.base.file.localCacheRandomPath('wav')
        soundfile.write(url, audio_data, 22050)
        _aigcpanel.base.result.result(config, {'url': _aigcpanel.base.file.urlForResult(config, url)})
        return

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
