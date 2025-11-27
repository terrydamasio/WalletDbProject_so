import os
from decimal import Decimal
from typing import List

from api.persistence.repositories.deposito_saque_repository import DepositoSaqueRepository
from api.persistence.repositories.saldo_repository import SaldoRepository
from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.persistence.repositories.moeda_repository import MoedaRepository
from api.models.deposito_saque_models import (
    DepositoRequest,
    SaqueRequest,
    OperacaoResponse,
    HistoricoResponse
)


class DepositoSaqueService:
    """
    Lógica de negócio para depósitos e saques.
    """

    def __init__(self):
        self.deposito_saque_repo = DepositoSaqueRepository()
        self.saldo_repo = SaldoRepository()
        self.carteira_repo = CarteiraRepository()
        self.moeda_repo = MoedaRepository()

    # ========================================
    # DEPÓSITO
    # ========================================

    def realizar_deposito(
        self, 
        endereco_carteira: str, 
        request: DepositoRequest
    ) -> OperacaoResponse:
        """
        Realiza um depósito na carteira.
        
        Regras:
        - Não exige chave privada
        - Não cobra taxa
        - Atualiza saldo
        - Registra histórico
        
        Args:
            endereco_carteira: Endereço da carteira
            request: Dados do depósito
        
        Returns:
            OperacaoResponse: Detalhes da operação
        
        Raises:
            ValueError: Se validações falharem
        """
        # 1) Validar carteira existe e está ativa
        carteira = self.carteira_repo.buscar_por_endereco(endereco_carteira)
        if not carteira:
            raise ValueError(f"Carteira {endereco_carteira} não encontrada")
        
        if carteira["status"] == "BLOQUEADA":
            raise ValueError("Carteira está bloqueada")

        # 2) Validar moeda existe
        if not self.moeda_repo.existe(request.codigo_moeda):
            raise ValueError(f"Moeda {request.codigo_moeda} não suportada")

        # 3) Buscar saldo atual
        saldo_anterior = self.saldo_repo.buscar_saldo_especifico(
            endereco_carteira, 
            request.codigo_moeda
        )
        
        if saldo_anterior is None:
            # Criar saldo zerado se não existir
            self.saldo_repo.criar_saldo_inicial(endereco_carteira, request.codigo_moeda)
            saldo_anterior = Decimal("0.00000000")

        # 4) Calcular novo saldo
        saldo_posterior = saldo_anterior + request.valor

        # 5) Atualizar saldo no banco
        self.saldo_repo.atualizar_saldo(
            endereco_carteira,
            request.codigo_moeda,
            saldo_posterior
        )

        # 6) Registrar histórico
        operacao = self.deposito_saque_repo.registrar_deposito(
            endereco_carteira=endereco_carteira,
            codigo_moeda=request.codigo_moeda,
            valor=request.valor,
            saldo_anterior=saldo_anterior,
            saldo_posterior=saldo_posterior
        )

        # 7) Retornar resposta
        return OperacaoResponse(**operacao)

    # ========================================
    # SAQUE
    # ========================================

    def realizar_saque(
        self, 
        endereco_carteira: str, 
        request: SaqueRequest
    ) -> OperacaoResponse:
        """
        Realiza um saque da carteira.
        
        Regras:
        - Exige chave privada válida
        - Cobra taxa (configurada no .env)
        - Verifica saldo suficiente (valor + taxa)
        - Atualiza saldo
        - Registra histórico
        
        Args:
            endereco_carteira: Endereço da carteira
            request: Dados do saque
        
        Returns:
            OperacaoResponse: Detalhes da operação
        
        Raises:
            ValueError: Se validações falharem
        """
        # 1) Validar carteira existe e está ativa
        carteira = self.carteira_repo.buscar_por_endereco(endereco_carteira)
        if not carteira:
            raise ValueError(f"Carteira {endereco_carteira} não encontrada")
        
        if carteira["status"] == "BLOQUEADA":
            raise ValueError("Carteira está bloqueada")

        # 2) VALIDAR CHAVE PRIVADA
        if not self.carteira_repo.validar_chave_privada(
            endereco_carteira, 
            request.chave_privada
        ):
            raise ValueError("Chave privada inválida")

        # 3) Validar moeda existe
        if not self.moeda_repo.existe(request.codigo_moeda):
            raise ValueError(f"Moeda {request.codigo_moeda} não suportada")

        # 4) Buscar saldo atual
        saldo_anterior = self.saldo_repo.buscar_saldo_especifico(
            endereco_carteira, 
            request.codigo_moeda
        )
        
        if saldo_anterior is None:
            raise ValueError(f"Sem saldo em {request.codigo_moeda}")

        # 5) Calcular taxa
        taxa_percentual = Decimal(os.getenv("TAXA_SAQUE_PERCENTUAL", "0.01"))
        taxa = request.valor * taxa_percentual
        valor_liquido = request.valor + taxa  # No saque, debita valor + taxa

        # 6) Verificar saldo suficiente
        if saldo_anterior < valor_liquido:
            raise ValueError(
                f"Saldo insuficiente. Necessário: {valor_liquido} "
                f"(valor: {request.valor} + taxa: {taxa}). "
                f"Disponível: {saldo_anterior}"
            )

        # 7) Calcular novo saldo
        saldo_posterior = saldo_anterior - valor_liquido

        # 8) Atualizar saldo no banco
        self.saldo_repo.atualizar_saldo(
            endereco_carteira,
            request.codigo_moeda,
            saldo_posterior
        )

        # 9) Registrar histórico
        operacao = self.deposito_saque_repo.registrar_saque(
            endereco_carteira=endereco_carteira,
            codigo_moeda=request.codigo_moeda,
            valor=request.valor,
            taxa=taxa,
            valor_liquido=valor_liquido,
            saldo_anterior=saldo_anterior,
            saldo_posterior=saldo_posterior
        )

        # 10) Retornar resposta
        return OperacaoResponse(**operacao)

    # ========================================
    # HISTÓRICO
    # ========================================

    def listar_historico(
        self, 
        endereco_carteira: str,
        codigo_moeda: str = None
    ) -> HistoricoResponse:
        """
        Lista histórico de depósitos e saques.
        
        Args:
            endereco_carteira: Endereço da carteira
            codigo_moeda: (Opcional) Filtrar por moeda
        
        Returns:
            HistoricoResponse: Lista de operações
        
        Raises:
            ValueError: Se carteira não existe
        """
        # Validar carteira existe
        carteira = self.carteira_repo.buscar_por_endereco(endereco_carteira)
        if not carteira:
            raise ValueError(f"Carteira {endereco_carteira} não encontrada")

        # Buscar histórico
        operacoes_raw = self.deposito_saque_repo.listar_historico(
            endereco_carteira, 
            codigo_moeda
        )

        operacoes = [OperacaoResponse(**op) for op in operacoes_raw]

        return HistoricoResponse(
            endereco_carteira=endereco_carteira,
            total_operacoes=len(operacoes),
            operacoes=operacoes
        )
