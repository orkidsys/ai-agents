"""
QA Tester Agent – Test design and automation support with workspace tools.

Uses LangChain to run an agent that can read/write files and list directories
in a workspace, proposing test strategies, designing test cases, and generating tests.
"""
import os
import json
import re
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from tools import get_qa_tools
from schemas import QATaskResponse

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


SYSTEM_PROMPT = """You are QA Tester, a senior QA engineer specializing in test planning,
test case design, and automation for web applications and APIs.

## Mindset
- Think in terms of risks, edge cases, and user impact.
- Prefer clear, reproducible steps and unambiguous results.
- Balance manual exploratory testing with automation where it adds the most value.

## Tools
You have access to:
- read_file: Read a file (path relative to workspace). Use this to inspect code and existing tests.
- write_file: Write or overwrite a file (path + content). Use this to create or update test files and fixtures.
- list_directory: List files and folders in a directory (path relative to workspace). Use this to understand project layout.

## Behavior
1. Start by understanding the feature under test from the user's description and relevant code (using list_directory/read_file).
2. Propose a concise test strategy: layers (unit/integration/e2e), types (functional, regression, negative, edge, happy path).
3. Design a focused set of high-value test cases with:
   - Clear titles
   - Preconditions
   - Steps
   - Expected results
4. When appropriate, generate or update automated test files (e.g. Jest/Vitest/Cypress/Playwright, pytest)
   that reflect the test cases, using modern best practices.
5. Keep tests maintainable and readable; avoid over-mocking or brittle selectors.
6. At the end, summarize what you did and call out recommended next steps (e.g. 'run npm test', add CI job).
"""


class QATesterAgent:
    """Agent that supports QA tasks in a workspace using read/write/list tools."""

    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.2,
        workspace_root: Optional[str] = None,
    ):
        """
        Initialize the QA Tester agent.

        Args:
            model_name: LLM model (e.g. "gpt-4", "gpt-4o-mini").
            temperature: Model temperature (lower = more deterministic).
            workspace_root: Root directory for file tools. Defaults to current working directory.
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.workspace_root = (
            workspace_root
            or os.environ.get("WORKSPACE_ROOT")
            or os.getcwd()
        )
        self.tools = get_qa_tools(workspace_root=self.workspace_root)
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT,
        )

    def test(
        self,
        request: str,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """
        Fulfill a QA testing request in the workspace.

        Args:
            request: Natural language request
                (e.g. "Analyze the login flow and design tests", "Add Jest tests for signup form").
            verbose: If True, print progress and final message.

        Returns:
            Dict with keys: question, response (messages + final content), structured_response (if parseable).
        """
        if verbose:
            print(f"Request: {request}")
            print(f"Workspace: {self.workspace_root}")
            print("=" * 60)

        try:
            result = self.agent.invoke({
                "messages": [HumanMessage(content=request)],
            })
            messages = result.get("messages", [])
            if not messages:
                raise ValueError("No messages returned from agent")

            final = messages[-1]
            content = final.content if hasattr(final, "content") else str(final)

            if verbose:
                print("Response:")
                print("-" * 60)
                print(content)
                print("=" * 60)

            structured = None
            try:
                structured = self._parse_structured(content)
            except Exception:
                # Parsing is best-effort; fall back to plain content.
                pass

            return {
                "question": request,
                "response": {
                    "messages": [str(m) for m in messages],
                    "content": content,
                },
                "structured_response": structured,
            }
        except Exception as e:
            if verbose:
                print(f"Error: {e}")
            raise

    def _parse_structured(self, content: str) -> Optional[QATaskResponse]:
        """Try to extract a QATaskResponse from the final message if JSON is present."""
        # Look for a JSON-like object in the content.
        json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", content, re.DOTALL)
        if not json_match:
            return None
        try:
            data = json.loads(json_match.group())
            # Basic heuristic: presence of task_summary indicates correct structure.
            if "task_summary" in data:
                return QATaskResponse(**data)
        except (json.JSONDecodeError, Exception):
            return None
        return None

    def print_result(self, result: Dict[str, Any]) -> None:
        """Pretty-print the result of test()."""
        print("\n" + "=" * 60)
        print("QA TESTER AGENT – RESULT")
        print("=" * 60)
        print(f"\nRequest: {result.get('question', '')}")
        print("\nResponse:")
        print("-" * 60)
        print(result.get("response", {}).get("content", ""))
        if result.get("structured_response"):
            s = result["structured_response"]
            if hasattr(s, "model_dump"):
                s = s.model_dump()
            print("\nStructured summary:")
            print(json.dumps(s, indent=2))
        print("=" * 60 + "\n")


def main():
    """Run the agent with an example QA request."""
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    agent = QATesterAgent(
        model_name="gpt-4",
        temperature=0.2,
        workspace_root=agent_dir,
    )
    example_request = (
        "Assume this workspace contains a web app. "
        "Design a concise test strategy and high-level test cases for the login flow. "
        "If appropriate, create a Jest test file at tests/login.spec.ts with at least a happy path test."
    )
    print("\nQA Tester Agent – Example run\n")
    result = agent.test(example_request, verbose=True)
    agent.print_result(result)


if __name__ == "__main__":
    main()

