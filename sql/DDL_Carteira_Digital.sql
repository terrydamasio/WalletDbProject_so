-- =========================================================
--  Script de criação da base, usuário,
--  Projeto: Carteira Digital
--  Banco:   MySQL 8+
-- =========================================================

-- =========================================================
-- MINI SPRINT 1 - INFRAESTRUTURA
-- =========================================================


-- 1) Criar base de dados
DROP DATABASE IF EXISTS wallet_homolog;
CREATE DATABASE wallet_homolog
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_0900_ai_ci;

-- 2) Criar usuário restrito para API
DROP USER IF EXISTS 'wallet_api_homolog'@'%';
CREATE USER 'wallet_api_homolog'@'%'
    IDENTIFIED BY 'api123';

-- 3) Conceder APENAS permissões DML (sem DDL)
GRANT SELECT, INSERT, UPDATE, DELETE
    ON wallet_homolog.*
    TO 'wallet_api_homolog'@'%';

FLUSH PRIVILEGES;

-- 4) Usar a base criada
USE wallet_homolog;

-- 5) Criar tabela CARTEIRA
CREATE TABLE carteira (
    endereco_carteira VARCHAR(100) PRIMARY KEY,
    hash_chave_privada VARCHAR(64) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('ATIVA', 'BLOQUEADA') DEFAULT 'ATIVA'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Verificar se tudo foi criado
SELECT 'Base e usuário criados com sucesso!' AS status;

-- =========================================================
-- MINI-SPRINT 2: TABELAS DE CARTEIRA, MOEDA E SALDO
-- =========================================================

-- Tabela MOEDA (moedas suportadas)
CREATE TABLE moeda (
    codigo_moeda VARCHAR(10) PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    tipo ENUM('CRYPTO', 'FIAT') NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabela SALDO_CARTEIRA (saldos por carteira e moeda)
CREATE TABLE saldo_carteira (
    id_saldo INT AUTO_INCREMENT PRIMARY KEY,
    endereco_carteira VARCHAR(100) NOT NULL,
    codigo_moeda VARCHAR(10) NOT NULL,
    saldo DECIMAL(20, 8) DEFAULT 0.00000000,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (endereco_carteira) REFERENCES carteira(endereco_carteira),
    FOREIGN KEY (codigo_moeda) REFERENCES moeda(codigo_moeda),
    
    UNIQUE KEY uk_carteira_moeda (endereco_carteira, codigo_moeda)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Índices para performance
CREATE INDEX idx_saldo_carteira ON saldo_carteira(endereco_carteira);
CREATE INDEX idx_saldo_moeda ON saldo_carteira(codigo_moeda);


-- =========================================================
-- MINI-SPRINT 3: TABELA DE DEPÓSITOS E SAQUES
-- =========================================================

CREATE TABLE deposito_saque (
    id_operacao INT AUTO_INCREMENT PRIMARY KEY,
    endereco_carteira VARCHAR(100) NOT NULL,
    codigo_moeda VARCHAR(10) NOT NULL,
    tipo_operacao ENUM('DEPOSITO', 'SAQUE') NOT NULL,
    valor DECIMAL(20, 8) NOT NULL,
    taxa DECIMAL(20, 8) DEFAULT 0.00000000,
    valor_liquido DECIMAL(20, 8) NOT NULL,
    saldo_anterior DECIMAL(20, 8) NOT NULL,
    saldo_posterior DECIMAL(20, 8) NOT NULL,
    data_operacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (endereco_carteira) REFERENCES carteira(endereco_carteira),
    FOREIGN KEY (codigo_moeda) REFERENCES moeda(codigo_moeda),
    
    INDEX idx_deposito_carteira (endereco_carteira),
    INDEX idx_deposito_data (data_operacao),
    INDEX idx_deposito_tipo (tipo_operacao)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Verificar criação
DESCRIBE deposito_saque;

-- =========================================================
-- MINI-SPRINT 4: TABELA DE CONVERSÕES
-- =========================================================

CREATE TABLE conversao (
    id_conversao INT AUTO_INCREMENT PRIMARY KEY,
    endereco_carteira VARCHAR(100) NOT NULL,
    moeda_origem VARCHAR(10) NOT NULL,
    moeda_destino VARCHAR(10) NOT NULL,
    valor_origem DECIMAL(20, 8) NOT NULL,
    cotacao DECIMAL(20, 8) NOT NULL,
    valor_convertido DECIMAL(20, 8) NOT NULL,
    taxa DECIMAL(20, 8) NOT NULL,
    valor_liquido DECIMAL(20, 8) NOT NULL,
    saldo_origem_anterior DECIMAL(20, 8) NOT NULL,
    saldo_origem_posterior DECIMAL(20, 8) NOT NULL,
    saldo_destino_anterior DECIMAL(20, 8) NOT NULL,
    saldo_destino_posterior DECIMAL(20, 8) NOT NULL,
    data_conversao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (endereco_carteira) REFERENCES carteira(endereco_carteira),
    FOREIGN KEY (moeda_origem) REFERENCES moeda(codigo_moeda),
    FOREIGN KEY (moeda_destino) REFERENCES moeda(codigo_moeda),
    
    INDEX idx_conversao_carteira (endereco_carteira),
    INDEX idx_conversao_data (data_conversao),
    INDEX idx_conversao_moedas (moeda_origem, moeda_destino)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Verificar criação
DESCRIBE conversao;


-- =========================================================
-- MINI-SPRINT 5: TABELA DE TRANSFERÊNCIAS
-- =========================================================

CREATE TABLE transferencia (
    id_transferencia INT AUTO_INCREMENT PRIMARY KEY,
    endereco_origem VARCHAR(100) NOT NULL,
    endereco_destino VARCHAR(100) NOT NULL,
    codigo_moeda VARCHAR(10) NOT NULL,
    valor DECIMAL(20, 8) NOT NULL,
    taxa DECIMAL(20, 8) NOT NULL,
    valor_liquido DECIMAL(20, 8) NOT NULL,
    saldo_origem_anterior DECIMAL(20, 8) NOT NULL,
    saldo_origem_posterior DECIMAL(20, 8) NOT NULL,
    saldo_destino_anterior DECIMAL(20, 8) NOT NULL,
    saldo_destino_posterior DECIMAL(20, 8) NOT NULL,
    data_transferencia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (endereco_origem) REFERENCES carteira(endereco_carteira),
    FOREIGN KEY (endereco_destino) REFERENCES carteira(endereco_carteira),
    FOREIGN KEY (codigo_moeda) REFERENCES moeda(codigo_moeda),
    
    INDEX idx_transferencia_origem (endereco_origem),
    INDEX idx_transferencia_destino (endereco_destino),
    INDEX idx_transferencia_data (data_transferencia),
    
    -- Garantir que origem e destino sejam diferentes
    CHECK (endereco_origem != endereco_destino)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Verificar criação
DESCRIBE transferencia;
