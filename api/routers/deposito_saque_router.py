from fastapi import APIRouter, HTTPException, status, Query

from api.services.deposito_saque_service import DepositoSaqueService
from api.models.deposito_saque_models import (
    DepositoRequest,
    SaqueRequest,
    OperacaoResponse,
    HistoricoResponse
)


router = APIRouter(prefix="/carteiras", tags=["Depósitos e Saques"])


# ========================================
# DEPÓSITO
# ========================================

@router.post(
    "/{endereco_carteira}/depositos",
    response_model=OperacaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Realizar depósito",
    description=(
        "Deposita valor em uma carteira.\n\n"
        "**Características:**\n"
        "- Não exige chave privada\n"
        "- Não cobra taxa\n"
        "- Atualiza saldo imediatamente\n"
        "- Registra no histórico"
    )
)
def realizar_deposito(
    endereco_carteira: str,
    request: DepositoRequest
):
    """
    Realiza um depósito na carteira.
    """
    try:
        service = DepositoSaqueService()
        return service.realizar_deposito(endereco_carteira, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao realizar depósito: {str(e)}"
        )


# ========================================
# SAQUE
# ========================================

@router.post(
    "/{endereco_carteira}/saques",
    response_model=OperacaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Realizar saque",
    description=(
        "Saca valor de uma carteira.\n\n"
        "**Características:**\n"
        "- ⚠️ Exige chave privada para autorização\n"
        "- Cobra taxa configurada (padrão: 1%)\n"
        "- Verifica saldo suficiente (valor + taxa)\n"
        "- Atualiza saldo imediatamente\n"
        "- Registra no histórico"
    )
)
def realizar_saque(
    endereco_carteira: str,
    request: SaqueRequest
):
    """
    Realiza um saque da carteira.
    """
    try:
        service = DepositoSaqueService()
        return service.realizar_saque(endereco_carteira, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao realizar saque: {str(e)}"
        )


# ========================================
# HISTÓRICO
# ========================================

@router.get(
    "/{endereco_carteira}/historico",
    response_model=HistoricoResponse,
    summary="Consultar histórico",
    description="Retorna o histórico de depósitos e saques de uma carteira."
)
def listar_historico(
    endereco_carteira: str,
    codigo_moeda: str = Query(
        None, 
        description="Filtrar por moeda específica (opcional)"
    )
):
    """
    Lista o histórico de depósitos e saques.
    """
    try:
        service = DepositoSaqueService()
        return service.listar_historico(endereco_carteira, codigo_moeda)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar histórico: {str(e)}"
        )
