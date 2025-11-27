from typing import Dict, Any, List
from decimal import Decimal
from sqlalchemy import text
from api.persistence.db import get_connection


class DepositoSaqueRepository:
    """
    Responsável por todas as operações de banco relacionadas a Depósitos e Saques.
    """

    def registrar_deposito(
        self,
        endereco_carteira: str,
        codigo_moeda: str,
        valor: Decimal,
        saldo_anterior: Decimal,
        saldo_posterior: Decimal
    ) -> Dict[str, Any]:
        """
        Registra um depósito no histórico.
        
        Args:
            endereco_carteira: Endereço da carteira
            codigo_moeda: Código da moeda
            valor: Valor depositado
            saldo_anterior: Saldo antes do depósito
            saldo_posterior: Saldo depois do depósito
        
        Returns:
            Dict: Dados da operação registrada
        """
        with get_connection() as conn:
            # Inserir registro
            result = conn.execute(
                text("""
                    INSERT INTO deposito_saque (
                        endereco_carteira,
                        codigo_moeda,
                        tipo_operacao,
                        valor,
                        taxa,
                        valor_liquido,
                        saldo_anterior,
                        saldo_posterior
                    ) VALUES (
                        :endereco,
                        :moeda,
                        'DEPOSITO',
                        :valor,
                        0.00000000,
                        :valor,
                        :saldo_anterior,
                        :saldo_posterior
                    )
                """),
                {
                    "endereco": endereco_carteira,
                    "moeda": codigo_moeda,
                    "valor": str(valor),
                    "saldo_anterior": str(saldo_anterior),
                    "saldo_posterior": str(saldo_posterior)
                }
            )

            id_operacao = result.lastrowid

            # Buscar operação criada
            row = conn.execute(
                text("""
                    SELECT 
                        id_operacao,
                        endereco_carteira,
                        codigo_moeda,
                        tipo_operacao,
                        valor,
                        taxa,
                        valor_liquido,
                        saldo_anterior,
                        saldo_posterior,
                        data_operacao
                    FROM deposito_saque
                    WHERE id_operacao = :id
                """),
                {"id": id_operacao}
            ).mappings().first()

        return dict(row)

    def registrar_saque(
        self,
        endereco_carteira: str,
        codigo_moeda: str,
        valor: Decimal,
        taxa: Decimal,
        valor_liquido: Decimal,
        saldo_anterior: Decimal,
        saldo_posterior: Decimal
    ) -> Dict[str, Any]:
        """
        Registra um saque no histórico.
        
        Args:
            endereco_carteira: Endereço da carteira
            codigo_moeda: Código da moeda
            valor: Valor do saque (antes da taxa)
            taxa: Taxa cobrada
            valor_liquido: Valor final debitado (valor + taxa)
            saldo_anterior: Saldo antes do saque
            saldo_posterior: Saldo depois do saque
        
        Returns:
            Dict: Dados da operação registrada
        """
        with get_connection() as conn:
            # Inserir registro
            result = conn.execute(
                text("""
                    INSERT INTO deposito_saque (
                        endereco_carteira,
                        codigo_moeda,
                        tipo_operacao,
                        valor,
                        taxa,
                        valor_liquido,
                        saldo_anterior,
                        saldo_posterior
                    ) VALUES (
                        :endereco,
                        :moeda,
                        'SAQUE',
                        :valor,
                        :taxa,
                        :valor_liquido,
                        :saldo_anterior,
                        :saldo_posterior
                    )
                """),
                {
                    "endereco": endereco_carteira,
                    "moeda": codigo_moeda,
                    "valor": str(valor),
                    "taxa": str(taxa),
                    "valor_liquido": str(valor_liquido),
                    "saldo_anterior": str(saldo_anterior),
                    "saldo_posterior": str(saldo_posterior)
                }
            )

            id_operacao = result.lastrowid

            # Buscar operação criada
            row = conn.execute(
                text("""
                    SELECT 
                        id_operacao,
                        endereco_carteira,
                        codigo_moeda,
                        tipo_operacao,
                        valor,
                        taxa,
                        valor_liquido,
                        saldo_anterior,
                        saldo_posterior,
                        data_operacao
                    FROM deposito_saque
                    WHERE id_operacao = :id
                """),
                {"id": id_operacao}
            ).mappings().first()

        return dict(row)

    def listar_historico(
        self, 
        endereco_carteira: str,
        codigo_moeda: str = None
    ) -> List[Dict[str, Any]]:
        """
        Lista o histórico de depósitos e saques de uma carteira.
        
        Args:
            endereco_carteira: Endereço da carteira
            codigo_moeda: (Opcional) Filtrar por moeda específica
        
        Returns:
            List[Dict]: Lista de operações
        """
        with get_connection() as conn:
            if codigo_moeda:
                rows = conn.execute(
                    text("""
                        SELECT 
                            id_operacao,
                            endereco_carteira,
                            codigo_moeda,
                            tipo_operacao,
                            valor,
                            taxa,
                            valor_liquido,
                            saldo_anterior,
                            saldo_posterior,
                            data_operacao
                        FROM deposito_saque
                        WHERE endereco_carteira = :endereco
                          AND codigo_moeda = :moeda
                        ORDER BY data_operacao DESC
                    """),
                    {"endereco": endereco_carteira, "moeda": codigo_moeda}
                ).mappings().all()
            else:
                rows = conn.execute(
                    text("""
                        SELECT 
                            id_operacao,
                            endereco_carteira,
                            codigo_moeda,
                            tipo_operacao,
                            valor,
                            taxa,
                            valor_liquido,
                            saldo_anterior,
                            saldo_posterior,
                            data_operacao
                        FROM deposito_saque
                        WHERE endereco_carteira = :endereco
                        ORDER BY data_operacao DESC
                    """),
                    {"endereco": endereco_carteira}
                ).mappings().all()

        return [dict(row) for row in rows]
