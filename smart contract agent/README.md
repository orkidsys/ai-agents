# Smart Contract Auditing Agent

Multi-agent smart contract auditor with **file upload support** and **intensive auditing** across four specialist agents: Security, Logic, Gas, and Compliance.

## Features

- **Multi-agent support**: Four specialist agents run in sequence for thorough coverage:
  - **Security**: Reentrancy, access control, overflow/underflow, unchecked calls, front-running, oracle manipulation
  - **Logic**: Invariants, edge cases, race conditions, upgradeability, integration assumptions
  - **Gas**: Storage/memory usage, loops, calldata, batching, contract size
  - **Compliance**: ERC-20/721/1155/4626 conformance, NatSpec, visibility, best practices
- **File upload**: Audit by **file path** (e.g. place contracts in `uploads/` and pass the path).
- **Intensive auditing**: Every run executes all four specialists and produces a merged, severity-sorted report with executive summary and recommendations.

## Setup

```bash
cd "smart contract agent"
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create a `.env` file with your OpenAI API key:

```
OPENAI_API_KEY=sk-...
```

## Usage

### 1. Audit by file path (e.g. uploaded file)

Place your contract in `uploads/` (or use any absolute path):

```bash
# Contract at uploads/Token.sol
python main.py Token.sol

# Or absolute path
python main.py /path/to/MyContract.sol
```

The report is printed to the terminal and saved as `audit_report.json` in the agent directory.

### 2. Audit from Python (file or raw source)

```python
from main import SmartContractAuditor

auditor = SmartContractAuditor(model_name="gpt-4", temperature=0.2)

# From file (e.g. after user upload)
report = auditor.audit(file_path="uploads/Token.sol", verbose=True)

# From raw source
report = auditor.audit(source_code="""
pragma solidity ^0.8.0;
contract MyContract { ... }
""", verbose=True)

auditor.print_report(report)
```

### 3. Orchestrator mode (LLM-driven tool use)

For free-form prompts where the model decides when to read files and run which audits:

```python
report = auditor.audit_with_orchestrator(
    "Audit the contract at uploads/Vault.sol and summarize the risks."
)
print(report["response"])
```

### 4. Example script

```bash
python example.py
```

This runs the built-in example (inline Solidity snippet and optional file).

## Project layout

```
smart contract agent/
├── main.py              # Orchestrator, CLI, and report synthesis
├── tools.py             # read_contract_file + specialist audit tools
├── schemas.py           # Finding, SpecialistReport, AuditReport
├── agents/
│   ├── security_agent.py
│   ├── logic_agent.py
│   ├── gas_agent.py
│   └── compliance_agent.py
├── uploads/             # Place contract files here for path-based audit
├── requirements.txt
├── example.py
└── README.md
```

## Output

- **AuditReport** includes:
  - `contract_name`, `audit_timestamp`
  - `specialist_reports`: one per agent (findings + summary + confidence)
  - `all_findings`: merged, deduplicated, sorted by severity
  - `executive_summary`, `risk_level`, `recommendations`

Findings use **Severity** (critical / high / medium / low / informational) and **Category** (e.g. reentrancy, access_control, gas_optimization, compliance_standards).

## Requirements

- Python 3.9+
- OpenAI API key
- Pydantic v2 (for `model_dump_json`)

This is for **assistive auditing** only; it does not replace a full professional audit or formal verification.
