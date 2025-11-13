
sudo apt update

# install PostgreSQL
sudo apt install postgresql postgresql-contrib
sudo systemctl status postgresql

sudo apt  install docker-compose 

sudo docker-compose -f compose.yaml up --build -d

# stop local pgsql
sudo systemctl stop postgresql