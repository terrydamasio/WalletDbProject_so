from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# ========================================
# REQUEST MODELS
# ========================================

class TransferenciaRequest(BaseModel):
    """
    Request para realizar uma transferência.
    """
    endereco_destino: str = Field(
        ...,
        max_length=100,
        description="Endereço da carteira destino"
    )
    codigo_moeda: str = Field(
        ..., 
        max_length=10,
        description="Código da moeda a transferir"
    )
    valor: Decimal = Field(
        ..., 
        gt=0,
        description="Valor a transferir (deve ser maior que zero)"
    )
    chave_privada: str = Field(
        ...,
        description="Chave privada da carteira origem para autorizar"
    )

    @field_validator('codigo_moeda')
    @classmethod
    def validar_moeda(cls, v: str) -> str:
        """Converte moeda para maiúsculas."""
        return v.upper()

    class Config:
        json_schema_extra = {
            "example": {
                "endereco_destino": "abc123def456",
                "codigo_moeda": "BTC",
                "valor": "0.10000000",
                "chave_privada": "d4e5f6a7b8c9..."
            }
        }


# ========================================
# RESPONSE MODELS
# ========================================

class TransferenciaResponse(BaseModel):
    """
    Response com detalhes da transferência realizada.
    """
    id_transferencia: int
    endereco_origem: str
    endereco_destino: str
    codigo_moeda: str
    valor: Decimal
    taxa: Decimal
    valor_liquido: Decimal
    saldo_origem_anterior: Decimal
    saldo_origem_posterior: Decimal
    saldo_destino_anterior: Decimal
    saldo_destino_posterior: Decimal
    data_transferencia: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id_transferencia": 1,
                "endereco_origem": "3a2f1b4c...",
                "endereco_destino": "9z8y7x6w...",
                "codigo_moeda": "BTC",
                "valor": "0.10000000",
                "taxa": "0.00100000",
                "valor_liquido": "0.10000000",
                "saldo_origem_anterior": "0.50000000",
                "saldo_origem_posterior": "0.39900000",
                "saldo_destino_anterior": "0.00000000",
                "saldo_destino_posterior": "0.10000000",
                "data_transferencia": "2024-01-15T12:30:00"
            }
        }


class HistoricoTransferenciaResponse(BaseModel):
    """
    Lista de transferências de uma carteira.
    """
    endereco_carteira: str
    total_transferencias: int
    transferencias: list[TransferenciaResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "endereco_carteira": "3a2f1b4c...",
                "total_transferencias": 2,
                "transferencias": []
            }
        }
