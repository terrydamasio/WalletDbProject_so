-- Popular com as 5 moedas obrigatórias
INSERT INTO moeda (codigo_moeda, nome, tipo) VALUES
('BTC', 'Bitcoin', 'CRYPTO'),
('ETH', 'Ethereum', 'CRYPTO'),
('SOL', 'Solana', 'CRYPTO'),
('USD', 'Dólar Americano', 'FIAT'),
('BRL', 'Real Brasileiro', 'FIAT');

-- Verificar
SELECT * FROM moeda;