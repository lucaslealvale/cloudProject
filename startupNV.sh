#!/bin/bash 
echo "welcome to the jungle" > /home/ubuntu/welcometothe.txt


sudo apt update && sudo apt upgrade -y
cd /home/ubuntu
sudo git clone https://github.com/raulikeda/tasks.git
echo "jungle" > /home/ubuntu/jungle.txt

sudo sed -i 's/node1/3.17.172.129/g' /home/ubuntu/tasks/portfolio/settings.py
cd tasks/
./install.sh
echo "welcome " > /home/ubuntu/welcome.txt

