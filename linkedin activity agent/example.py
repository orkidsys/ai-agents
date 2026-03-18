"""
Example usage of the LinkedIn Activity Agent.

This script demonstrates various capabilities of the agent including:
- Generating LinkedIn posts
- Analyzing feed for engagement opportunities
- Creating content strategies
- Generating thoughtful comments
"""
from main import LinkedInActivityAgent


def example_generate_post():
    """Example: Generate a LinkedIn post."""
    print("\n" + "=" * 70)
    print("📝 EXAMPLE: Generate LinkedIn Post")
    print("=" * 70)
    
    agent = LinkedInActivityAgent(model_name="gpt-4", temperature=0.7)
    
    result = agent.generate_post(
        topic="the future of remote work",
        tone="thought_leader",
        include_hashtags=True,
        verbose=True
    )
    
    agent.print_response(result)
    return result


def example_analyze_feed():
    """Example: Analyze LinkedIn feed for engagement."""
    print("\n" + "=" * 70)
    print("🔍 EXAMPLE: Analyze Feed for Engagement")
    print("=" * 70)
    
    agent = LinkedInActivityAgent(model_name="gpt-4", temperature=0.5)
    
    result = agent.analyze_feed(
        topics=["artificial intelligence", "leadership", "career development"],
        limit=15,
        verbose=True
    )
    
    agent.print_response(result)
    return result


def example_content_strategy():
    """Example: Create a content strategy."""
    print("\n" + "=" * 70)
    print("📊 EXAMPLE: Create Content Strategy")
    print("=" * 70)
    
    agent = LinkedInActivityAgent(model_name="gpt-4", temperature=0.6)
    
    result = agent.create_content_strategy(
        profile_url="https://www.linkedin.com/in/example-profile",
        goals=[
            "establish thought leadership in AI",
            "grow follower base to 10,000",
            "generate leads for consulting services"
        ],
        industry="Technology / Artificial Intelligence",
        verbose=True
    )
    
    agent.print_response(result)
    return result


def example_generate_comments():
    """Example: Generate comments for engagement."""
    print("\n" + "=" * 70)
    print("💬 EXAMPLE: Generate Engagement Comments")
    print("=" * 70)
    
    agent = LinkedInActivityAgent(model_name="gpt-4", temperature=0.7)
    
    result = agent.generate_comments(
        topics=["startup funding", "product management", "tech leadership"],
        count=5,
        verbose=True
    )
    
    agent.print_response(result)
    return result


def example_custom_query():
    """Example: Custom query to the agent."""
    print("\n" + "=" * 70)
    print("🎯 EXAMPLE: Custom Query")
    print("=" * 70)
    
    agent = LinkedInActivityAgent(model_name="gpt-4", temperature=0.7)
    
    result = agent.run(
        query="""I'm a software engineer looking to transition into a product management role. 
        Help me create a LinkedIn presence that showcases my technical background while 
        demonstrating product thinking. What kind of content should I post, and how should 
        I engage with the PM community on LinkedIn?""",
        topics=["product management", "software engineering", "career transition"],
        verbose=True
    )
    
    agent.print_response(result)
    return result


def example_profile_analysis():
    """Example: Analyze a LinkedIn profile."""
    print("\n" + "=" * 70)
    print("👤 EXAMPLE: Profile Analysis")
    print("=" * 70)
    
    agent = LinkedInActivityAgent(model_name="gpt-4", temperature=0.5)
    
    result = agent.run(
        query="""Analyze this LinkedIn profile and provide recommendations for improvement. 
        What content themes should they focus on? How can they increase engagement?""",
        profile_url="https://www.linkedin.com/in/example-tech-leader",
        verbose=True
    )
    
    agent.print_response(result)
    return result


def run_all_examples():
    """Run all examples sequentially."""
    print("\n" + "🚀 LINKEDIN ACTIVITY AGENT - EXAMPLES" + "\n")
    print("Running all demonstration examples...")
    print("=" * 70)
    
    examples = [
        ("Generate Post", example_generate_post),
        ("Analyze Feed", example_analyze_feed),
        ("Content Strategy", example_content_strategy),
        ("Generate Comments", example_generate_comments),
        ("Custom Query", example_custom_query),
        ("Profile Analysis", example_profile_analysis),
    ]
    
    results = {}
    
    for name, example_func in examples:
        print(f"\n{'='*70}")
        print(f"Running: {name}")
        print('='*70)
        
        try:
            results[name] = example_func()
            print(f"✅ {name} completed successfully")
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            import traceback
            traceback.print_exc()
            results[name] = {"error": str(e)}
    
    print("\n" + "=" * 70)
    print("📋 SUMMARY")
    print("=" * 70)
    for name, result in results.items():
        status = "✅ Success" if "error" not in result else f"❌ Failed: {result.get('error')}"
        print(f"  {name}: {status}")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_map = {
            "post": example_generate_post,
            "feed": example_analyze_feed,
            "strategy": example_content_strategy,
            "comments": example_generate_comments,
            "custom": example_custom_query,
            "profile": example_profile_analysis,
            "all": run_all_examples,
        }
        
        example_name = sys.argv[1].lower()
        if example_name in example_map:
            example_map[example_name]()
        else:
            print(f"Unknown example: {example_name}")
            print(f"Available examples: {', '.join(example_map.keys())}")
    else:
        print("LinkedIn Activity Agent Examples")
        print("-" * 40)
        print("Usage: python example.py [example_name]")
        print("")
        print("Available examples:")
        print("  post     - Generate a LinkedIn post")
        print("  feed     - Analyze feed for engagement")
        print("  strategy - Create content strategy")
        print("  comments - Generate engagement comments")
        print("  custom   - Custom query example")
        print("  profile  - Profile analysis")
        print("  all      - Run all examples")
        print("")
        print("Running default example (generate post)...")
        print("-" * 40)
        example_generate_post()
