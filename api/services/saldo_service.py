from typing import List
from api.persistence.repositories.saldo_repository import SaldoRepository
from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.models.saldo_models import SaldoCarteira, ListaSaldos


class SaldoService:
    """
    Lógica de negócio para consulta de saldos.
    """

    def __init__(self):
        self.saldo_repo = SaldoRepository()
        self.carteira_repo = CarteiraRepository()

    def listar_saldos(self, endereco_carteira: str) -> ListaSaldos:
        """
        Lista todos os saldos de uma carteira.
        
        Args:
            endereco_carteira: Endereço da carteira
        
        Returns:
            ListaSaldos: Saldos da carteira
        
        Raises:
            ValueError: Se carteira não existe
        """
        # Validar se carteira existe
        carteira = self.carteira_repo.buscar_por_endereco(endereco_carteira)
        if not carteira:
            raise ValueError(f"Carteira {endereco_carteira} não encontrada")

        # Buscar saldos
        rows = self.saldo_repo.buscar_saldos_carteira(endereco_carteira)

        saldos = [
            SaldoCarteira(
                codigo_moeda=row["codigo_moeda"],
                nome_moeda=row["nome_moeda"],
                saldo=row["saldo"],
                data_atualizacao=row["data_atualizacao"]
            )
            for row in rows
        ]

        return ListaSaldos(
            endereco_carteira=endereco_carteira,
            saldos=saldos,
            total_moedas=len(saldos)
        )
