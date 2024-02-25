import os
import wave
import math
import torchaudio
import shutil
import configparser
import logging
import threading
import variables
import subprocess
import p2pSender
import p2pListener
import rsa
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
        variables.listenPort = int(config.get("Settings", "listenPort"))
        variables.sendPort = int(config.get("Settings", "sendPort"))
        variables.socketBufferSize = int(config.get("Settings", "socketBufferSize"))
        variables.waitTimeThreshold = int(config.get("Settings", "waitTimeThreshold"))
        variables.appname = config.get("Settings", "appname")

        with open(variables.keyPath+"public_key.pem", "rb") as public_key_file:
            public_key_pem = public_key_file.read()
        
        variables.publicKey = rsa.PublicKey.load_pkcs1(public_key_pem)

        with open(variables.keyPath+"private_key.pem", "rb") as private_key_file:
            private_key_pem = private_key_file.read()

        variables.privateKey = rsa.PrivateKey.load_pkcs1(private_key_pem)

    else:
        variables.maxFileSize = 1073741824
        variables.maxThreads = 2
        variables.logLevel = "debug"
        variables.tempFolderPath = "../temp/"
        variables.timeSlice = 100
        variables.listenPort = 8081
        variables.sendPort = 8082
        variables.socketBufferSize = 4096
        variables.waitTimeThreshold = 90
        variables.appname = "YTLangF"
        config.add_section("Settings")
        config.set("Settings", "maxFileSize", str(variables.maxFileSize))
        config.set("Settings", "maxThreads", str(variables.maxThreads))
        config.set("Settings", "maxFileSize", str(variables.maxFileSize))
        config.set("Settings", "maxThreads", str(variables.maxThreads))
        config.set("Settings", "logLevel", variables.logLevel)
        config.set("Settings", "tempFolderPath", variables.tempFolderPath)
        config.set("Settings", "timeSlice", str(variables.timeSlice))
        config.set("Settings", "listenPort", str(variables.listenPort))
        config.set("Settings", "sendPort", str(variables.sendPort))
        config.set("Settings", "socketBufferSize", str(variables.socketBufferSize))
        config.set("Settings", "waitTimeThreshold", str(variables.waitTimeThreshold))
        config.set("Settings", "appname", str(variables.appname))
        
        with open(variables.configFilePath, "w") as f:
            config.write(f)
            
        KEY_LENGTH = 2048
        variables.publicKey, variables.privateKey = rsa.newkeys(KEY_LENGTH)

        with open(variables.keyPath+"public_key.pem", "wb") as public_key_file:
            public_key_file.write(variables.publicKey.save_pkcs1())

        with open(variables.keyPath+"private_key.pem", "wb") as private_key_file:
            private_key_file.write(variables.privateKey.save_pkcs1())

    logging.basicConfig(format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    variables.logger = logging.getLogger(__name__)
    variables.logger.setLevel(getattr(logging, variables.logLevel.upper()))
    
    variables.jobThread = threading.Thread(target=jobRunner)
    variables.jobThread.start()

    variables.listenerThread = threading.Thread(target=p2pListener.serverListen)
    variables.listenerThread.start()

#Connects with the instance of mongoDB based on the value given in the .env fie

def set_mongo_client():
    global client, db, collection
    load_dotenv()
    mongouri = os.getenv("MONGODB_URI")
    client = MongoClient(mongouri)
    db = client["YT"]
    collection = db["records"]

#Fetch other nodes to connect to

def ipfsSwarmPeers():
    command = "ipfs swarm peers | awk -F'/' '{print $NF}'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    peer_ids = result.stdout.strip().split('\n')
    return peer_ids

#Connect to other nodes

def ipfsForward(peerID):
    command = "ipfs p2p forward /x/" + str(variables.appname) + "/1.0 /ip4/127.0.0.1/tcp/" + str(variables.sendPort) + " /p2p/" + str(peerID)
    subprocess.run(command, shell=True)

#Start service for other nodes to connect to

def ipfsListen():
    command = "ipfs p2p listen /x/" + str(variables.appname) + "/1.0 /ip4/127.0.0.1/tcp/" + str(variables.listenPort)
    subprocess.run(command, shell=True)

#Close an existing forward connection

def ipfsP2PClose(peerID):
    command = "ipfs p2p close -t /ipfs/" + str(peerID)
    subprocess.run(command, shell=True)

#Close an existing listen connection

def closeIpfsListen():
    command = "ipfs p2p close /x/" + str(variables.appname) + "/1.0 /ip4/127.0.0.1/tcp/" + str(variables.listenPort)
    subprocess.run(command, shell=True)

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
       return

   langs = split_wav(path+"track.wav", path)
   shutil.rmtree(path)
   variables.logger.info("YTB "+url+" "+str(langs))
   add_record(hex_dig,langs)

#Function that process the individual jobs

def jobHandler(url, hex_dig):
    global lock, count
    if p2pSender.clientSend(hex_dig):
        download_file(url, hex_dig)
    
    while lock:
        pass
    lock = True
    count = count-1
    variables.logger.debug("Count decrement is "+str(count))
    lock = False

#Function to spawn threads to handle multiple jobs pushed in the jobURLList 

def jobRunner():
    global count
    while (True):
            for job in variables.jobURLList:
                while(count >= variables.maxThreads):
                    pass
                count = count+1
                variables.logger.debug("Count increment is "+str(count))
                variables.logger.debug("Processing job "+str(job))
                threading.Thread(target=jobHandler, args=(job["url"], job["hash"])).start()
                variables.jobURLList.remove(job)
