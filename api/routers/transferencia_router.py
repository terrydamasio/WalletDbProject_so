from fastapi import APIRouter, HTTPException, status, Query
from typing import Literal

from api.services.transferencia_service import TransferenciaService
from api.models.transferencia_models import (
    TransferenciaRequest,
    TransferenciaResponse,
    HistoricoTransferenciaResponse
)


router = APIRouter(prefix="/carteiras", tags=["Transferências"])


# ========================================
# REALIZAR TRANSFERÊNCIA
# ========================================

@router.post(
    "/{endereco_origem}/transferencias",
    response_model=TransferenciaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Realizar transferência",
    description=(
        "Transfere saldo de uma carteira para outra.\n\n"
        "**Características:**\n"
        "- ⚠️ Exige chave privada da carteira origem\n"
        "- Origem paga taxa (padrão: 1%)\n"
        "- Destino recebe valor sem taxa\n"
        "- Total debitado da origem = valor + taxa\n"
        "- Atualiza saldos de ambas as carteiras\n"
        "- Registra no histórico"
    )
)
def realizar_transferencia(
    endereco_origem: str,
    request: TransferenciaRequest
):
    """
    Realiza transferência entre carteiras.
    """
    try:
        service = TransferenciaService()
        return service.realizar_transferencia(endereco_origem, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao realizar transferência: {str(e)}"
        )


# ========================================
# HISTÓRICO
# ========================================

@router.get(
    "/{endereco_carteira}/transferencias",
    response_model=HistoricoTransferenciaResponse,
    summary="Consultar histórico de transferências",
    description="Retorna o histórico de transferências de uma carteira."
)
def listar_historico_transferencias(
    endereco_carteira: str,
    tipo: Literal["enviadas", "recebidas"] = Query(
        None,
        description="Filtrar por tipo: 'enviadas' ou 'recebidas' (opcional)"
    )
):
    """
    Lista o histórico de transferências.
    """
    try:
        service = TransferenciaService()
        return service.listar_historico(endereco_carteira, tipo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar histórico: {str(e)}"
        )
