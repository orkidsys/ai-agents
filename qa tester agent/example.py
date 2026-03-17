"""
Example usage of the QA Tester Agent.
"""
import os
from main import QATesterAgent


def example_design_login_tests():
    """Design high-level test cases for a login flow."""
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    agent = QATesterAgent(
        model_name="gpt-4",
        temperature=0.2,
        workspace_root=agent_dir,
    )
    result = agent.test(
        "Design high-level test scenarios and detailed test cases for a typical email/password login form, "
        "including happy path, validation errors, and lockout after repeated failures.",
        verbose=True,
    )
    agent.print_result(result)
    return result


def example_generate_jest_tests_for_login():
    """Ask the agent to generate a Jest test file for login."""
    project_path = os.path.dirname(os.path.abspath(__file__))
    agent = QATesterAgent(
        model_name="gpt-4",
        temperature=0.2,
        workspace_root=project_path,
    )
    result = agent.test(
        "In the 'tests' folder, create a Jest test file 'login.spec.ts' with a happy path test "
        "for a React login form component and at least one negative test for invalid credentials.",
        verbose=True,
    )
    agent.print_result(result)
    return result


def example_custom_workspace():
    """Run the QA agent against a custom application folder."""
    project_path = os.path.expanduser("~/my-web-app")
    if not os.path.isdir(project_path):
        print(f"Directory not found: {project_path}. Using current directory.")
        project_path = os.getcwd()

    agent = QATesterAgent(
        model_name="gpt-4",
        temperature=0.2,
        workspace_root=project_path,
    )
    result = agent.test(
        "List the src and tests directories (if they exist) and summarize what appears to be covered by tests.",
        verbose=True,
    )
    agent.print_result(result)
    return result


if __name__ == "__main__":
    print("\nQA Tester Agent – Examples\n")
    # Uncomment the example you want to run:
    example_design_login_tests()
    # example_generate_jest_tests_for_login()
    # example_custom_workspace()

