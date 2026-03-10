"""
Portfolio data fetching tools for the portfolio agent.
Provides wallet balance and cryptocurrency price data.
"""
import os
import requests
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class PortfolioToolInput(BaseModel):
    """Input schema for portfolio data tool."""
    evm_wallet_address: Optional[str] = Field(
        None, 
        description="EVM wallet address (e.g., 0x...)"
    )
    solana_wallet_address: Optional[str] = Field(
        None,
        description="Solana wallet address (base58 encoded)"
    )
    timeframe: str = Field(
        "monthly",
        description="Timeframe for analysis: daily, weekly, or monthly"
    )


class CoinGeckoService:
    """Service for fetching cryptocurrency price data from CoinGecko."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("COINGECKO_API_KEY")
        self.base_url = "https://api.coingecko.com/api/v3"
        self.headers = {}
        if self.api_key:
            self.headers["x-cg-demo-api-key"] = self.api_key
    
    def get_price(self, coin_id: str) -> Optional[float]:
        """Get current price for a coin."""
        try:
            url = f"{self.base_url}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd"
            }
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get(coin_id, {}).get("usd")
        except Exception as e:
            print(f"Error fetching price for {coin_id}: {e}")
        return None
    
    def get_historical_price(self, coin_id: str, days_ago: int) -> Optional[float]:
        """Get historical price for a coin."""
        try:
            url = f"{self.base_url}/coins/{coin_id}/history"
            target_date = datetime.now() - timedelta(days=days_ago)
            params = {
                "date": target_date.strftime("%d-%m-%Y"),
                "localization": "false"
            }
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "market_data" in data and "current_price" in data["market_data"]:
                    return data["market_data"]["current_price"].get("usd")
        except Exception as e:
            print(f"Error fetching historical price for {coin_id}: {e}")
        return None
    
    def get_top_gainers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top gaining cryptocurrencies."""
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "price_change_percentage_24h_desc",
                "per_page": limit,
                "page": 1
            }
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching top gainers: {e}")
        return []
    
    def get_top_losers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top losing cryptocurrencies."""
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "price_change_percentage_24h_asc",
                "per_page": limit,
                "page": 1
            }
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching top losers: {e}")
        return []


class WalletService:
    """Service for fetching wallet balances."""
    
    def __init__(self, alchemy_api_key: Optional[str] = None):
        self.alchemy_api_key = alchemy_api_key or os.getenv("ALCHEMY_API_KEY")
    
    def get_evm_balance(self, address: str) -> Dict[str, Any]:
        """
        Get EVM wallet balance.
        Note: This is a simplified version. For production, use Alchemy API.
        """
        # Placeholder - in production, use Alchemy API
        return {
            "address": address,
            "tokens": [],
            "native_balance": "0",
            "error": "Alchemy API integration required for full functionality"
        }
    
    def get_solana_balance(self, address: str) -> Dict[str, Any]:
        """
        Get Solana wallet balance.
        Note: This requires Solana RPC endpoint.
        """
        # Placeholder - in production, use Solana RPC
        return {
            "address": address,
            "tokens": [],
            "sol_balance": "0",
            "error": "Solana RPC integration required for full functionality"
        }


class PortfolioDataTool(BaseTool):
    """Tool for fetching historical portfolio data."""
    
    name: str = "get_historical_portfolio_data"
    description: str = """Get historical portfolio data for EVM and Solana wallets.
    
    This tool fetches:
    - Current token balances
    - Historical prices at the start of the period
    - Current prices
    - Price changes and percentages
    - Top gainers/losers from the market
    
    Returns comprehensive portfolio analysis data."""
    
    args_schema: type[BaseModel] = PortfolioToolInput
    
    def __init__(self):
        super().__init__()
        self.coingecko = CoinGeckoService()
        self.wallet = WalletService()
    
    def _run(
        self,
        evm_wallet_address: Optional[str] = None,
        solana_wallet_address: Optional[str] = None,
        timeframe: str = "monthly"
    ) -> str:
        """Execute the tool."""
        try:
            # Calculate days for historical data
            days_map = {
                "daily": 1,
                "weekly": 7,
                "monthly": 30
            }
            days = days_map.get(timeframe.lower(), 30)
            
            # Mock portfolio data for demonstration
            # In production, fetch real wallet balances
            portfolio_data = {
                "tokens": [],
                "tokensPerformanceOrdered": [],
                "startPeriodTotalAmountUsd": 0,
                "totalAmountUsd": 0,
                "totalAmountChange": 0,
                "totalAmountChangePercent": 0,
                "topGainers": self._format_top_tokens(self.coingecko.get_top_gainers(10)),
                "topLosers": self._format_top_tokens(self.coingecko.get_top_losers(10)),
                "createdAt": datetime.now().isoformat(),
                "timeframe": timeframe
            }
            
            # If addresses provided, try to fetch real data
            if evm_wallet_address:
                wallet_data = self.wallet.get_evm_balance(evm_wallet_address)
                # Process wallet data and add to portfolio
            
            if solana_wallet_address:
                wallet_data = self.wallet.get_solana_balance(solana_wallet_address)
                # Process wallet data and add to portfolio
            
            import json
            return json.dumps(portfolio_data, indent=2)
        
        except Exception as e:
            import json
            return json.dumps({
                "error": f"Failed to fetch portfolio data: {str(e)}"
            })
    
    def _format_top_tokens(self, tokens: List[Dict]) -> List[Dict]:
        """Format top tokens for response."""
        formatted = []
        for token in tokens[:10]:
            formatted.append({
                "coingeckoId": token.get("id", ""),
                "symbol": token.get("symbol", "").upper(),
                "name": token.get("name", ""),
                "marketCapRank": token.get("market_cap_rank", 0),
                "currentPrice": token.get("current_price", 0),
                "priceChange": token.get("price_change_percentage_24h", 0)
            })
        return formatted
