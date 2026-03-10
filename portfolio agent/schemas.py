"""
Schema-Guided Reasoning (SGR) schemas for Portfolio Analysis.

This implements a 5-step reasoning process enforced by Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


# ============================================================================
# Token and Market Data Schemas
# ============================================================================

class TokenHolding(BaseModel):
    """Individual token holding data."""
    symbol: str = Field(description="Token symbol (e.g., BTC, ETH)")
    name: str = Field(description="Full token name")
    chain: str = Field(description="Blockchain network (e.g., ethereum, solana)")
    amount: float = Field(description="Amount of tokens held")
    amountUsd: float = Field(description="Amount of tokens held in USD")
    currentPrice: float = Field(description="Current price in USD")
    historicalPrice: float = Field(description="Price at start of period in USD")
    priceChange: float = Field(description="Price change in USD (currentPrice - historicalPrice)")
    priceChangePercent: float = Field(description="Price change percentage")


class TopToken(BaseModel):
    """Top token from market data."""
    coingeckoId: str = Field(description="CoinGecko token identifier")
    symbol: str = Field(description="Token symbol")
    name: str = Field(description="Token name")
    marketCapRank: int = Field(description="Market capitalization rank")
    currentPrice: float = Field(description="Current token price in USD")
    priceChange: float = Field(description="Price change percentage over the period")


# ============================================================================
# 5-Step SGR Schema for Portfolio Analysis
# ============================================================================

class Step1RequestParsing(BaseModel):
    """STEP 1: Request Parsing"""
    userQuery: str = Field(description="The original user question")
    timeframe: Literal["unknown", "daily", "weekly", "monthly"] = Field(
        description="Extracted time period from user query, default to 'unknown' if not specified"
    )
    walletAddresses: dict = Field(
        description="Wallet addresses to analyze (evm and/or solana)"
    )
    parsingReasoning: str = Field(
        description="Explain how you identified the time period and report type from the user query"
    )


class Step2DataFetching(BaseModel):
    """STEP 2: Portfolio Data Fetching"""
    toolsUsed: List[str] = Field(
        description="List of used tools (e.g., ['get_historical_portfolio_data'])"
    )
    portfolio: List[TokenHolding] = Field(
        description="Complete token holdings data with current and historical values"
    )
    fetchingNotes: str = Field(
        description="Notes about the data fetching process: which tools were used, any issues encountered, data availability"
    )


class Step3CompositionAnalysis(BaseModel):
    """STEP 3: Portfolio Composition Analysis"""
    totalAmountUsd: float = Field(description="Total portfolio value in USD across all tokens")
    topHoldings: List[str] = Field(
        max_length=5,
        description="Top 5 tokens in portfolio, sorted by USD value in descending order"
    )
    topGainers: List[TopToken] = Field(
        max_length=10,
        description="Top performing tokens by USD value change"
    )
    topLosers: List[TopToken] = Field(
        max_length=10,
        description="Bottom performing tokens by USD value change"
    )
    compositionSummary: str = Field(
        description="Summary of portfolio composition and diversification"
    )


class Step4PerformanceAnalysis(BaseModel):
    """STEP 4: Performance Analysis"""
    periodStartValue: float = Field(description="Total portfolio value at start of period in USD")
    periodEndValue: float = Field(description="Total portfolio value at end of period in USD")
    totalDeltaUSD: float = Field(description="Total change in USD value (end - start)")
    totalDeltaPercentage: float = Field(description="Total percentage change in portfolio USD value")
    tokensOrderedByPerformance: List[str] = Field(
        description="Array of token symbols sorted by decreasing performance in the portfolio by USD value change. ONLY include tokens that are in the portfolio."
    )
    performanceSummary: str = Field(
        description="Summary of portfolio performance over the time period"
    )


class Step5ReportGeneration(BaseModel):
    """STEP 5: Report Generation"""
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level in the analysis based on data completeness"
    )
    error: Literal["tool_error", "llm_error", "user_error", "no_error"] = Field(
        description="The type of error that occurred. tool_error=the tool call failed, user_error=the user question contains non-cryptocurrency related content, llm_error=all other errors, no_error=no error occurred"
    )
    keyTakeaways: List[str] = Field(
        description="3-5 key takeaways from the portfolio analysis"
    )
    recommendations: List[str] = Field(
        description="Observations about portfolio composition and performance (not investment advice)"
    )
    limitations: List[str] = Field(
        description="Data limitations and analysis constraints"
    )
    summary: str = Field(
        description="Summary of the portfolio analysis. Always include 'This is not financial advice.'"
    )


class PortfolioAnalysisResponse(BaseModel):
    """Complete 5-step Schema-Guided Reasoning response for portfolio analysis."""
    step1_requestParsing: Step1RequestParsing = Field(
        description="STEP 1 (MANDATORY): Parse user request to extract time period, report type, and wallet addresses."
    )
    step2_dataFetching: Step2DataFetching = Field(
        description="STEP 2 (MANDATORY): Call get_historical_portfolio_data tool EXACTLY ONCE using the timeframe from STEP 1."
    )
    step3_compositionAnalysis: Step3CompositionAnalysis = Field(
        description="STEP 3 (MANDATORY): Analyze portfolio composition including total value, top tokens, and diversification."
    )
    step4_performanceAnalysis: Step4PerformanceAnalysis = Field(
        description="STEP 4 (MANDATORY): Analyze portfolio performance including wins/losses, best/worst performers, and overall metrics."
    )
    step5_reportGeneration: Step5ReportGeneration = Field(
        description="STEP 5 (MANDATORY): Generate comprehensive portfolio report with insights and final analysis."
    )
