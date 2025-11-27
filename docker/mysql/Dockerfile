FROM mysql:8.0

ENV MYSQL_ROOT_PASSWORD=root
ENV MYSQL_DATABASE=wallet_homolog
ENV MYSQL_USER=wallet_user
ENV MYSQL_PASSWORD=wallet123

COPY init.sql /docker-entrypoint-initdb.d/
COPY DDL_Carteira_Digital.sql /docker-entrypoint-initdb.d/
COPY DML_Popular_Moedas.sql /docker-entrypoint-initdb.d/
