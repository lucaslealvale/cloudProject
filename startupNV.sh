#!/bin/bash          
echo "rodou isto e apenas um tdddddddddddddddddestdddddde" > /home/ubuntu/hokage.txt

sudo apt update && sudo apt upgrade -y
sleep 250
cd /home/ubuntu
sudo git clone https://github.com/raulikeda/tasks.git
sudo sed -i 's/node1/18.218.161.121/g' /home/ubuntu/tasks/portfolio/settings.py
cd tasks/
./install.sh
echo "rodou isto e apenas um tdddddddddddddddddeste" > /home/ubuntu/test.txt



