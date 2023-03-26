import os
import wave
import math
import torchaudio
import shutil
from pymongo import MongoClient
import yt_dlp as youtube_dl
from dotenv import load_dotenv
from models import YTRecord 
from speechbrain.pretrained import EncoderClassifier
language_id = EncoderClassifier.from_hparams(source="TalTechNLP/voxlingua107-epaca-tdnn", savedir="tmp")

client = None
db = None
collection = None

def set_mongo_client():
    global client, db, collection
    load_dotenv()
    mongouri = os.getenv("MONGODB_URI")
    client = MongoClient(mongouri)
    db = client["YT"]
    collection = db["records"]

def find_record(hash):
    return collection.find_one({"YTHash": hash})
    
def add_record(hash,langs):
    record = YTRecord(YTHash=hash, langs=langs)
    collection.insert_one(record.dict(by_alias=True))

def split_wav(filename, path, time):
    langs = []
    read = wave.open(filename, "r")
    frameRate = read.getframerate()
    numFrames = read.getnframes()
    duration = numFrames / float(frameRate)
    numSplits = int(math.ceil(duration / time))
    framesPerSplit = int(numFrames / numSplits)
    for i in range(numSplits):
        outFilename = path+"output_%s.wav" % i
        outFile = wave.open(outFilename, "w")
        outFile.setparams(read.getparams())
        for j in range(framesPerSplit):
            outFile.writeframes(read.readframes(1))
        outFile.close()
        signal = language_id.load_audio(outFilename, savedir=path)
        prediction =  language_id.classify_batch(signal)
        langs.append(prediction[3][0])
    read.close()
    return list(set(langs))
    
def download_file(url,hex_dig):
   path="../temp/"+hex_dig+"/"
   if os.path.exists(path):
       return
   os.makedirs(path)
   ydl_opts = {
	"format": "bestaudio/best",
    	"outtmpl": path+"track",
    	"postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "wav",
        "preferredquality": "192",
    }],
   }
   with youtube_dl.YoutubeDL(ydl_opts) as ydl:
       ydl.download([url])
   langs = split_wav(path+"track.wav", path, 100)
   shutil.rmtree(path)
   print(str(langs))
   add_record(hex_dig,langs)
   
