import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/ping")
async def ping():
    return JSONResponse(content={"code": 0, "msg": "ok"})


def get_app():
    return app


def set_app(newApp):
    global app
    app = newApp

def mount_gradio(gradio_app):
    app.mount("/", gradio_app)


def run(args):
    uvicorn.run(app, host="127.0.0.1", port=args.port)
