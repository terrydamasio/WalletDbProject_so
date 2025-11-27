from fastapi import APIRouter, HTTPException, status, Query

from api.services.conversao_service import ConversaoService
from api.models.conversao_models import (
    ConversaoRequest,
    CotacaoRequest,
    CotacaoResponse,
    ConversaoResponse,
    HistoricoConversaoResponse
)


router = APIRouter(prefix="/carteiras", tags=["Conversões"])


# ========================================
# CONSULTAR COTAÇÃO
# ========================================

@router.post(
    "/cotacao",
    response_model=CotacaoResponse,
    summary="Consultar cotação",
    description=(
        "Consulta a cotação atual entre duas moedas na Coinbase.\n\n"
        "**Não realiza conversão**, apenas consulta o preço."
    )
)
def consultar_cotacao(request: CotacaoRequest):
    """
    Consulta cotação entre moedas.
    """
    try:
        service = ConversaoService()
        return service.consultar_cotacao(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar cotação: {str(e)}"
        )


# ========================================
# REALIZAR CONVERSÃO
# ========================================

@router.post(
    "/{endereco_carteira}/conversoes",
    response_model=ConversaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Realizar conversão",
    description=(
        "Converte saldo de uma moeda para outra.\n\n"
        "Características:\n"
        "- ⚠️ Exige chave privada para autorização\n"
        "- Usa cotação em tempo real da Coinbase\n"
        "- Cobra taxa configurada (padrão: 2%)\n"
        "- Atualiza saldos de ambas as moedas\n"
        "- Registra no histórico"
    )
)
    
def realizar_conversao(
    endereco_carteira: str,
    request: ConversaoRequest
):
    """
    Realiza conversão entre moedas.
    """
    try:
        service = ConversaoService()
        return service.realizar_conversao(endereco_carteira, request)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao realizar conversão: {str(e)}"
        )

@router.get(
    "/{endereco_carteira}/conversoes",
    response_model=HistoricoConversaoResponse,
    summary="Consultar histórico de conversões",
    description="Retorna o histórico de conversões de uma carteira."
)

def listar_historico_conversoes(
    endereco_carteira: str,
    moeda: str = Query(
        None,
        description="Filtrar por moeda de origem ou destino (opcional)"
    )
):
    """
    Lista o histórico de conversões.
    """
    try:
        service = ConversaoService()
        return service.listar_historico(endereco_carteira, moeda)

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