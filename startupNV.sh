#!/bin/bash          
echo "rodou isto e apenas um tdddddddddddddddddestdddddde" > /home/ubuntu/hokage.txt

sudo apt update && sudo apt upgrade -y
sleep 180
sudo git clone https://github.com/raulikeda/tasks.git
sudo sed -i 's/node1/ec2-54-175-243-41.compute-1.amazonaws.com/g' /home/ubuntu/tasks/portfolio/settings.py
cd tasks/
./install.sh
echo "rodou isto e apenas um tdddddddddddddddddeste" > /home/ubuntu/test.txt
