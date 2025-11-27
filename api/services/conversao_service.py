import os
from decimal import Decimal
from typing import List

from api.persistence.repositories.conversao_repository import ConversaoRepository
from api.persistence.repositories.saldo_repository import SaldoRepository
from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.persistence.repositories.moeda_repository import MoedaRepository
from api.services.coinbase_service import CoinbaseService
from api.models.conversao_models import (
    ConversaoRequest,
    CotacaoRequest,
    CotacaoResponse,
    ConversaoResponse,
    HistoricoConversaoResponse
)


class ConversaoService:
    """
    Lógica de negócio para conversões entre moedas.
    """

    def __init__(self):
        self.conversao_repo = ConversaoRepository()
        self.saldo_repo = SaldoRepository()
        self.carteira_repo = CarteiraRepository()
        self.moeda_repo = MoedaRepository()
        self.coinbase_service = CoinbaseService()

    # ========================================
    # CONSULTAR COTAÇÃO
    # ========================================

    def consultar_cotacao(self, request: CotacaoRequest) -> CotacaoResponse:
        """
        Consulta a cotação entre duas moedas na Coinbase.
        
        Args:
            request: Dados da consulta
        
        Returns:
            CotacaoResponse: Cotação atual
        
        Raises:
            ValueError: Se moedas não existirem ou par não for suportado
        """
        # Validar moedas existem
        if not self.moeda_repo.existe(request.moeda_origem):
            raise ValueError(f"Moeda {request.moeda_origem} não suportada")
        
        if not self.moeda_repo.existe(request.moeda_destino):
            raise ValueError(f"Moeda {request.moeda_destino} não suportada")

        # Obter cotação da Coinbase
        try:
            cotacao = self.coinbase_service.obter_cotacao(
                request.moeda_origem,
                request.moeda_destino
            )
        except ValueError as e:
            raise ValueError(f"Erro ao obter cotação: {str(e)}")

        return CotacaoResponse(
            moeda_origem=request.moeda_origem,
            moeda_destino=request.moeda_destino,
            cotacao=cotacao
        )

    # ========================================
    # REALIZAR CONVERSÃO
    # ========================================

    def realizar_conversao(
        self, 
        endereco_carteira: str, 
        request: ConversaoRequest
    ) -> ConversaoResponse:
        """
        Realiza conversão entre moedas.
        
        Regras:
        - Exige chave privada válida
        - Usa cotação real da Coinbase
        - Cobra taxa (configurada no .env)
        - Verifica saldo suficiente na moeda origem
        - Atualiza saldos de origem e destino
        - Registra histórico
        
        Args:
            endereco_carteira: Endereço da carteira
            request: Dados da conversão
        
        Returns:
            ConversaoResponse: Detalhes da conversão
        
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

        # 3) Validar moedas diferentes
        if request.moeda_origem == request.moeda_destino:
            raise ValueError("Moedas de origem e destino devem ser diferentes")

        # 4) Validar moedas existem
        if not self.moeda_repo.existe(request.moeda_origem):
            raise ValueError(f"Moeda {request.moeda_origem} não suportada")
        
        if not self.moeda_repo.existe(request.moeda_destino):
            raise ValueError(f"Moeda {request.moeda_destino} não suportada")

        # 5) Buscar saldo da moeda de origem
        saldo_origem_anterior = self.saldo_repo.buscar_saldo_especifico(
            endereco_carteira, 
            request.moeda_origem
        )
        
        if saldo_origem_anterior is None or saldo_origem_anterior < request.valor:
            raise ValueError(
                f"Saldo insuficiente em {request.moeda_origem}. "
                f"Necessário: {request.valor}. "
                f"Disponível: {saldo_origem_anterior or 0}"
            )

        # 6) Obter cotação da Coinbase
        try:
            cotacao = self.coinbase_service.obter_cotacao(
                request.moeda_origem,
                request.moeda_destino
            )
        except ValueError as e:
            raise ValueError(f"Erro ao obter cotação: {str(e)}")

        # 7) Calcular valores
        valor_convertido = request.valor * cotacao
        
        taxa_percentual = Decimal(os.getenv("TAXA_CONVERSAO_PERCENTUAL", "0.02"))
        taxa = valor_convertido * taxa_percentual
        
        valor_liquido = valor_convertido - taxa

        # 8) Buscar saldo da moeda de destino
        saldo_destino_anterior = self.saldo_repo.buscar_saldo_especifico(
            endereco_carteira, 
            request.moeda_destino
        )
        
        if saldo_destino_anterior is None:
            self.saldo_repo.criar_saldo_inicial(endereco_carteira, request.moeda_destino)
            saldo_destino_anterior = Decimal("0.00000000")

        # 9) Calcular novos saldos
        saldo_origem_posterior = saldo_origem_anterior - request.valor
        saldo_destino_posterior = saldo_destino_anterior + valor_liquido

        # 10) Atualizar saldos no banco
        self.saldo_repo.atualizar_saldo(
            endereco_carteira,
            request.moeda_origem,
            saldo_origem_posterior
        )
        
        self.saldo_repo.atualizar_saldo(
            endereco_carteira,
            request.moeda_destino,
            saldo_destino_posterior
        )

        # 11) Registrar histórico
        conversao = self.conversao_repo.registrar_conversao(
            endereco_carteira=endereco_carteira,
            moeda_origem=request.moeda_origem,
            moeda_destino=request.moeda_destino,
            valor_origem=request.valor,
            cotacao=cotacao,
            valor_convertido=valor_convertido,
            taxa=taxa,
            valor_liquido=valor_liquido,
            saldo_origem_anterior=saldo_origem_anterior,
            saldo_origem_posterior=saldo_origem_posterior,
            saldo_destino_anterior=saldo_destino_anterior,
            saldo_destino_posterior=saldo_destino_posterior
        )

        # 12) Retornar resposta
        return ConversaoResponse(**conversao)

    # ========================================
    # HISTÓRICO
    # ========================================

    def listar_historico(
        self, 
        endereco_carteira: str,
        moeda: str = None
    ) -> HistoricoConversaoResponse:
        """
        Lista histórico de conversões.
        
        Args:
            endereco_carteira: Endereço da carteira
            moeda: (Opcional) Filtrar por moeda
        
        Returns:
            HistoricoConversaoResponse: Lista de conversões
        
        Raises:
            ValueError: Se carteira não existe
        """
        # Validar carteira existe
        carteira = self.carteira_repo.buscar_por_endereco(endereco_carteira)
        if not carteira:
            raise ValueError(f"Carteira {endereco_carteira} não encontrada")

        # Buscar histórico
        conversoes_raw = self.conversao_repo.listar_historico(
            endereco_carteira, 
            moeda
        )

        conversoes = [ConversaoResponse(**conv) for conv in conversoes_raw]

        return HistoricoConversaoResponse(
            endereco_carteira=endereco_carteira,
            total_conversoes=len(conversoes),
            conversoes=conversoes
        )
