from typing import List, Dict, Any, Optional
from decimal import Decimal
from sqlalchemy import text
from api.persistence.db import get_connection


class SaldoRepository:
    """
    Responsável por todas as operações de banco relacionadas a Saldos.
    """

    def buscar_saldos_carteira(self, endereco_carteira: str) -> List[Dict[str, Any]]:
        """
        Busca todos os saldos de uma carteira com informações das moedas.
        
        Args:
            endereco_carteira: Endereço da carteira
        
        Returns:
            List[Dict]: Lista de saldos com dados da moeda
        """
        with get_connection() as conn:
            rows = conn.execute(
                text("""
                    SELECT 
                        s.codigo_moeda,
                        m.nome as nome_moeda,
                        s.saldo,
                        s.data_atualizacao
                    FROM saldo_carteira s
                    INNER JOIN moeda m ON s.codigo_moeda = m.codigo_moeda
                    WHERE s.endereco_carteira = :endereco
                    ORDER BY m.tipo, s.codigo_moeda
                """),
                {"endereco": endereco_carteira}
            ).mappings().all()

        return [dict(row) for row in rows]

    def buscar_saldo_especifico(
        self, 
        endereco_carteira: str, 
        codigo_moeda: str
    ) -> Optional[Decimal]:
        """
        Busca o saldo de uma carteira em uma moeda específica.
        
        Args:
            endereco_carteira: Endereço da carteira
            codigo_moeda: Código da moeda
        
        Returns:
            Decimal ou None: Saldo ou None se não existir
        """
        with get_connection() as conn:
            saldo = conn.execute(
                text("""
                    SELECT saldo
                    FROM saldo_carteira
                    WHERE endereco_carteira = :endereco
                      AND codigo_moeda = :moeda
                """),
                {"endereco": endereco_carteira, "moeda": codigo_moeda}
            ).scalar()

        return Decimal(str(saldo)) if saldo is not None else None

    def criar_saldo_inicial(
        self, 
        endereco_carteira: str, 
        codigo_moeda: str
    ) -> None:
        """
        Cria um registro de saldo zerado para uma carteira em uma moeda.
        
        Args:
            endereco_carteira: Endereço da carteira
            codigo_moeda: Código da moeda
        """
        with get_connection() as conn:
            conn.execute(
                text("""
                    INSERT INTO saldo_carteira (endereco_carteira, codigo_moeda, saldo)
                    VALUES (:endereco, :moeda, 0.00000000)
                    ON DUPLICATE KEY UPDATE saldo = saldo
                """),
                {"endereco": endereco_carteira, "moeda": codigo_moeda}
            )

    def atualizar_saldo(
        self, 
        endereco_carteira: str, 
        codigo_moeda: str, 
        novo_saldo: Decimal
    ) -> None:
        """
        Atualiza o saldo de uma carteira em uma moeda.
        
        Args:
            endereco_carteira: Endereço da carteira
            codigo_moeda: Código da moeda
            novo_saldo: Novo valor do saldo
        """
        with get_connection() as conn:
            conn.execute(
                text("""
                    UPDATE saldo_carteira
                    SET saldo = :saldo
                    WHERE endereco_carteira = :endereco
                      AND codigo_moeda = :moeda
                """),
                {
                    "saldo": str(novo_saldo),
                    "endereco": endereco_carteira,
                    "moeda": codigo_moeda
                }
            )
    
    def inicializar_saldos_carteira(self, endereco_carteira: str) -> None:
        """
        Cria registros zerados de saldo para todas as moedas ativas.
        Chamado automaticamente ao criar uma nova carteira.
        
        Args:
            endereco_carteira: Endereço da carteira
        """
        with get_connection() as conn:
            conn.execute(
                text("""
                    INSERT INTO saldo_carteira (endereco_carteira, codigo_moeda, saldo)
                    SELECT :endereco, codigo_moeda, 0.00000000
                    FROM moeda
                    WHERE ativo = TRUE
                """),
                {"endereco": endereco_carteira}
            )
