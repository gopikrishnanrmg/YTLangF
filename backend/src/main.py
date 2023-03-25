from fastapi import FastAPI
import hashlib
import threading
import functions

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    functions.set_mongo_client()

@app.get("/video/{url:path}")
async def fetch_video(url: str):
   print(url)
   #functions.set_mongo_client()
   hashObject = hashlib.sha256(url.encode())
   hexDig = hashObject.hexdigest()
   record = functions.find_record(hexDig)
   if record:
       return {"status": "success", "message": str(record)}
   else:
       functions.download_file(url,hexDig)   
       return {"status": "success", "message": "Added"}

'''   
if __name__ == "__main__":
    functions.set_mongo_client()
    uvicorn.run(app)
'''
