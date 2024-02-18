ipfs_version=v0.26.0
apt install python3 python3-pip uvicorn ffmpeg
pip3 install -r requirements.txt
wget https://dist.ipfs.tech/kubo/${ipfs_version}/kubo_${ipfs_version}_linux-amd64.tar.gz
tar -xvzf kubo_${ipfs_version}_linux-amd64.tar.gz
cd kubo
bash install.sh
ipfs init
ipfs config Routing.Type dht
ipfs config --json Experimental.Libp2pStreamMounting true
echo "/key/swarm/psk/1.0.0/
/base16/
8828b3b593d8b7b37db860a70460bc2fa7539140f45d7ff855b30a6765c8c947" > ~/.ipfs/swarm.key 
rm -r ../kubo*