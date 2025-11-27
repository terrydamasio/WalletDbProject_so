import os
import secrets
import hashlib
from typing import Dict, Any, Optional, List
from sqlalchemy import text
from api.persistence.db import get_connection


class CarteiraRepository:
    """
    Responsável por todas as operações de banco relacionadas a Carteiras.
    """

    def criar(self) -> Dict[str, Any]:
        """
        Gera chaves, cria carteira e retorna dados incluindo chave privada.
        
        Returns:
            Dict: Dados da carteira criada + chave privada
        """
        # 1) Gerar chaves
        private_key_size = int(os.getenv("PRIVATE_KEY_SIZE", "32"))
        public_key_size = int(os.getenv("PUBLIC_KEY_SIZE", "16"))
        
        chave_privada = secrets.token_hex(private_key_size)
        endereco = secrets.token_hex(public_key_size)
        hash_privada = hashlib.sha256(chave_privada.encode()).hexdigest()

        with get_connection() as conn:
            # 2) Inserir carteira
            conn.execute(
                text("""
                    INSERT INTO carteira (endereco_carteira, hash_chave_privada)
                    VALUES (:endereco, :hash_privada)
                """),
                {"endereco": endereco, "hash_privada": hash_privada}
            )

            # 3) Inicializar saldos zerados para todas as moedas
            conn.execute(
                text("""
                    INSERT INTO saldo_carteira (endereco_carteira, codigo_moeda, saldo)
                    SELECT :endereco, codigo_moeda, 0.00000000
                    FROM moeda
                    WHERE ativo = TRUE
                """),
                {"endereco": endereco}
            )

            # 4) Buscar carteira criada
            row = conn.execute(
                text("""
                    SELECT endereco_carteira, data_criacao, status, hash_chave_privada
                    FROM carteira
                    WHERE endereco_carteira = :endereco
                """),
                {"endereco": endereco}
            ).mappings().first()

        carteira = dict(row)
        carteira["chave_privada"] = chave_privada  # Apenas retornada aqui!
        return carteira

    def buscar_por_endereco(self, endereco_carteira: str) -> Optional[Dict[str, Any]]:
        """
        Busca uma carteira pelo endereço.
        
        Args:
            endereco_carteira: Endereço da carteira
        
        Returns:
            Dict ou None
        """
        with get_connection() as conn:
            row = conn.execute(
                text("""
                    SELECT endereco_carteira, data_criacao, status, hash_chave_privada
                    FROM carteira
                    WHERE endereco_carteira = :endereco
                """),
                {"endereco": endereco_carteira}
            ).mappings().first()

        return dict(row) if row else None

    def validar_chave_privada(self, endereco_carteira: str, chave_privada: str) -> bool:
        """
        Valida se a chave privada fornecida corresponde ao hash armazenado.
        
        Args:
            endereco_carteira: Endereço da carteira
            chave_privada: Chave privada a validar
        
        Returns:
            bool: True se a chave está correta
        """
        hash_fornecido = hashlib.sha256(chave_privada.encode()).hexdigest()
        
        with get_connection() as conn:
            hash_banco = conn.execute(
                text("""
                    SELECT hash_chave_privada
                    FROM carteira
                    WHERE endereco_carteira = :endereco
                """),
                {"endereco": endereco_carteira}
            ).scalar()

        return hash_banco == hash_fornecido if hash_banco else False

    def listar(self) -> List[Dict[str, Any]]:
        """
        Lista todas as carteiras.
        
        Returns:
            List[Dict]: Lista de carteiras
        """
        with get_connection() as conn:
            rows = conn.execute(
                text("""
                    SELECT endereco_carteira, data_criacao, status
                    FROM carteira
                    ORDER BY data_criacao DESC
                """)
            ).mappings().all()

        return [dict(row) for row in rows]

    def atualizar_status(
        self, 
        endereco_carteira: str, 
        status: str
    ) -> Optional[Dict[str, Any]]:
        """
        Atualiza o status de uma carteira.
        
        Args:
            endereco_carteira: Endereço da carteira
            status: Novo status (ATIVA ou BLOQUEADA)
        
        Returns:
            Dict ou None: Carteira atualizada
        """
        with get_connection() as conn:
            conn.execute(
                text("""
                    UPDATE carteira
                    SET status = :status
                    WHERE endereco_carteira = :endereco
                """),
                {"status": status, "endereco": endereco_carteira}
            )

            row = conn.execute(
                text("""
                    SELECT endereco_carteira, data_criacao, status
                    FROM carteira
                    WHERE endereco_carteira = :endereco
                """),
                {"endereco": endereco_carteira}
            ).mappings().first()

        return dict(row) if row else None
