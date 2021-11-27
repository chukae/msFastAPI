import json
import pathlib
from functools import lru_cache
from fastapi import (FastAPI, Depends, Request,Header,
File,
UploadFile,
HTTPException)
import io
import uuid
from fastapi.responses import HTMLResponse, FileResponse
#from starlette.requests import Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

class Settings(BaseSettings):
    app_auth_token: str
    debug: bool = False
    echo_active: bool = False

    app_auth_token_prod: str =None
    skip_auth: bool = False

    class Config:
        env_file = ".env"
@lru_cache
def get_settings():
    return Settings()

settings = get_settings()

DEBUG = settings.debug
BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"


app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
def home_view(request: Request, settings:Settings = Depends(get_settings)):
    print(BASE_DIR / "templates")
    print(settings.debug)
    return templates.TemplateResponse("home.html",{"request":request, "abe": 123})

def verify_auth(authorization =Header(None),settings:Settings = Depends(get_settings)):
    if settings.debug and settings.skip_auth:
        return
    if authorization is None:
        raise HTTPException(detail="Unauthorized", status_code=401)
    label, token = authorization.split()
    if token != settings.app_auth_token:
        raise HTTPException(detail="Unauthorized - Invalid token", status_code=401)


@app.post("/")
async def prediction_view(file:UploadFile = File(...),authorization =Header(None), settings:Settings = Depends(get_settings)):
    # if not settings.echo_active:
    #     raise HTTPException(detail="Invalid endpoint", status_code=400)
    #bytes_str= await io.BytesIO(file.read())
    #UPLOAD_DIR.mkdir(exist_ok=True)
    verify_auth(authorization, settings)
    bytes_str=  io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
        raise HTTPException(detail="Invalid Images", status_code=400)
    preds = pytesseract.image_to_string(img)
    predictions = [x for x in preds.split("/n")]
    return {"results":predictions, "original": preds}

@app.post("/img-show/", response_class=FileResponse)
async def home_img_view(file:UploadFile = File(...), settings:Settings = Depends(get_settings)):
    if not settings.echo_active:
        raise HTTPException(detail="Invalid endpoint", status_code=400)
    #bytes_str= await io.BytesIO(file.read())
    UPLOAD_DIR.mkdir(exist_ok=True)
    bytes_str=  io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
        raise HTTPException(detail="Invalid Images", status_code=400)
    fname = pathlib.Path(file.filename)
    fext = fname.suffix
    dest = UPLOAD_DIR / f"{uuid.uuid1()}{fext}"
    # with open(str(dest), 'wb') as out:
    #     out.write(bytes_str.read())
    img.save(dest)
    return dest