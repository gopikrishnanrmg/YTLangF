ipfs shutdown
sudo systemctl start mongod
ipfs daemon &
while true; 
    do 
        if  lsof -i:8080 | grep ipfs; then
            break
        fi
    done
cd src && uvicorn main:app --reload
