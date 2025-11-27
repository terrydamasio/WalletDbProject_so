# Projeto Carteira Digital
A carteira permite:

- Criar carteiras (com chave pública e chave privada)
- Ver saldos por moeda (BTC, ETH, SOL, USD)
- Fazer **depósitos**
- Fazer **saques** (com taxa e validação da chave privada)
- Fazer **conversão entre moedas** (usando cotação da Coinbase)
- Fazer **transferência entre carteiras**

---

## 1. Pré-requisitos

Antes de começar, você precisa ter instalado no seu computador:

- Python 3.10+
- MySQL 8+
- git (opcional)

Verifique as versões:

```bash
python --version
mysql --version
```

---

## 2. Clonar ou baixar o projeto

```bash
git clone https://github.com/terrydamasio/WalletDbProject
cd projeto_carteira_digital
```

Ou extraia o ZIP e abra o terminal dentro da pasta do projeto.

---

## 3. Criar e ativar o ambiente virtual (venv)

### Windows:
```bash
python -m venv venv
.env\Scripts\Activate
```

### Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 5. Criar o banco e usuário no MySQL

Execute o código SQL do diretório "/sql/DDL_Carteira_Digital.sql" no seu DB (Workbench):

Isso irá criar todas o banco de dados e todas as tabelas e colunas necessárias do projeto.

---

## 6. Iniciar o Servidor

```bash
uvicorn api.main:app --reload
```
```bash
docker compose up -d
```
```bash
 docker compose down 
```

Acesse:

👉 Documentação Swagger: http://127.0.0.1:8000/docs </br>
👉 Documentação ReDoc: http://127.0.0.1:8000/redoc</br>
👉 Health Check: http://127.0.0.1:8000/health</br>

---

## 7. Estrutura do projeto

```
projeto_carteira_digital/
│
├── api/
│   ├── main.py
│   ├── models/
│   ├── routers/
│   ├── services/
│   └── persistence/
│       │── repositories/
│       └── db.py
│
├── sql/DDL_Carteira_Digital.sql
├── requirements.txt
└── .env
```

---

## 9. Testes básicos

### Criar carteira:
POST /carteiras

### Ver saldo:
GET /carteiras/{endereco}/saldos

### Depósito:
POST /carteiras/{endereco}/depositos

### Saque:
POST /carteiras/{endereco}/saques

### Conversão:
POST /carteiras/{endereco}/conversoes

### Transferência:
POST /carteiras/{endereco_origem}/transferencias

---