# Move Contract Validator Agent

Multi-agent **Move** review for **Aptos**-style and **Sui**-style modules. Four specialists run in parallel (each is an LLM call with a focused system prompt):

| Specialist   | Focus |
|-------------|--------|
| **security** | Resources, `signer` / capabilities, token safety, cross-module trust |
| **logic**    | Invariants, abort conditions, edge cases |
| **gas**      | Storage, hot paths, tables/collections |
| **compliance** | Docs, errors, framework idioms, module layout |

Results merge into one `MoveValidationReport` with deduplicated findings and overall risk.

**Disclaimer:** This is LLM-assisted static review. It does **not** replace the Move compiler, formal verification, or a professional security audit.

## Setup

```bash
cd "move contract validator agent"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env-example .env
# Set OPENAI_API_KEY
```

## Usage

**Python — full multi-agent validation**

```python
import sys, os
sys.path.insert(0, "/path/to/move contract validator agent")
from main import MoveContractValidator

v = MoveContractValidator(model_name="gpt-4o")
report = v.validate(file_path="uploads/my_module.move", verbose=True)
v.print_report(report)
```

Or pass `source_code=` instead of `file_path`.

**CLI**

```bash
python main.py                    # inline Aptos-like example
python main.py uploads/foo.move   # or path to your .move file
```

JSON report is written to `move_validation_report.json` when using CLI with a file path.

**Orchestrator mode** (model chooses tool sequence — useful for multi-step workflows):

```python
out = v.validate_with_orchestrator(
    "Read uploads/token.move and run full validation.",
    file_path="uploads/token.move",
)
print(out["response"])
```

## Layout

```
move contract validator agent/
├── main.py                 # MoveContractValidator
├── schemas.py
├── tools.py                # read_move_file + specialist tools
├── agents/
│   ├── security_agent.py
│   ├── logic_agent.py
│   ├── gas_agent.py
│   ├── compliance_agent.py
│   └── base_parse.py
├── uploads/                # drop .move files here for short paths
├── example.py
├── requirements.txt
└── .env-example
```

## License

MIT (same spirit as other agents in this repo).
