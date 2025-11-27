from typing import Dict, Any, List
from decimal import Decimal
from sqlalchemy import text
from api.persistence.db import get_connection


class ConversaoRepository:
    """
    Responsável por todas as operações de banco relacionadas a Conversões.
    """

    def registrar_conversao(
        self,
        endereco_carteira: str,
        moeda_origem: str,
        moeda_destino: str,
        valor_origem: Decimal,
        cotacao: Decimal,
        valor_convertido: Decimal,
        taxa: Decimal,
        valor_liquido: Decimal,
        saldo_origem_anterior: Decimal,
        saldo_origem_posterior: Decimal,
        saldo_destino_anterior: Decimal,
        saldo_destino_posterior: Decimal
    ) -> Dict[str, Any]:
        """
        Registra uma conversão no histórico.
        
        Args:
            endereco_carteira: Endereço da carteira
            moeda_origem: Código da moeda de origem
            moeda_destino: Código da moeda de destino
            valor_origem: Valor original a converter
            cotacao: Taxa de câmbio utilizada
            valor_convertido: Valor resultante (antes da taxa)
            taxa: Taxa cobrada pela conversão
            valor_liquido: Valor final creditado (após taxa)
            saldo_origem_anterior: Saldo da moeda origem antes
            saldo_origem_posterior: Saldo da moeda origem depois
            saldo_destino_anterior: Saldo da moeda destino antes
            saldo_destino_posterior: Saldo da moeda destino depois
        
        Returns:
            Dict: Dados da conversão registrada
        """
        with get_connection() as conn:
            # Inserir registro
            result = conn.execute(
                text("""
                    INSERT INTO conversao (
                        endereco_carteira,
                        moeda_origem,
                        moeda_destino,
                        valor_origem,
                        cotacao,
                        valor_convertido,
                        taxa,
                        valor_liquido,
                        saldo_origem_anterior,
                        saldo_origem_posterior,
                        saldo_destino_anterior,
                        saldo_destino_posterior
                    ) VALUES (
                        :endereco,
                        :moeda_origem,
                        :moeda_destino,
                        :valor_origem,
                        :cotacao,
                        :valor_convertido,
                        :taxa,
                        :valor_liquido,
                        :saldo_origem_anterior,
                        :saldo_origem_posterior,
                        :saldo_destino_anterior,
                        :saldo_destino_posterior
                    )
                """),
                {
                    "endereco": endereco_carteira,
                    "moeda_origem": moeda_origem,
                    "moeda_destino": moeda_destino,
                    "valor_origem": str(valor_origem),
                    "cotacao": str(cotacao),
                    "valor_convertido": str(valor_convertido),
                    "taxa": str(taxa),
                    "valor_liquido": str(valor_liquido),
                    "saldo_origem_anterior": str(saldo_origem_anterior),
                    "saldo_origem_posterior": str(saldo_origem_posterior),
                    "saldo_destino_anterior": str(saldo_destino_anterior),
                    "saldo_destino_posterior": str(saldo_destino_posterior)
                }
            )

            id_conversao = result.lastrowid

            # Buscar conversão criada
            row = conn.execute(
                text("""
                    SELECT 
                        id_conversao,
                        endereco_carteira,
                        moeda_origem,
                        moeda_destino,
                        valor_origem,
                        cotacao,
                        valor_convertido,
                        taxa,
                        valor_liquido,
                        saldo_origem_anterior,
                        saldo_origem_posterior,
                        saldo_destino_anterior,
                        saldo_destino_posterior,
                        data_conversao
                    FROM conversao
                    WHERE id_conversao = :id
                """),
                {"id": id_conversao}
            ).mappings().first()

        return dict(row)

    def listar_historico(
        self, 
        endereco_carteira: str,
        moeda: str = None
    ) -> List[Dict[str, Any]]:
        """
        Lista o histórico de conversões de uma carteira.
        
        Args:
            endereco_carteira: Endereço da carteira
            moeda: (Opcional) Filtrar por moeda de origem ou destino
        
        Returns:
            List[Dict]: Lista de conversões
        """
        with get_connection() as conn:
            if moeda:
                rows = conn.execute(
                    text("""
                        SELECT 
                            id_conversao,
                            endereco_carteira,
                            moeda_origem,
                            moeda_destino,
                            valor_origem,
                            cotacao,
                            valor_convertido,
                            taxa,
                            valor_liquido,
                            saldo_origem_anterior,
                            saldo_origem_posterior,
                            saldo_destino_anterior,
                            saldo_destino_posterior,
                            data_conversao
                        FROM conversao
                        WHERE endereco_carteira = :endereco
                          AND (moeda_origem = :moeda OR moeda_destino = :moeda)
                        ORDER BY data_conversao DESC
                    """),
                    {"endereco": endereco_carteira, "moeda": moeda}
                ).mappings().all()
            else:
                rows = conn.execute(
                    text("""
                        SELECT 
                            id_conversao,
                            endereco_carteira,
                            moeda_origem,
                            moeda_destino,
                            valor_origem,
                            cotacao,
                            valor_convertido,
                            taxa,
                            valor_liquido,
                            saldo_origem_anterior,
                            saldo_origem_posterior,
                            saldo_destino_anterior,
                            saldo_destino_posterior,
                            data_conversao
                        FROM conversao
                        WHERE endereco_carteira = :endereco
                        ORDER BY data_conversao DESC
                    """),
                    {"endereco": endereco_carteira}
                ).mappings().all()

        return [dict(row) for row in rows]

    def buscar_por_id(self, id_conversao: int) -> Dict[str, Any]:
        """
        Busca uma conversão específica por ID.
        
        Args:
            id_conversao: ID da conversão
        
        Returns:
            Dict ou None
        """
        with get_connection() as conn:
            row = conn.execute(
                text("""
                    SELECT 
                        id_conversao,
                        endereco_carteira,
                        moeda_origem,
                        moeda_destino,
                        valor_origem,
                        cotacao,
                        valor_convertido,
                        taxa,
                        valor_liquido,
                        saldo_origem_anterior,
                        saldo_origem_posterior,
                        saldo_destino_anterior,
                        saldo_destino_posterior,
                        data_conversao
                    FROM conversao
                    WHERE id_conversao = :id
                """),
                {"id": id_conversao}
            ).mappings().first()

        return dict(row) if row else None
