from fastapi import APIRouter, HTTPException, status
from typing import List

from api.services.carteira_service import CarteiraService
from api.services.saldo_service import SaldoService
from api.models.carteira_models import Carteira, CarteiraCriada
from api.models.saldo_models import ListaSaldos


router = APIRouter(prefix="/carteiras", tags=["Carteiras"])


# ========================================
# ENDPOINTS DE CARTEIRA
# ========================================

@router.post(
    "",
    response_model=CarteiraCriada,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova carteira",
    description=(
        "Cria uma nova carteira com chaves pública e privada.\n\n"
        "⚠️ **ATENÇÃO:** A chave privada é retornada APENAS nesta resposta!\n"
        "Guarde-a com segurança, pois não será possível recuperá-la depois."
    )
)
def criar_carteira():
    """
    Cria uma nova carteira digital.
    """
    try:
        service = CarteiraService()
        return service.criar_carteira()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar carteira: {str(e)}"
        )


@router.get(
    "",
    response_model=List[Carteira],
    summary="Listar todas as carteiras",
    description="Retorna a lista de todas as carteiras cadastradas."
)
def listar_carteiras():
    """
    Lista todas as carteiras.
    """
    try:
        service = CarteiraService()
        return service.listar()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar carteiras: {str(e)}"
        )


@router.get(
    "/{endereco_carteira}",
    response_model=Carteira,
    summary="Buscar carteira por endereço",
    description="Retorna informações básicas de uma carteira específica."
)
def buscar_carteira(endereco_carteira: str):
    """
    Busca uma carteira pelo endereço.
    """
    try:
        service = CarteiraService()
        return service.buscar_por_endereco(endereco_carteira)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar carteira: {str(e)}"
        )


@router.patch(
    "/{endereco_carteira}/bloquear",
    response_model=Carteira,
    summary="Bloquear carteira",
    description="Bloqueia uma carteira, impedindo operações futuras."
)
def bloquear_carteira(endereco_carteira: str):
    """
    Bloqueia uma carteira.
    """
    try:
        service = CarteiraService()
        return service.bloquear(endereco_carteira)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao bloquear carteira: {str(e)}"
        )


# ========================================
# ENDPOINTS DE SALDOS
# ========================================

@router.get(
    "/{endereco_carteira}/saldos",
    response_model=ListaSaldos,
    summary="Consultar saldos da carteira",
    description="Retorna os saldos da carteira em todas as moedas suportadas."
)
def listar_saldos(endereco_carteira: str):
    """
    Lista todos os saldos de uma carteira.
    """
    try:
        service = SaldoService()
        return service.listar_saldos(endereco_carteira)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar saldos: {str(e)}"
        )
