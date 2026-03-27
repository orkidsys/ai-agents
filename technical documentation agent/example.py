"""
Example run for Technical Documentation Agent.
"""
import os

from dotenv import load_dotenv

from main import TechnicalDocumentationAgent

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def example_openai() -> None:
    agent = TechnicalDocumentationAgent(provider="openai", model_name="gpt-4o-mini")
    r = agent.chat(
        message=(
            "We need an API doc snippet: POST /v1/items creates an item. "
            "Body: name (string), tags (string[]). Returns 201 with id. Auth: Bearer."
        ),
        verbose=True,
    )
    agent.print_result(r)


if __name__ == "__main__":
    example_openai()
