import os
import wave
import math
import torchaudio
import shutil
import yt_dlp as youtube_dl
from speechbrain.pretrained import EncoderClassifier
language_id = EncoderClassifier.from_hparams(source="TalTechNLP/voxlingua107-epaca-tdnn", savedir="tmp")


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
        signal = language_id.load_audio(outFilename)
        prediction =  language_id.classify_batch(signal)
        langs.append(prediction[3][0])
    read.close()
    return list(set(langs))
    
def download_file(url,hex_dig):
   path="temp/"+hex_dig+"/"
   os.mkdir(path)
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
