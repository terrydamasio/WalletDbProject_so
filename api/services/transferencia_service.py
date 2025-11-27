import os
from decimal import Decimal
from typing import List

from api.persistence.repositories.transferencia_repository import TransferenciaRepository
from api.persistence.repositories.saldo_repository import SaldoRepository
from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.persistence.repositories.moeda_repository import MoedaRepository
from api.models.transferencia_models import (
    TransferenciaRequest,
    TransferenciaResponse,
    HistoricoTransferenciaResponse
)


class TransferenciaService:
    """
    Lógica de negócio para transferências entre carteiras.
    """

    def __init__(self):
        self.transferencia_repo = TransferenciaRepository()
        self.saldo_repo = SaldoRepository()
        self.carteira_repo = CarteiraRepository()
        self.moeda_repo = MoedaRepository()

    # ========================================
    # REALIZAR TRANSFERÊNCIA
    # ========================================

    def realizar_transferencia(
        self, 
        endereco_origem: str, 
        request: TransferenciaRequest
    ) -> TransferenciaResponse:
        """
        Realiza transferência entre carteiras.
        
        Regras:
        - Exige chave privada da carteira origem
        - Origem paga taxa (configurada no .env)
        - Destino recebe valor líquido (sem taxa aplicada)
        - Verifica saldo suficiente na origem (valor + taxa)
        - Atualiza saldos de origem e destino
        - Registra histórico
        
        Args:
            endereco_origem: Endereço da carteira que envia
            request: Dados da transferência
        
        Returns:
            TransferenciaResponse: Detalhes da transferência
        
        Raises:
            ValueError: Se validações falharem
        """
        # 1) Validar que origem e destino são diferentes
        if endereco_origem == request.endereco_destino:
            raise ValueError("Não é possível transferir para a mesma carteira")

        # 2) Validar carteira origem existe e está ativa
        carteira_origem = self.carteira_repo.buscar_por_endereco(endereco_origem)
        if not carteira_origem:
            raise ValueError(f"Carteira origem {endereco_origem} não encontrada")
        
        if carteira_origem["status"] == "BLOQUEADA":
            raise ValueError("Carteira origem está bloqueada")

        # 3) VALIDAR CHAVE PRIVADA DA ORIGEM
        if not self.carteira_repo.validar_chave_privada(
            endereco_origem, 
            request.chave_privada
        ):
            raise ValueError("Chave privada inválida")

        # 4) Validar carteira destino existe e está ativa
        carteira_destino = self.carteira_repo.buscar_por_endereco(
            request.endereco_destino
        )
        if not carteira_destino:
            raise ValueError(
                f"Carteira destino {request.endereco_destino} não encontrada"
            )
        
        if carteira_destino["status"] == "BLOQUEADA":
            raise ValueError("Carteira destino está bloqueada")

        # 5) Validar moeda existe
        if not self.moeda_repo.existe(request.codigo_moeda):
            raise ValueError(f"Moeda {request.codigo_moeda} não suportada")

        # 6) Buscar saldo da carteira origem
        saldo_origem_anterior = self.saldo_repo.buscar_saldo_especifico(
            endereco_origem, 
            request.codigo_moeda
        )
        
        if saldo_origem_anterior is None:
            raise ValueError(
                f"Carteira origem não possui saldo em {request.codigo_moeda}"
            )

        # 7) Calcular taxa
        taxa_percentual = Decimal(os.getenv("TAXA_TRANSFERENCIA_PERCENTUAL", "0.01"))
        taxa = request.valor * taxa_percentual
        
        # Total a debitar da origem = valor + taxa
        total_debito = request.valor + taxa
        
        # Valor que o destino recebe (sem taxa)
        valor_liquido = request.valor

        # 8) Verificar saldo suficiente na origem
        if saldo_origem_anterior < total_debito:
            raise ValueError(
                f"Saldo insuficiente em {request.codigo_moeda}. "
                f"Necessário: {total_debito} "
                f"(valor: {request.valor} + taxa: {taxa}). "
                f"Disponível: {saldo_origem_anterior}"
            )

        # 9) Buscar saldo da carteira destino
        saldo_destino_anterior = self.saldo_repo.buscar_saldo_especifico(
            request.endereco_destino, 
            request.codigo_moeda
        )
        
        if saldo_destino_anterior is None:
            # Criar saldo zerado se não existir
            self.saldo_repo.criar_saldo_inicial(
                request.endereco_destino, 
                request.codigo_moeda
            )
            saldo_destino_anterior = Decimal("0.00000000")

        # 10) Calcular novos saldos
        saldo_origem_posterior = saldo_origem_anterior - total_debito
        saldo_destino_posterior = saldo_destino_anterior + valor_liquido

        # 11) Atualizar saldo da origem
        self.saldo_repo.atualizar_saldo(
            endereco_origem,
            request.codigo_moeda,
            saldo_origem_posterior
        )

        # 12) Atualizar saldo do destino
        self.saldo_repo.atualizar_saldo(
            request.endereco_destino,
            request.codigo_moeda,
            saldo_destino_posterior
        )

        # 13) Registrar histórico
        transferencia = self.transferencia_repo.registrar_transferencia(
            endereco_origem=endereco_origem,
            endereco_destino=request.endereco_destino,
            codigo_moeda=request.codigo_moeda,
            valor=request.valor,
            taxa=taxa,
            valor_liquido=valor_liquido,
            saldo_origem_anterior=saldo_origem_anterior,
            saldo_origem_posterior=saldo_origem_posterior,
            saldo_destino_anterior=saldo_destino_anterior,
            saldo_destino_posterior=saldo_destino_posterior
        )

        # 14) Retornar resposta
        return TransferenciaResponse(**transferencia)

    # ========================================
    # HISTÓRICO
    # ========================================

    def listar_historico(
        self, 
        endereco_carteira: str,
        tipo: str = None
    ) -> HistoricoTransferenciaResponse:
        """
        Lista histórico de transferências.
        
        Args:
            endereco_carteira: Endereço da carteira
            tipo: 'enviadas', 'recebidas' ou None para todas
        
        Returns:
            HistoricoTransferenciaResponse: Lista de transferências
        
        Raises:
            ValueError: Se carteira não existe ou tipo inválido
        """
        # Validar carteira existe
        carteira = self.carteira_repo.buscar_por_endereco(endereco_carteira)
        if not carteira:
            raise ValueError(f"Carteira {endereco_carteira} não encontrada")

        # Validar tipo
        if tipo and tipo not in ["enviadas", "recebidas"]:
            raise ValueError("Tipo deve ser 'enviadas', 'recebidas' ou None")

        # Buscar histórico
        transferencias_raw = self.transferencia_repo.listar_historico(
            endereco_carteira, 
            tipo
        )

        transferencias = [
            TransferenciaResponse(**transf) 
            for transf in transferencias_raw
        ]

        return HistoricoTransferenciaResponse(
            endereco_carteira=endereco_carteira,
            total_transferencias=len(transferencias),
            transferencias=transferencias
        )
