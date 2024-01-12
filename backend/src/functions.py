import os
import wave
import math
import torchaudio
import shutil
import configparser
import variables
import yt_dlp as youtube_dl
from pymongo import MongoClient
from dotenv import load_dotenv
from models import YTRecord 
from speechbrain.pretrained import EncoderClassifier
language_id = EncoderClassifier.from_hparams(source="TalTechNLP/voxlingua107-epaca-tdnn", savedir="tmp")

client = None
db = None
collection = None


def init():
    config = configparser.ConfigParser()
    if os.path.exists(variables.configFilePath):
        config.read(variables.configFilePath)
        variables.maxFileSize = int(config.get("Settings", "maxFileSize"))
        variables.maxThreads = int(config.get("Settings", "maxThreads"))
        variables.tempFolderPath = config.get("Settings", "tempFolderPath")
        variables.timeSlice = int(config.get("Settings", "timeSlice"))
    else:
        config.add_section("Settings")
        config.set("Settings", "maxFileSize", str(1073741824))
        config.set("Settings", "maxThreads", str(2))
        config.set("Settings", "tempFolderPath", "../temp/")
        config.set("Settings", "timeSlice", str(100))
        with open(variables.configFilePath, "w") as f:
            config.write(f)


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

def split_wav(filename, path):
    langs = []
    read = wave.open(filename, "r")
    frameRate = read.getframerate()
    numFrames = read.getnframes()
    duration = numFrames / float(frameRate)
    numSplits = int(math.ceil(duration / variables.timeSlice))
    framesPerSplit = int(numFrames / numSplits)
    for i in range(numSplits):
        outFilename = path+"output_%s.wav" % i
        outFile = wave.open(outFilename, "w")
        outFile.setparams(read.getparams())
        outFile.writeframes(read.readframes(framesPerSplit))
        outFile.close()
        signal = language_id.load_audio(outFilename, savedir=path)
        prediction =  language_id.classify_batch(signal)
        langs.append(prediction[3][0])
    read.close()
    return list(set(langs))
    
def download_file(url, hex_dig, count_list):
   path = variables.tempFolderPath+hex_dig+"/"
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
   file_size = os.path.getsize(path+"track.wav")

   if(file_size > variables.maxFileSize):
       shutil.rmtree(path)
       count_list[0] = count_list[0]-1
       return

   langs = split_wav(path+"track.wav", path)
   shutil.rmtree(path)
   print(str(langs))
   add_record(hex_dig,langs)
   count_list[0] = count_list[0]-1
   print("count is "+str(count_list[0]))