import httpx
from decimal import Decimal
from typing import Dict, Any


class CoinbaseService:
    """
    Responsável por obter cotações da API pública da Coinbase.
    
    Documentação: https://docs.cloud.coinbase.com/sign-in-with-coinbase/docs/api-prices
    """

    BASE_URL = "https://api.coinbase.com/v2/prices"

    def __init__(self):
        self.client = httpx.Client(timeout=10.0)

    def obter_cotacao(self, moeda_origem: str, moeda_destino: str) -> Decimal:
        """
        Obtém a cotação spot (atual) entre duas moedas.
        
        Args:
            moeda_origem: Código da moeda de origem (ex: BTC)
            moeda_destino: Código da moeda de destino (ex: USD)
        
        Returns:
            Decimal: Taxa de conversão (preço spot)
        
        Raises:
            ValueError: Se não conseguir obter a cotação
            
        Exemplo:
            >>> service = CoinbaseService()
            >>> cotacao = service.obter_cotacao("BTC", "USD")
            >>> print(cotacao)  # Ex: 43250.50
        """
        try:
            # Construir URL: /v2/prices/{MOEDA_ORIGEM}-{MOEDA_DESTINO}/spot
            url = f"{self.BASE_URL}/{moeda_origem}-{moeda_destino}/spot"
            
            # Fazer requisição
            response = self.client.get(url)
            response.raise_for_status()
            
            # Extrair dados
            data = response.json()
            
            # Validar estrutura da resposta
            if "data" not in data or "amount" not in data["data"]:
                raise ValueError("Resposta da API inválida")
            
            # Converter para Decimal
            cotacao = Decimal(data["data"]["amount"])
            
            return cotacao
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(
                    f"Par de moedas {moeda_origem}-{moeda_destino} não suportado pela Coinbase"
                )
            else:
                raise ValueError(f"Erro na API da Coinbase: {e.response.status_code}")
        
        except httpx.RequestError as e:
            raise ValueError(f"Erro de conexão com a API da Coinbase: {str(e)}")
        
        except (KeyError, ValueError) as e:
            raise ValueError(f"Erro ao processar resposta da API: {str(e)}")

    def obter_cotacao_detalhada(
        self, 
        moeda_origem: str, 
        moeda_destino: str
    ) -> Dict[str, Any]:
        """
        Obtém cotação com informações detalhadas.
        
        Args:
            moeda_origem: Código da moeda de origem
            moeda_destino: Código da moeda de destino
        
        Returns:
            Dict com: amount (cotação), currency (moeda destino), base (moeda origem)
        """
        try:
            url = f"{self.BASE_URL}/{moeda_origem}-{moeda_destino}/spot"
            response = self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            return {
                "cotacao": Decimal(data["data"]["amount"]),
                "moeda_base": data["data"]["base"],
                "moeda_cotacao": data["data"]["currency"]
            }
            
        except Exception as e:
            raise ValueError(f"Erro ao obter cotação detalhada: {str(e)}")

    def calcular_conversao(
        self, 
        valor_origem: Decimal, 
        moeda_origem: str, 
        moeda_destino: str
    ) -> Dict[str, Decimal]:
        """
        Calcula quanto vale um valor convertido entre moedas.
        
        Args:
            valor_origem: Valor a converter
            moeda_origem: Moeda de origem
            moeda_destino: Moeda de destino
        
        Returns:
            Dict com: cotacao, valor_convertido
            
        Exemplo:
            >>> service.calcular_conversao(Decimal("0.5"), "BTC", "USD")
            {
                "cotacao": Decimal("43250.50"),
                "valor_convertido": Decimal("21625.25")
            }
        """
        cotacao = self.obter_cotacao(moeda_origem, moeda_destino)
        valor_convertido = valor_origem * cotacao
        
        return {
            "cotacao": cotacao,
            "valor_convertido": valor_convertido
        }

    def close(self):
        """Fecha o cliente HTTP."""
        self.client.close()

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.close()
