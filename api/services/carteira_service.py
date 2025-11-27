from typing import List
from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.models.carteira_models import Carteira, CarteiraCriada


class CarteiraService:
    """
    Lógica de negócio para operações de carteira.
    """

    def __init__(self):
        self.carteira_repo = CarteiraRepository()

    def criar_carteira(self) -> CarteiraCriada:
        """
        Cria uma nova carteira com saldos zerados em todas as moedas.
        
        Returns:
            CarteiraCriada: Dados da carteira incluindo chave privada
        """
        row = self.carteira_repo.criar()
        
        return CarteiraCriada(
            endereco_carteira=row["endereco_carteira"],
            data_criacao=row["data_criacao"],
            status=row["status"],
            chave_privada=row["chave_privada"]
        )

    def buscar_por_endereco(self, endereco_carteira: str) -> Carteira:
        """
        Busca uma carteira pelo endereço.
        
        Args:
            endereco_carteira: Endereço da carteira
        
        Returns:
            Carteira: Dados da carteira (sem chave privada)
        
        Raises:
            ValueError: Se carteira não existe
        """
        row = self.carteira_repo.buscar_por_endereco(endereco_carteira)
        if not row:
            raise ValueError(f"Carteira {endereco_carteira} não encontrada")

        return Carteira(
            endereco_carteira=row["endereco_carteira"],
            data_criacao=row["data_criacao"],
            status=row["status"]
        )

    def listar(self) -> List[Carteira]:
        """
        Lista todas as carteiras.
        
        Returns:
            List[Carteira]: Lista de carteiras
        """
        rows = self.carteira_repo.listar()
        
        return [
            Carteira(
                endereco_carteira=row["endereco_carteira"],
                data_criacao=row["data_criacao"],
                status=row["status"]
            )
            for row in rows
        ]

    def bloquear(self, endereco_carteira: str) -> Carteira:
        """
        Bloqueia uma carteira.
        
        Args:
            endereco_carteira: Endereço da carteira
        
        Returns:
            Carteira: Carteira bloqueada
        
        Raises:
            ValueError: Se carteira não existe
        """
        row = self.carteira_repo.atualizar_status(endereco_carteira, "BLOQUEADA")
        if not row:
            raise ValueError(f"Carteira {endereco_carteira} não encontrada")

        return Carteira(
            endereco_carteira=row["endereco_carteira"],
            data_criacao=row["data_criacao"],
            status=row["status"]
        )
