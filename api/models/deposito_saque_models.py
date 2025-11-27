from typing import Literal
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field


# ========================================
# REQUEST MODELS (Entrada da API)
# ========================================

class DepositoRequest(BaseModel):
    """
    Request para realizar um depósito.
    """
    codigo_moeda: str = Field(
        ..., 
        max_length=10,
        description="Código da moeda (BTC, ETH, SOL, USD, BRL)"
    )
    valor: Decimal = Field(
        ..., 
        gt=0,
        description="Valor a depositar (deve ser maior que zero)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "codigo_moeda": "BTC",
                "valor": "0.50000000"
            }
        }


class SaqueRequest(BaseModel):
    """
    Request para realizar um saque.
    """
    codigo_moeda: str = Field(
        ..., 
        max_length=10,
        description="Código da moeda"
    )
    valor: Decimal = Field(
        ..., 
        gt=0,
        description="Valor a sacar (deve ser maior que zero)"
    )
    chave_privada: str = Field(
        ...,
        description="Chave privada para autorizar o saque"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "codigo_moeda": "BTC",
                "valor": "0.10000000",
                "chave_privada": "d4e5f6a7b8c9..."
            }
        }


# ========================================
# RESPONSE MODELS (Saída da API)
# ========================================

class OperacaoResponse(BaseModel):
    """
    Response padrão para operações de depósito e saque.
    """
    id_operacao: int = Field(..., description="ID único da operação")
    endereco_carteira: str = Field(..., description="Endereço da carteira")
    codigo_moeda: str = Field(..., description="Código da moeda")
    tipo_operacao: Literal["DEPOSITO", "SAQUE"] = Field(..., description="Tipo da operação")
    valor: Decimal = Field(..., description="Valor da operação")
    taxa: Decimal = Field(..., description="Taxa cobrada")
    valor_liquido: Decimal = Field(..., description="Valor líquido (valor ± taxa)")
    saldo_anterior: Decimal = Field(..., description="Saldo antes da operação")
    saldo_posterior: Decimal = Field(..., description="Saldo após a operação")
    data_operacao: datetime = Field(..., description="Data/hora da operação")

    class Config:
        json_schema_extra = {
            "example": {
                "id_operacao": 1,
                "endereco_carteira": "3a2f1b4c...",
                "codigo_moeda": "BTC",
                "tipo_operacao": "DEPOSITO",
                "valor": "0.50000000",
                "taxa": "0.00000000",
                "valor_liquido": "0.50000000",
                "saldo_anterior": "0.00000000",
                "saldo_posterior": "0.50000000",
                "data_operacao": "2024-01-15T10:45:00"
            }
        }


class HistoricoResponse(BaseModel):
    """
    Lista de operações de depósito/saque.
    """
    endereco_carteira: str
    total_operacoes: int
    operacoes: list[OperacaoResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "endereco_carteira": "3a2f1b4c...",
                "total_operacoes": 2,
                "operacoes": [
                    {
                        "id_operacao": 1,
                        "tipo_operacao": "DEPOSITO",
                        "valor": "0.50000000",
                        # ... outros campos ...
                    }
                ]
            }
        }