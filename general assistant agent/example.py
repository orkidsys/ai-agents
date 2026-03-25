"""
Examples: General Assistant Agent with different LLM providers.

Set the matching API key in .env and install the optional package for that provider.
"""
import os

from dotenv import load_dotenv

from main import GeneralAssistantAgent

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def example_openai() -> None:
    agent = GeneralAssistantAgent(provider="openai", model_name="gpt-4o-mini")
    r = agent.chat(
        message="What is 144 / 12? Use the calculator tool.",
        verbose=True,
    )
    agent.print_result(r)


def example_anthropic() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Skip anthropic example: ANTHROPIC_API_KEY not set")
        return
    agent = GeneralAssistantAgent(provider="anthropic")
    r = agent.chat(message="What time is it in America/New_York? Use the time tool.")
    agent.print_result(r)


def example_google_gemini() -> None:
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
        print("Skip google example: GOOGLE_API_KEY / GEMINI_API_KEY not set")
        return
    agent = GeneralAssistantAgent(provider="google", model_name="gemini-2.0-flash")
    r = agent.chat(message="Briefly explain what a timezone is.")
    agent.print_result(r)


if __name__ == "__main__":
    print("Running OpenAI example (set OPENAI_API_KEY)...")
    example_openai()
    # example_anthropic()
    # example_google_gemini()
