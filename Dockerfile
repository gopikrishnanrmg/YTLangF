FROM ubuntu:latest
WORKDIR /home/
COPY backend ./
RUN apt update && apt install -y python3 python3-pip wget net-tools nano
RUN chmod +x install.sh
RUN ./install.sh


