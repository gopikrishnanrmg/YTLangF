ps -a | grep -e "uvicorn" -e "python3" | awk  '{print $1}' | xargs -I {} kill -9 {}
