ipfs shutdown
ps -a | grep -e "uvicorn" -e "python3" -e "ffmpeg" | awk  '{print $1}' | xargs -I {} kill -9 {}
