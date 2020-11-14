#!/bin/bash          
sudo apt update && sudo apt upgrade 
echo "rodou" > /home/ubuntu/test.txt
sudo apt install postgresql postgresql-contrib -y
sudo su - postgres
psql -c "CREATE USER cloud WITH PASSWORD 'cloud';"
createdb -O cloud tasks
sed -i 's/'localhost'/'*'/g' /etc/postgresql/10/main/postgresql.conf
host all all 192.168.0.0/20 trust
exit
sudo ufw allow 5432/tcp
sudo systemctl restart postgresql
echo "postgres reseted" > /home/ubuntu/test.txt
