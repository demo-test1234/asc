import numpy
import soundfile
import uvicorn
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse
import aigcpanel.base.job
from cosyvoice.utils.common import set_all_random_seed
from cosyvoice.utils.file_utils import load_wav

app = FastAPI()

runtime = {
    'cosyvoice': None
}


@app.get("/ping")
async def ping():
    return JSONResponse(content={"code": 0, "msg": "ok"})


@app.post("/config")
async def config():
    data = {
        "functions": {
            "voiceClone": {
            },
            "tts": {
                "speakers": runtime['cosyvoice'].list_avaliable_spks()
            }
        }
    }
    return JSONResponse(content={"code": 0, "msg": "ok", "data": data})


@app.post("/tts")
async def tts(request: Request, background_tasks: BackgroundTasks):
    if aigcpanel.base.job.overCount():
        return JSONResponse(content={"code": -1, "msg": "Too many Jobs"})

    body = await request.json()
    seed = body.get("seed", 0)
    speed = body.get("speed", 1.0)
    text = body.get("text")
    speaker = body.get("speaker")
    param = body.get("param", {})

    if not text or not speaker:
        return JSONResponse(content={"code": -1, "msg": "Invalid request"})

    jobId = aigcpanel.base.job.create({"filePath": None})

    def process():
        try:
            set_all_random_seed(seed)
            audio_data = []
            for i in runtime['cosyvoice'].inference_sft(text, speaker, stream=False, speed=speed):
                audio_data.append(i['tts_speech'].numpy().flatten())
            audio_data = numpy.concatenate(audio_data)
            filePath = aigcpanel.base.job.outputPath(f"{jobId}.wav")
            soundfile.write(filePath, audio_data, 22050)
            aigcpanel.base.job.updateSuccess(jobId, {"filePath": filePath})
        except Exception as e:
            aigcpanel.base.job.updateFail(jobId, str(e))
            print('error', e)

    background_tasks.add_task(process)

    return JSONResponse(content={"code": 0, "msg": "ok", "data": {"jobId": jobId}})


@app.post("/voiceClone")
async def voiceClone(request: Request, background_tasks: BackgroundTasks):
    if aigcpanel.base.job.overCount():
        return JSONResponse(content={"code": -1, "msg": "Too many Jobs"})

    body = await request.json()
    seed = body.get("seed", 0)
    speed = body.get("speed", 1.0)
    text = body.get("text")
    promptAudio = body.get("promptAudio")
    promptText = body.get("promptText")
    # 跨语种
    param = body.get("param", {})
    if not text or not promptAudio or not promptText:
        return JSONResponse(content={"code": -1, "msg": "Invalid request"})

    jobId = aigcpanel.base.job.create({"filePath": None})

    def process():
        try:
            set_all_random_seed(seed)
            prompt_speech_16k = postprocess(load_wav(promptAudio, 16000))
            audio_data = []
            if 'CrossLingual' in param and param['CrossLingual']:
                # 跨语种复刻
                for i in runtime['cosyvoice'].inference_cross_lingual(text, prompt_speech_16k,
                                                                      stream=False, speed=speed):
                    audio_data.append(i['tts_speech'].numpy().flatten())
            else:
                # 3s极速复刻
                for i in runtime['cosyvoice'].inference_zero_shot(text, promptText, prompt_speech_16k,
                                                                  stream=False, speed=speed):
                    audio_data.append(i['tts_speech'].numpy().flatten())
            audio_data = numpy.concatenate(audio_data)
            filePath = aigcpanel.base.job.outputPath(f"{jobId}.wav")
            soundfile.write(filePath, audio_data, 22050)
            aigcpanel.base.job.updateSuccess(jobId, {"filePath": filePath})
        except Exception as e:
            aigcpanel.base.job.updateFail(jobId, str(e))
            print('error', e)

    background_tasks.add_task(process)

    return JSONResponse(content={"code": 0, "msg": "ok", "data": {"jobId": jobId}})


@app.post("/query")
async def query(request: Request):
    body = await request.json()
    job = aigcpanel.base.job.get(body.get("jobId"))
    if not job:
        return JSONResponse(content={"code": -1, "msg": "Job not found"})
    return JSONResponse(content={"code": 0, "msg": "ok", "data": job})


def run(args):
    uvicorn.run(app, host="127.0.0.1", port=args.port)


import librosa
import torch

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
