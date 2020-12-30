#!/bin/bash
pip3 install -r requirements.txt
sudo mkdir -p /usr/local/lib/e3dc2mqtt
sudo cp e3dc2mqtt.py /usr/local/lib/e3dc2mqtt/e3dc2mqtt.py
sudo chown ${USER}:${USER} /usr/local/lib/e3dc2mqtt/e3dc2mqtt.py
sed "s/##USER##/${USER}/" e3dc2mqtt.service > e3dc2mqtt_.service
sudo cp e3dc2mqtt_.service /etc/systemd/system/e3dc2mqtt.service
rm e3dc2mqtt_.service
sudo systemctl daemon-reload
sudo systemctl enable e3dc2mqtt
sudo systemctl start e3dc2mqtt
