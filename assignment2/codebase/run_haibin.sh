
sudo apt update

# install PostgreSQL
sudo apt install postgresql postgresql-contrib
sudo systemctl status postgresql

sudo apt  install docker-compose 

# sudo docker-compose -f compose.yaml up --build -d

# stop local pgsql
sudo systemctl stop postgresql


docker-compose down && docker-compose up --build -d

# docker exec -it kafka kafka-console-consumer     --bootstrap-server localhost:9092     --topic api-logs     --from-beginning