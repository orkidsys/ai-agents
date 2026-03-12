"""
Example usage of the Frontend Developer Agent.
"""
import os
from main import FrontendDeveloperAgent


def example_create_component():
    """Create a simple React component in the agent workspace."""
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    agent = FrontendDeveloperAgent(
        model_name="gpt-4",
        temperature=0.3,
        workspace_root=agent_dir,
    )
    result = agent.implement(
        "Create a React component file at examples/Hello.jsx that renders an h1 saying 'Hello from Frontend Agent' and a paragraph. Use a function component.",
        verbose=True,
    )
    agent.print_result(result)
    return result


def example_custom_workspace():
    """Run the agent against a custom project path."""
    # Point to your own frontend project
    project_path = os.path.expanduser("~/my-react-app")
    if not os.path.isdir(project_path):
        print(f"Directory not found: {project_path}. Using current directory.")
        project_path = os.getcwd()

    agent = FrontendDeveloperAgent(
        model_name="gpt-4",
        temperature=0.3,
        workspace_root=project_path,
    )
    result = agent.implement(
        "List the project root directory and read package.json if it exists. Summarize the project (framework and scripts).",
        verbose=True,
    )
    agent.print_result(result)
    return result


def example_implement_feature():
    """Ask the agent to implement a small feature in the local examples folder."""
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    agent = FrontendDeveloperAgent(workspace_root=agent_dir)
    result = agent.implement(
        "In the 'examples' folder, add a Counter.jsx React component with a count state, "
        "a button that increments it, and a button that decrements it. Style the buttons with a simple CSS class in the same file or inline.",
        verbose=True,
    )
    agent.print_result(result)
    return result


if __name__ == "__main__":
    print("\nFrontend Developer Agent – Examples\n")
    # Uncomment the example you want to run:
    example_create_component()
    # example_custom_workspace()
    # example_implement_feature()
