from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field


class SaldoCarteira(BaseModel):
    """
    Representa o saldo de uma carteira em uma moeda específica.
    """
    codigo_moeda: str = Field(..., description="Código da moeda")
    nome_moeda: str = Field(..., description="Nome da moeda")
    saldo: Decimal = Field(..., ge=0, description="Saldo disponível")
    data_atualizacao: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "codigo_moeda": "BTC",
                "nome_moeda": "Bitcoin",
                "saldo": "0.50000000",
                "data_atualizacao": "2024-01-15T10:30:00"
            }
        }


class ListaSaldos(BaseModel):
    """
    Lista de saldos de uma carteira.
    """
    endereco_carteira: str
    saldos: list[SaldoCarteira]
    total_moedas: int

    class Config:
        json_schema_extra = {
            "example": {
                "endereco_carteira": "abc123def456",
                "total_moedas": 5,
                "saldos": [
                    {
                        "codigo_moeda": "BTC",
                        "nome_moeda": "Bitcoin",
                        "saldo": "0.50000000",
                        "data_atualizacao": "2024-01-15T10:30:00"
                    }
                ]
            }
        }
