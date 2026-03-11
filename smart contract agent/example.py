"""
Example usage of the Smart Contract Auditing Agent.

Demonstrates:
- Auditing by file path (uploaded or local file)
- Auditing raw source code
- Optional orchestrator mode
"""
import os
from main import SmartContractAuditor

# Base directory for paths
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS = os.path.join(AGENT_DIR, "uploads")


def example_inline_source():
    """Audit a small Solidity snippet passed as string."""
    print("=" * 70)
    print("EXAMPLE 1: Audit inline source code")
    print("=" * 70)

    auditor = SmartContractAuditor(model_name="gpt-4", temperature=0.2)

    source = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleToken {
    mapping(address => uint256) public balanceOf;

    function transfer(address to, uint256 amount) external {
        require(balanceOf[msg.sender] >= amount);
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
    }
}
"""
    report = auditor.audit(source_code=source, verbose=True)
    auditor.print_report(report)
    return report


def example_file_path():
    """Audit a contract file (e.g. from uploads/)."""
    print("=" * 70)
    print("EXAMPLE 2: Audit by file path")
    print("=" * 70)

    # Example: create a sample file in uploads if none exists
    sample_path = os.path.join(UPLOADS, "Sample.sol")
    if not os.path.isfile(sample_path):
        os.makedirs(UPLOADS, exist_ok=True)
        with open(sample_path, "w") as f:
            f.write("""
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Sample {
    uint256 public value;
    function set(uint256 v) external { value = v; }
}
""")
        print(f"Created sample file: {sample_path}")

    auditor = SmartContractAuditor()
    report = auditor.audit(file_path=sample_path, verbose=True)
    auditor.print_report(report)
    return report


def example_orchestrator():
    """Use orchestrator LLM to run tools (read file + all audits)."""
    print("=" * 70)
    print("EXAMPLE 3: Orchestrator mode (LLM-driven tools)")
    print("=" * 70)

    auditor = SmartContractAuditor()
    sample_path = os.path.join(UPLOADS, "Sample.sol")
    if not os.path.isfile(sample_path):
        print("Run example_file_path() first to create Sample.sol, or pass another path.")
        return None

    result = auditor.audit_with_orchestrator(
        f"Audit the smart contract at {sample_path}. Run all four specialist audits and give a short summary.",
        verbose=True,
    )
    print(result["response"])
    return result


if __name__ == "__main__":
    example_inline_source()
    print()
    example_file_path()
    # Uncomment to run orchestrator (more API calls):
    # example_orchestrator()
