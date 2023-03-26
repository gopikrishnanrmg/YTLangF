from fastapi import FastAPI, BackgroundTasks
import hashlib
import threading
import functions
from fastapi.concurrency import run_in_threadpool

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    functions.set_mongo_client()

@app.get("/video/{url:path}")
async def fetch_video(url: str, background_tasks: BackgroundTasks):
   print(url)
   hashObject = hashlib.sha256(url.encode())
   hexDig = hashObject.hexdigest()
   record = functions.find_record(hexDig)
   if record:
       return {"status": "success", "message": str(record)}
   else:
       background_tasks.add_task(functions.download_file, url, hexDig)
       return {"status": "failure", "message": "Adding info about this file"}

