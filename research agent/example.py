"""
Example usage of the Research Agent.

This script demonstrates how to use the ResearchAgent class
to conduct research on various topics.
"""
from main import ResearchAgent


def example_basic_research():
    """Example of basic research usage."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Research")
    print("=" * 70)
    
    # Initialize the agent
    agent = ResearchAgent(model_name="gpt-4", temperature=0.3)
    
    # Conduct research
    result = agent.research(
        "What are the latest developments in quantum computing?",
        verbose=True
    )
    
    # Print results
    agent.print_research(result)
    
    return result


def example_multiple_queries():
    """Example of researching multiple topics."""
    print("=" * 70)
    print("EXAMPLE 2: Multiple Research Queries")
    print("=" * 70)
    
    agent = ResearchAgent()
    
    queries = [
        "Explain the history of Greek mythology",
        "What is machine learning?",
    ]
    
    results = []
    for query in queries:
        print(f"\n🔍 Researching: {query}")
        try:
            result = agent.research(query, verbose=False)
            agent.print_research(result)
            results.append(result)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return results


def example_custom_agent():
    """Example of creating a custom agent with different settings."""
    print("=" * 70)
    print("EXAMPLE 3: Custom Agent Configuration")
    print("=" * 70)
    
    # Create agent with custom temperature (more creative)
    agent = ResearchAgent(
        model_name="gpt-4",
        temperature=0.7  # Higher temperature for more creative responses
    )
    
    result = agent.research(
        "What are the potential future applications of AI?",
        verbose=True
    )
    
    agent.print_research(result)
    return result


if __name__ == "__main__":
    # Run examples
    print("\n" + "🚀 RESEARCH AGENT EXAMPLES" + "\n")
    
    # Uncomment the example you want to run:
    
    # Example 1: Basic research
    example_basic_research()
    
    # Example 2: Multiple queries
    # example_multiple_queries()
    
    # Example 3: Custom agent
    # example_custom_agent()
