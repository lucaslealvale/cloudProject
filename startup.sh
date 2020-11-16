#!/bin/bash          
sudo apt update && sudo apt upgrade -y
echo "rodou isto e apenas um teste" > /home/ubuntu/test.txt
sudo apt install postgresql postgresql-contrib -y
sudo su - postgres -c "psql -c \"CREATE USER cloud  WITH PASSWORD 'cloud' \""
sudo -u postgres psql -c 'create database tasks;'
sudo sed -i 's/#listen_/listen_/g' /etc/postgresql/10/main/postgresql.conf
sudo sed -i 's/localhost/*/g' /etc/postgresql/10/main/postgresql.conf
sudo sed -i -e '$ahost    all             all             0.0.0.0/0          trust' /etc/postgresql/10/main/pg_hba.conf
sudo ufw allow 5432/tcp
sudo systemctl restart postgresql



