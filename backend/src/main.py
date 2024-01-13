import hashlib
import threading
import functions
import logging
import variables
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from bson import json_util


count_list = [0]

app = FastAPI()

origins = [
    "https://www.youtube.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    functions.init()
    functions.set_mongo_client()

@app.get("/video/{url:path}")
async def fetch_video(url: str, background_tasks: BackgroundTasks):
   variables.logger.info("Request incoming "+url)
   hashObject = hashlib.sha256(url.encode())
   hexDig = hashObject.hexdigest()
   record = functions.find_record(hexDig)
   variables.logger.debug("Fetching from database "+str(json_util.dumps(record)))
   if record:
       return {"status": "success", "message": str(json_util.dumps(record))}
   else:
       while(count_list[0]>=variables.maxThreads):
           pass     
       count_list[0] = count_list[0]+1
       variables.logger.debug("count is "+str(count_list[0]))
       background_tasks.add_task(functions.download_file, url, hexDig, count_list)
       return {"status": "failure", "message": "Adding info about this file"}

