from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field


class Carteira(BaseModel):
    """
    Representa uma carteira (sem expor a chave privada).
    """
    endereco_carteira: str = Field(..., description="Endereço público da carteira")
    data_criacao: datetime = Field(..., description="Data/hora de criação")
    status: Literal["ATIVA", "BLOQUEADA"] = Field(..., description="Status da carteira")

    class Config:
        json_schema_extra = {
            "example": {
                "endereco_carteira": "abc123def456",
                "data_criacao": "2024-01-15T10:00:00",
                "status": "ATIVA"
            }
        }


class CarteiraCriada(Carteira):
    """
    Retornada apenas na criação - inclui a chave privada.
    ⚠️ A chave privada NUNCA mais será exibida após esta resposta!
    """
    chave_privada: str = Field(..., description="Chave privada (guardar com segurança!)")

    class Config:
        json_schema_extra = {
            "example": {
                "endereco_carteira": "abc123def456",
                "data_criacao": "2024-01-15T10:00:00",
                "status": "ATIVA",
                "chave_privada": "d4e5f6a7b8c9..."
            }
        }
