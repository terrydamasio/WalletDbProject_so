from typing import Dict, Any, List
from decimal import Decimal
from sqlalchemy import text
from api.persistence.db import get_connection


class TransferenciaRepository:
    """
    Responsável por todas as operações de banco relacionadas a Transferências.
    """

    def registrar_transferencia(
        self,
        endereco_origem: str,
        endereco_destino: str,
        codigo_moeda: str,
        valor: Decimal,
        taxa: Decimal,
        valor_liquido: Decimal,
        saldo_origem_anterior: Decimal,
        saldo_origem_posterior: Decimal,
        saldo_destino_anterior: Decimal,
        saldo_destino_posterior: Decimal
    ) -> Dict[str, Any]:
        """
        Registra uma transferência no histórico.
        
        Args:
            endereco_origem: Endereço da carteira que envia
            endereco_destino: Endereço da carteira que recebe
            codigo_moeda: Código da moeda transferida
            valor: Valor original da transferência
            taxa: Taxa cobrada da origem
            valor_liquido: Valor que o destino recebe (sem taxa)
            saldo_origem_anterior: Saldo da origem antes
            saldo_origem_posterior: Saldo da origem depois
            saldo_destino_anterior: Saldo do destino antes
            saldo_destino_posterior: Saldo do destino depois
        
        Returns:
            Dict: Dados da transferência registrada
        """
        with get_connection() as conn:
            # Inserir registro
            result = conn.execute(
                text("""
                    INSERT INTO transferencia (
                        endereco_origem,
                        endereco_destino,
                        codigo_moeda,
                        valor,
                        taxa,
                        valor_liquido,
                        saldo_origem_anterior,
                        saldo_origem_posterior,
                        saldo_destino_anterior,
                        saldo_destino_posterior
                    ) VALUES (
                        :endereco_origem,
                        :endereco_destino,
                        :codigo_moeda,
                        :valor,
                        :taxa,
                        :valor_liquido,
                        :saldo_origem_anterior,
                        :saldo_origem_posterior,
                        :saldo_destino_anterior,
                        :saldo_destino_posterior
                    )
                """),
                {
                    "endereco_origem": endereco_origem,
                    "endereco_destino": endereco_destino,
                    "codigo_moeda": codigo_moeda,
                    "valor": str(valor),
                    "taxa": str(taxa),
                    "valor_liquido": str(valor_liquido),
                    "saldo_origem_anterior": str(saldo_origem_anterior),
                    "saldo_origem_posterior": str(saldo_origem_posterior),
                    "saldo_destino_anterior": str(saldo_destino_anterior),
                    "saldo_destino_posterior": str(saldo_destino_posterior)
                }
            )

            id_transferencia = result.lastrowid

            # Buscar transferência criada
            row = conn.execute(
                text("""
                    SELECT 
                        id_transferencia,
                        endereco_origem,
                        endereco_destino,
                        codigo_moeda,
                        valor,
                        taxa,
                        valor_liquido,
                        saldo_origem_anterior,
                        saldo_origem_posterior,
                        saldo_destino_anterior,
                        saldo_destino_posterior,
                        data_transferencia
                    FROM transferencia
                    WHERE id_transferencia = :id
                """),
                {"id": id_transferencia}
            ).mappings().first()

        return dict(row)

    def listar_historico(
        self, 
        endereco_carteira: str,
        tipo: str = None
    ) -> List[Dict[str, Any]]:
        """
        Lista o histórico de transferências de uma carteira.
        
        Args:
            endereco_carteira: Endereço da carteira
            tipo: (Opcional) 'enviadas', 'recebidas' ou None para todas
        
        Returns:
            List[Dict]: Lista de transferências
        """
        with get_connection() as conn:
            if tipo == "enviadas":
                rows = conn.execute(
                    text("""
                        SELECT 
                            id_transferencia,
                            endereco_origem,
                            endereco_destino,
                            codigo_moeda,
                            valor,
                            taxa,
                            valor_liquido,
                            saldo_origem_anterior,
                            saldo_origem_posterior,
                            saldo_destino_anterior,
                            saldo_destino_posterior,
                            data_transferencia
                        FROM transferencia
                        WHERE endereco_origem = :endereco
                        ORDER BY data_transferencia DESC
                    """),
                    {"endereco": endereco_carteira}
                ).mappings().all()
            
            elif tipo == "recebidas":
                rows = conn.execute(
                    text("""
                        SELECT 
                            id_transferencia,
                            endereco_origem,
                            endereco_destino,
                            codigo_moeda,
                            valor,
                            taxa,
                            valor_liquido,
                            saldo_origem_anterior,
                            saldo_origem_posterior,
                            saldo_destino_anterior,
                            saldo_destino_posterior,
                            data_transferencia
                        FROM transferencia
                        WHERE endereco_destino = :endereco
                        ORDER BY data_transferencia DESC
                    """),
                    {"endereco": endereco_carteira}
                ).mappings().all()
            
            else:  # Todas (enviadas e recebidas)
                rows = conn.execute(
                    text("""
                        SELECT 
                            id_transferencia,
                            endereco_origem,
                            endereco_destino,
                            codigo_moeda,
                            valor,
                            taxa,
                            valor_liquido,
                            saldo_origem_anterior,
                            saldo_origem_posterior,
                            saldo_destino_anterior,
                            saldo_destino_posterior,
                            data_transferencia
                        FROM transferencia
                        WHERE endereco_origem = :endereco 
                           OR endereco_destino = :endereco
                        ORDER BY data_transferencia DESC
                    """),
                    {"endereco": endereco_carteira}
                ).mappings().all()

        return [dict(row) for row in rows]

    def buscar_por_id(self, id_transferencia: int) -> Dict[str, Any]:
        """
        Busca uma transferência específica por ID.
        
        Args:
            id_transferencia: ID da transferência
        
        Returns:
            Dict ou None
        """
        with get_connection() as conn:
            row = conn.execute(
                text("""
                    SELECT 
                        id_transferencia,
                        endereco_origem,
                        endereco_destino,
                        codigo_moeda,
                        valor,
                        taxa,
                        valor_liquido,
                        saldo_origem_anterior,
                        saldo_origem_posterior,
                        saldo_destino_anterior,
                        saldo_destino_posterior,
                        data_transferencia
                    FROM transferencia
                    WHERE id_transferencia = :id
                """),
                {"id": id_transferencia}
            ).mappings().first()

        return dict(row) if row else None
