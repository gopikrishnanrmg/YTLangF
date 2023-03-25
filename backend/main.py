from fastapi import FastAPI
import hashlib
import threading
import functions


app = FastAPI()

@app.get("/video/{url:path}")
async def fetch_video(url: str):
   print(url)
   hash_object = hashlib.sha256(url.encode())
   hex_dig = hash_object.hexdigest()
   functions.download_file(url,hex_dig)   
   return {"status": "success", "message": "Added"}
