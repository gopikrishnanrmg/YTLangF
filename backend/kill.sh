ipfs shutdown
ps -a | grep -e "uvicorn" -e "python3" -e "python" -e "ffmpeg" | awk  '{print $1}' | xargs -I {} kill -9 {}
