import os
import wave
import math
import torchaudio
import shutil
import configparser
import logging
import threading
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
lock = False
count = 0

#Creates or reads the config file and initializes the logger 

def init():
    config = configparser.ConfigParser()
    if os.path.exists(variables.configFilePath):
        config.read(variables.configFilePath)
        variables.maxFileSize = int(config.get("Settings", "maxFileSize"))
        variables.maxThreads = int(config.get("Settings", "maxThreads"))
        variables.logLevel = config.get("Settings", "logLevel")
        variables.tempFolderPath = config.get("Settings", "tempFolderPath")
        variables.timeSlice = int(config.get("Settings", "timeSlice"))
    else:
        variables.maxFileSize = 1073741824
        variables.maxThreads = 2
        variables.logLevel = "debug"
        variables.tempFolderPath = "../temp/"
        variables.timeSlice = 100
        config.add_section("Settings")
        config.set("Settings", "maxFileSize", str(variables.maxFileSize))
        config.set("Settings", "maxThreads", str(variables.maxThreads))
        config.set("Settings", "logLevel", variables.logLevel)
        config.set("Settings", "tempFolderPath", variables.tempFolderPath)
        config.set("Settings", "timeSlice", str(variables.timeSlice))
        with open(variables.configFilePath, "w") as f:
            config.write(f)

    logging.basicConfig(format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    variables.logger = logging.getLogger(__name__)
    variables.logger.setLevel(getattr(logging, variables.logLevel.upper()))

    variables.jobThread = threading.Thread(target=jobRunner)
    variables.jobThread.start()

#Connects with the instance of mongoDB based on the value given in the .env fie

def set_mongo_client():
    global client, db, collection
    load_dotenv()
    mongouri = os.getenv("MONGODB_URI")
    client = MongoClient(mongouri)
    db = client["YT"]
    collection = db["records"]

#Searches MongoDB for records

def find_record(hash):
    return collection.find_one({"YTHash": hash})

#Adds a new record to MongoDB

def add_record(hash,langs):
    record = YTRecord(YTHash=hash, langs=langs)
    collection.insert_one(record.dict(by_alias=True))

#Splits the downloaded wav file into chunks and analyzes them

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

#Downloads the youtube video in wav format, if the size is larger than variables.maxFileSize we 
#ignore the file and do not classify it

def download_file(url, hex_dig):
   global lock, count
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
       variables.logger.debug("Ignoring url "+str(json_util.dumps(record)))
       shutil.rmtree(path)
       while lock:
           pass
       lock = True
       count = count-1
       variables.logger.debug("Count decrement is "+str(count))
       lock = False
       return

   langs = split_wav(path+"track.wav", path)
   shutil.rmtree(path)
   variables.logger.info("YTB "+url+" "+str(langs))
   add_record(hex_dig,langs)
   while lock:
       pass
   lock = True
   count = count-1
   variables.logger.debug("Count decrement is "+str(count))
   lock = False

#Function to spawn threads to handle multiple jobs pushed in the jobURLList 

def jobRunner():
    global count
    while True:
            for job in variables.jobURLList:
                while count >= variables.maxThreads:
                    pass
                count = count+1
                variables.logger.debug("Count increment is "+str(count))
                variables.logger.debug("Processing job "+str(job))
                threading.Thread(target=download_file, args=(job["url"], job["hash"])).start()
                variables.jobURLList.remove(job)
