from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import shutil
import csv
import os
import uuid
import asyncio
from .scraper import run_scraper

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "/tmp/uploads"
OUTPUT_FILE = "/tmp/output.csv"

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "status": "waiting"})

@app.post("/upload", response_class=HTMLResponse)
async def handle_upload(request: Request, file: UploadFile):
    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}.csv")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    urls = []
    with open(input_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:
                urls.append(row[0].strip())

    await run_scraper(urls, OUTPUT_FILE)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "status": "done",
        "download_url": "/download"
    })

@app.get("/download")
async def download_file():
    return FileResponse(OUTPUT_FILE, filename="output.csv")
