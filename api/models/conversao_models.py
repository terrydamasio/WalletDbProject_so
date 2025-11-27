from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# ========================================
# REQUEST MODELS
# ========================================

class ConversaoRequest(BaseModel):
    """
    Request para realizar uma conversão entre moedas.
    """
    moeda_origem: str = Field(
        ..., 
        max_length=10,
        description="Código da moeda de origem"
    )
    moeda_destino: str = Field(
        ..., 
        max_length=10,
        description="Código da moeda de destino"
    )
    valor: Decimal = Field(
        ..., 
        gt=0,
        description="Valor a converter (deve ser maior que zero)"
    )
    chave_privada: str = Field(
        ...,
        description="Chave privada para autorizar a conversão"
    )

    @field_validator('moeda_origem', 'moeda_destino')
    @classmethod
    def validar_moeda(cls, v: str) -> str:
        """Converte moedas para maiúsculas."""
        return v.upper()

    class Config:
        json_schema_extra = {
            "example": {
                "moeda_origem": "BTC",
                "moeda_destino": "USD",
                "valor": "0.50000000",
                "chave_privada": "d4e5f6a7b8c9..."
            }
        }


class CotacaoRequest(BaseModel):
    """
    Request para consultar cotação entre moedas.
    """
    moeda_origem: str = Field(..., max_length=10)
    moeda_destino: str = Field(..., max_length=10)

    @field_validator('moeda_origem', 'moeda_destino')
    @classmethod
    def validar_moeda(cls, v: str) -> str:
        return v.upper()

    class Config:
        json_schema_extra = {
            "example": {
                "moeda_origem": "BTC",
                "moeda_destino": "USD"
            }
        }


# ========================================
# RESPONSE MODELS
# ========================================

class CotacaoResponse(BaseModel):
    """
    Response com cotação entre moedas.
    """
    moeda_origem: str
    moeda_destino: str
    cotacao: Decimal
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "moeda_origem": "BTC",
                "moeda_destino": "USD",
                "cotacao": "43250.50000000",
                "timestamp": "2024-01-15T11:30:00"
            }
        }


class ConversaoResponse(BaseModel):
    """
    Response com detalhes da conversão realizada.
    """
    id_conversao: int
    endereco_carteira: str
    moeda_origem: str
    moeda_destino: str
    valor_origem: Decimal
    cotacao: Decimal
    valor_convertido: Decimal
    taxa: Decimal
    valor_liquido: Decimal
    saldo_origem_anterior: Decimal
    saldo_origem_posterior: Decimal
    saldo_destino_anterior: Decimal
    saldo_destino_posterior: Decimal
    data_conversao: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id_conversao": 1,
                "endereco_carteira": "3a2f1b4c...",
                "moeda_origem": "BTC",
                "moeda_destino": "USD",
                "valor_origem": "0.50000000",
                "cotacao": "43250.50000000",
                "valor_convertido": "21625.25000000",
                "taxa": "432.50500000",
                "valor_liquido": "21192.74500000",
                "saldo_origem_anterior": "1.00000000",
                "saldo_origem_posterior": "0.50000000",
                "saldo_destino_anterior": "0.00000000",
                "saldo_destino_posterior": "21192.74500000",
                "data_conversao": "2024-01-15T11:30:00"
            }
        }


class HistoricoConversaoResponse(BaseModel):
    """
    Lista de conversões de uma carteira.
    """
    endereco_carteira: str
    total_conversoes: int
    conversoes: list[ConversaoResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "endereco_carteira": "3a2f1b4c...",
                "total_conversoes": 2,
                "conversoes": []
            }
        }
