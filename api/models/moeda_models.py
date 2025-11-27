from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field

class Moeda(BaseModel):
    """
    Representa uma moeda suportada pelo sistema.
    """
    codigo_moeda: str = Field(..., max_length=10, description="Código da moeda (ex: BTC, USD)")
    nome: str = Field(..., max_length=50, description="Nome completo da moeda")
    tipo: Literal["CRYPTO", "FIAT"] = Field(..., description="Tipo da moeda")
    ativo: bool = Field(default=True, description="Se a moeda está ativa")
    data_cadastro: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "codigo_moeda": "BTC",
                "nome": "Bitcoin",
                "tipo": "CRYPTO",
                "ativo": True
            }
        }
