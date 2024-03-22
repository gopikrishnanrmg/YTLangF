ipfs_version=v0.26.0
wget https://dist.ipfs.tech/kubo/${ipfs_version}/kubo_${ipfs_version}_linux-amd64.tar.gz
tar -xvzf kubo_${ipfs_version}_linux-amd64.tar.gz
cd kubo
sudo bash install.sh
ipfs init
ipfs bootstrap rm --all
ipfs config Routing.Type dhtserver
ipfs config --json Experimental.Libp2pStreamMounting true
ipfs config --json Swarm.EnableHolePunching true
ipfs config --json Swarm.RelayService.Enable true
echo "/key/swarm/psk/1.0.0/
/base16/
8828b3b593d8b7b37db860a70460bc2fa7539140f45d7ff855b30a6765c8c947" > ~/.ipfs/swarm.key
curl -X GET \
    -H 'Content-Type: application/json' \
    https://api.jsonsilo.com/public/6b1b0705-688d-4c5f-89a8-08b85c17c048 | jq -r .[] | while read bootstrap; do  ipfs bootstrap add $bootstrap; done  
rm -r ../kubo*