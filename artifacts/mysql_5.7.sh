#!/bin/bash
# Start mysql server
docker run --rm \
  --platform linux/amd64 \
  --name chatbot_mysql \
  -e MYSQL_ROOT_PASSWORD=password \
  -p 3306:3306 \
  mysql/mysql-server:5.7 

# create and grant permission to chatbot user
CREATE USER 'chatbot'@'%' IDENTIFIED BY 'P@ss99W0rd';
GRANT USAGE ON *.* TO `chatbot`@`%`;
GRANT SELECT, INSERT, INDEX, UPDATE, DELETE, ALTER, CREATE ON *.* TO `chatbot`@`%`;


# access mysql server using chatbot user
mysql -uchatbot -h127.0.0.1 -ppassword