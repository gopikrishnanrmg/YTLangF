ipfs_version=v0.26.0
source /etc/lsb-release
sudo apt install -y python3 python3-pip uvicorn ffmpeg gnupg curl jq lsof
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
   --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu $DISTRIB_CODENAME/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org
pip3 install -r requirements.txt
wget https://dist.ipfs.tech/kubo/${ipfs_version}/kubo_${ipfs_version}_linux-amd64.tar.gz
tar -xvzf kubo_${ipfs_version}_linux-amd64.tar.gz
cd kubo
sudo bash install.sh
ipfs init
ipfs bootstrap rm --all
ipfs config Routing.Type dht
ipfs config --json Experimental.Libp2pStreamMounting true
ipfs config --json Swarm.EnableHolePunching true
ipfs config --json Swarm.RelayClient.Enable true
echo "/key/swarm/psk/1.0.0/
/base16/
8828b3b593d8b7b37db860a70460bc2fa7539140f45d7ff855b30a6765c8c947" > ~/.ipfs/swarm.key
curl -X GET \
    -H 'Content-Type: application/json' \
    https://api.jsonsilo.com/public/6b1b0705-688d-4c5f-89a8-08b85c17c048 | jq -r .[] | while read bootstrap; do  ipfs bootstrap add $bootstrap; done  
rm -r ../kubo*