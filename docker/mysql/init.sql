-- Cria a database
CREATE DATABASE IF NOT EXISTS wallet_homolog;

USE wallet_homolog;

-- Executa seus scripts existentes
SOURCE /docker-entrypoint-initdb.d/DDL_Carteira_Digital.sql;
SOURCE /docker-entrypoint-initdb.d/DML_Popular_Moedas.sql;

-- Cria usuário
CREATE USER IF NOT EXISTS 'wallet_user'@'%' IDENTIFIED BY 'wallet123';
GRANT ALL PRIVILEGES ON wallet_homolog.* TO 'wallet_user'@'%';

FLUSH PRIVILEGES;
