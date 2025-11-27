from typing import List, Dict, Any, Optional
from sqlalchemy import text
from api.persistence.db import get_connection


class MoedaRepository:
    """
    Responsável por todas as operações de banco relacionadas a Moedas.
    """

    def listar_todas(self) -> List[Dict[str, Any]]:
        """
        Lista todas as moedas ativas do sistema.
        
        Returns:
            List[Dict]: Lista de moedas
        """
        with get_connection() as conn:
            rows = conn.execute(
                text("""
                    SELECT codigo_moeda, nome, tipo, ativo, data_cadastro
                    FROM moeda
                    WHERE ativo = TRUE
                    ORDER BY tipo, codigo_moeda
                """)
            ).mappings().all()

        return [dict(row) for row in rows]

    def buscar_por_codigo(self, codigo_moeda: str) -> Optional[Dict[str, Any]]:
        """
        Busca uma moeda específica pelo código.
        
        Args:
            codigo_moeda: Código da moeda (ex: BTC, USD)
        
        Returns:
            Dict ou None
        """
        with get_connection() as conn:
            row = conn.execute(
                text("""
                    SELECT codigo_moeda, nome, tipo, ativo, data_cadastro
                    FROM moeda
                    WHERE codigo_moeda = :codigo AND ativo = TRUE
                """),
                {"codigo": codigo_moeda}
            ).mappings().first()

        return dict(row) if row else None

    def existe(self, codigo_moeda: str) -> bool:
        """
        Verifica se uma moeda existe e está ativa.
        
        Args:
            codigo_moeda: Código da moeda
        
        Returns:
            bool: True se existe e está ativa
        """
        with get_connection() as conn:
            count = conn.execute(
                text("""
                    SELECT COUNT(*) as total
                    FROM moeda
                    WHERE codigo_moeda = :codigo AND ativo = TRUE
                """),
                {"codigo": codigo_moeda}
            ).scalar()

        return count > 0
