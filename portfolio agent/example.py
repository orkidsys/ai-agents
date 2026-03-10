"""
Example usage of the Portfolio Agent.

This script demonstrates how to use the PortfolioAgent class
to analyze cryptocurrency portfolios.
"""
from main import PortfolioAgent
from datetime import datetime
import json


def example_basic_analysis():
    """Example of basic portfolio analysis."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Portfolio Analysis")
    print("=" * 70)
    
    # Initialize the agent
    agent = PortfolioAgent(model_name="gpt-4", temperature=0.3)
    
    # Analyze portfolio
    result = agent.analyze(
        query="Review my portfolio",
        evm_wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
        verbose=True
    )
    
    # Print results
    agent.print_analysis(result)
    
    return result


def example_daily_report():
    """Example of daily portfolio report."""
    print("=" * 70)
    print("EXAMPLE 2: Daily Portfolio Report")
    print("=" * 70)
    
    agent = PortfolioAgent()
    
    result = agent.analyze(
        query="Give me a daily report",
        evm_wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
        solana_wallet_address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
        verbose=True
    )
    
    agent.print_analysis(result)
    return result


def example_performance_analysis():
    """Example of performance analysis."""
    print("=" * 70)
    print("EXAMPLE 3: Performance Analysis")
    print("=" * 70)
    
    agent = PortfolioAgent()
    
    queries = [
        "Analyze my portfolio and show which tokens are underperforming",
        "What is my total profit/loss this month?",
        "Which coins in my portfolio had the highest growth this month?",
    ]
    
    results = []
    for query in queries:
        print(f"\n🔍 Analyzing: {query}")
        try:
            result = agent.analyze(
                query=query,
                evm_wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                verbose=False
            )
            agent.print_analysis(result)
            results.append(result)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return results


def example_save_results():
    """Example of saving results to JSON."""
    print("=" * 70)
    print("EXAMPLE 4: Save Results to JSON")
    print("=" * 70)
    
    agent = PortfolioAgent()
    
    result = agent.analyze(
        query="Review my portfolio",
        evm_wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
        verbose=True
    )
    
    # Save to file
    filename = f"portfolio_analysis_{int(datetime.now().timestamp())}.json"
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✅ Results saved to {filename}")
    return result


if __name__ == "__main__":
    from datetime import datetime
    
    print("\n" + "🚀 PORTFOLIO AGENT EXAMPLES" + "\n")
    
    # Uncomment the example you want to run:
    
    # Example 1: Basic analysis
    # example_basic_analysis()
    
    # Example 2: Daily report
    # example_daily_report()
    
    # Example 3: Performance analysis
    # example_performance_analysis()
    
    # Example 4: Save results
    # example_save_results()
    
    print("Uncomment an example in the script to run it!")
