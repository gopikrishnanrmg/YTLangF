import hashlib
import threading
import functions
import logging
import variables
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bson import json_util

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
async def fetch_video(url: str):
   variables.logger.info("Request incoming "+url)
   hashObject = hashlib.sha256(url.encode())
   hexDig = hashObject.hexdigest()
   record = functions.find_record(hexDig)
   variables.logger.debug("Fetching from database "+str(json_util.dumps(record)))
   if record:
       return {"status": "success", "message": str(json_util.dumps(record))}
   else:
       job = {}
       job["url"] = url
       job["hash"] = hexDig
       if job not in variables.jobURLList:
           variables.jobURLList.append(job)
           variables.logger.debug("Added job "+str(job))
       return {"status": "failure", "message": "Adding info about this file"}

