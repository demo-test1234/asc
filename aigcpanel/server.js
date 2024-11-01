const serverRuntime = {
    port: 0,
}

let shellController = null

module.exports = {
    ServerApi: null,
    _url() {
        return `http://localhost:${serverRuntime.port}/`
    },
    async _client() {
        return await this.ServerApi.GradioClient.connect(this._url());
    },
    _send(serverInfo, type, data) {
        this.ServerApi.event.sendChannel(serverInfo.eventChannelName, {type, data})
    },

    async init(ServerApi) {
        this.ServerApi = ServerApi;
    },
    async start(serverInfo) {
        // console.log('this.ServerApi.app.availablePort(50617)', await this.ServerApi.app.availablePort(50617))
        this._send(serverInfo, 'starting', serverInfo)
        let command = []
        if (serverInfo.setting?.['port']) {
            serverRuntime.port = serverInfo.setting.port
        } else if (!serverRuntime.port || !await this.ServerApi.app.isPortAvailable(serverRuntime.port)) {
            serverRuntime.port = await this.ServerApi.app.availablePort(50617)
        }
        if (serverInfo.setting?.['startCommand']) {
            command.push(serverInfo.setting.startCommand)
        } else {
            command.push(`"${serverInfo.localPath}/main"`)
            command.push(`--port=${serverRuntime.port}`)
            if (serverInfo.setting?.['gpuMode'] === 'cpu') {
                command.push('--gpu_mode=cpu')
            }
        }
        shellController = await this.ServerApi.app.spawnShell(command, {
            stdout: (data) => {
                this.ServerApi.file.appendText(serverInfo.logFile, data)
            },
            stderr: (data) => {
                this.ServerApi.file.appendText(serverInfo.logFile, data)
            },
            success: (data) => {
                this._send(serverInfo, 'success', serverInfo)
            },
            error: (data, code) => {
                this.ServerApi.file.appendText(serverRuntime.logFile, data)
                this._send(serverInfo, 'error', serverInfo)
            },
        })
    },
    async ping(serverInfo) {
        try {
            const client = await this._client()
            const result = await client.predict("/change_instruction", {
                mode_checkbox_group: "预训练音色",
            });
            return true
        } catch (e) {
        }
        return false
    },
    async stop(serverInfo) {
        this._send(serverInfo, 'stopping', serverInfo)
        try {
            shellController.stop()
            shellController = null
        } catch (e) {
            console.log('stop error', e)
        }
        this._send(serverInfo, 'stopped', serverInfo)
    },
    async config() {
        return {
            "code": 0,
            "msg": "ok",
            "data": {
                "httpUrl": shellController ? this._url() : null,
                "functions": {
                    "soundClone": {
                        "param": [
                            {
                                name: "speed",
                                type: "slider",
                                title: "语速",
                                icon: "iconfont icon-speed",
                                defaultValue: 1.0,
                                placeholder: "请输入语速",
                                min: 0.5,
                                max: 2,
                                step: 0.1,
                                sliderMarks: {'0.5': '慢', '1': '正常', '2': '快'},
                            },
                            {
                                name: "seed",
                                type: "inputNumber",
                                title: "随机种子",
                                icon: "iconfont icon-seed",
                                defaultValue: 0,
                                placeholder: "请输入随机种子",
                                tips: '相同的种子可以确保每次生成结果数据一致',
                                min: 0,
                                max: 999999,
                            },
                            {
                                name: "crossLingual",
                                type: "switch",
                                title: "跨语种复刻",
                                defaultValue: false,
                                placeholder: "请输入语速",
                                tips: "跨语种克隆时需要特殊处理，因此需要标记是否为跨语种克隆"
                            }
                        ],
                    },
                    "soundTts": {
                        "param": [
                            {
                                name: "speaker",
                                type: "select",
                                title: "音色",
                                icon: "iconfont icon-speaker",
                                defaultValue: "中文女",
                                placeholder: "请选择音色",
                                options: [
                                    {label: "中文女", value: "中文女"},
                                    {label: "中文男", value: "中文男"},
                                    {label: "日语男", value: "日语男"},
                                    {label: "粤语女", value: "粤语女"},
                                    {label: "英文女", value: "英文女"},
                                    {label: "英文男", value: "英文男"},
                                    {label: "韩语女", value: "韩语女"},
                                ]
                            },
                            {
                                name: "speed",
                                type: "slider",
                                title: "语速",
                                icon: "iconfont icon-speed",
                                defaultValue: 1.0,
                                placeholder: "请输入语速",
                                min: 0.5,
                                max: 2,
                                step: 0.1,
                                sliderMarks: {'0.5': '慢', '1': '正常', '2': '快'},
                            },
                            {
                                name: "seed",
                                type: "inputNumber",
                                title: "随机种子",
                                icon: "iconfont icon-seed",
                                tips: '相同的种子可以确保每次生成结果数据一致',
                                defaultValue: 0,
                                placeholder: "请输入随机种子",
                                min: 0,
                                max: 999999,
                            }
                        ],
                    }
                }
            }
        }
    },
    async soundTts(serverInfo, data) {
        // soundTts { text: '你好', speaker: '中文女', speed: 1, seed: 0 }
        // console.log('soundTts', data)
        const client = await this._client()
        const resultData = {
            // success, querying, retry
            type: 'success',
            start: 0,
            end: 0,
            jobId: '',
            data: {
                filePath: null
            }
        }
        resultData.start = Date.now()
        const result = await client.predict("/generate_audio", {
            mode_checkbox_group: "预训练音色",
            tts_text: data.text,
            sft_dropdown: data.param.speaker,
            prompt_text: "",
            prompt_wav_upload: null,
            prompt_wav_record: null,
            instruct_text: "",
            seed: parseInt(data.param.seed),
            stream: "false",
            speed: parseFloat(data.param.speed),
        });
        resultData.end = Date.now()
        resultData.data.filePath = await this.ServerApi.file.temp('wav')
        const resultWav = result.data[0].url
        await this.ServerApi.requestUrlFileToLocal(resultWav, resultData.data.filePath)
        return {
            code: 0,
            msg: 'ok',
            data: resultData
        }
    },
    async soundClone(serverInfo, data) {
        // soundTts { text: '你好', promptAudio: '/path/to/wav.wav', promptText: '文字', speed: 1, seed: 0 }
        // console.log('soundClone', data)
        const client = await this._client()
        const resultData = {
            // success, querying, retry
            type: 'success',
            start: 0,
            end: 0,
            jobId: '',
            data: {
                filePath: null
            }
        }
        const param = data.param || {}
        resultData.start = Date.now()
        const result = await client.predict("/generate_audio", {
            mode_checkbox_group: param['CrossLingual'] ? "跨语种复刻" : "3s极速复刻",
            tts_text: data.text,
            sft_dropdown: "",
            prompt_text: data.promptText,
            prompt_wav_upload: this.ServerApi.GradioHandleFile(data.promptAudio),
            prompt_wav_record: null,
            instruct_text: "",
            seed: parseInt(data.param.seed),
            stream: "false",
            speed: parseFloat(data.param.speed),
        });
        // console.log('soundClone.result', result)
        resultData.end = Date.now()
        resultData.data.filePath = await this.ServerApi.file.temp('wav')
        const resultWav = result.data[0].url
        await this.ServerApi.requestUrlFileToLocal(resultWav, resultData.data.filePath)
        return {
            code: 0,
            msg: 'ok',
            data: resultData
        }
    },

}
