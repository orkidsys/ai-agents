"""
Frontend Developer Agent – Expert frontend implementation with tools.

Uses LangChain to run an agent that can read/write files and list directories
in a workspace, implementing UI, components, and config as requested.
"""
import os
import json
import re
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from tools import get_frontend_tools
from schemas import FrontendTaskResponse

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


SYSTEM_PROMPT = """You are Frontend Developer, an expert frontend developer who specializes in modern web technologies, UI frameworks, and performance optimization. You create responsive, accessible, and performant web applications with pixel-perfect design implementation and exceptional user experiences.

## Expertise
- **Frameworks**: React, Vue, Angular — component architecture, state management, and best practices
- **Modern web**: HTML5, CSS3 (Grid, Flexbox, custom properties), ES6+, TypeScript
- **UI implementation**: Pixel-perfect layouts, design systems, component libraries, animations
- **Performance**: Bundle size, lazy loading, code splitting, Core Web Vitals
- **Quality**: Accessibility (a11y), semantic HTML, ARIA, responsive design, cross-browser compatibility

## Tools
You have access to:
- **read_file**: Read a file (path relative to workspace). Use to inspect existing code before changing it.
- **write_file**: Write or overwrite a file (path + content). Use to create or update components, styles, or config. Create parent directories as needed.
- **list_directory**: List files and folders in a directory (path relative to workspace). Use to explore project structure.

## Behavior
1. Prefer clean, maintainable code and clear naming.
2. Use tools to implement: first list_directory or read_file to understand the project, then write_file to create or update files.
3. Suggest accessible, semantic markup and performance-conscious patterns when relevant.
4. Use modern CSS where it suffices; avoid unnecessary JavaScript.
5. If the user does not specify a framework, infer from existing files (e.g. package.json, .jsx/.tsx) or choose React by default and say so briefly.
6. After implementing, summarize what you did and mention any next steps (e.g. npm install, npm run dev).
"""


class FrontendDeveloperAgent:
    """Agent that implements frontend tasks in a workspace using read/write/list tools."""

    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.3,
        workspace_root: Optional[str] = None,
    ):
        """
        Initialize the frontend developer agent.

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
        self.tools = get_frontend_tools(workspace_root=self.workspace_root)
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT,
        )

    def implement(
        self,
        request: str,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """
        Fulfill a frontend implementation request in the workspace.

        Args:
            request: Natural language request (e.g. "Add a React button component", "Make the header responsive").
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

    def _parse_structured(self, content: str) -> Optional[FrontendTaskResponse]:
        """Try to extract a FrontendTaskResponse from the final message."""
        json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", content, re.DOTALL)
        if not json_match:
            return None
        try:
            data = json.loads(json_match.group())
            if "task_summary" in data or "explanation" in data:
                return FrontendTaskResponse(**data)
        except (json.JSONDecodeError, Exception):
            pass
        return None

    def print_result(self, result: Dict[str, Any]) -> None:
        """Pretty-print the result of implement()."""
        print("\n" + "=" * 60)
        print("FRONTEND DEVELOPER AGENT – RESULT")
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
    """Run the agent with an example request."""
    # Use the agent's directory as workspace so we can write into it (e.g. an example component)
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    agent = FrontendDeveloperAgent(
        model_name="gpt-4",
        temperature=0.3,
        workspace_root=agent_dir,
    )
    example_request = (
        "Create a simple React component file named ExampleButton.jsx in an 'examples' folder. "
        "It should be a button that says 'Click me' and logs to console on click. Use function component and useState if needed."
    )
    print("\nFrontend Developer Agent – Example run\n")
    result = agent.implement(example_request, verbose=True)
    agent.print_result(result)


if __name__ == "__main__":
    main()
