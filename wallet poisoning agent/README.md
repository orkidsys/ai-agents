# Wallet Poisoning Agent

An AI agent focused on **Web3 wallet (address) poisoning**: what it is, how to detect it, and how to protect yourself. The agent educates users and helps them verify destination addresses before sending funds.

## What is address poisoning?

**Address poisoning** (also called wallet poisoning or vanity-address scams) is a social-engineering attack in Web3:

1. Attackers generate an address that matches the **first and last characters** of a victim’s real address.
2. They send a tiny “dust” transfer from this fake address to the victim.
3. The victim’s transaction history then shows the fake address.
4. When the victim copies what they think is a known address, they may send funds to the attacker.

The agent does **not** help with attacks; it only helps with **education and defense**.

## Features

- **Education**: Explain address poisoning, common tactics, and best practices.
- **Address comparison**: Compare two EVM addresses to see if they are lookalikes (matching prefix/suffix).
- **Format validation**: Check that an address is a valid EVM (0x + 40 hex) format.
- **Structured output**: Optional `WalletPoisoningReport` and `AddressCheckResult` for integration.

## Installation

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env and set:
# OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### Ask about poisoning and protection

```python
from main import WalletPoisoningAgent

agent = WalletPoisoningAgent(model_name="gpt-4", temperature=0.3)

result = agent.ask(
    "What is wallet poisoning and how do I avoid sending to a poisoned address?",
    verbose=True,
)
agent.print_report(result)
```

### Compare two addresses (trusted vs destination)

```python
trusted = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
destination = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b7"

check = agent.check_address(trusted, destination, verbose=True)
# check["analysis"] has prefix_match_len, suffix_match_len, risk_note
# check["address_check_result"] is a structured AddressCheckResult when applicable
```

### Validate an address format

```python
from tools import validate_evm_address

result = validate_evm_address.invoke({"address": "0x..."})
print(result)
```

### Run the example

```bash
python example.py
```

## Project layout

- `main.py` – `WalletPoisoningAgent`, system prompt, and `ask` / `check_address` entrypoints.
- `tools.py` – `check_address_similarity`, `get_poisoning_facts`, `validate_evm_address`.
- `schemas.py` – `WalletPoisoningReport`, `AddressCheckResult`.
- `example.py` – Example flows.
- `.env.example` – Template for `OPENAI_API_KEY`.

## Security and disclaimer

- The agent is for **education and self-verification** only.
- It does not perform on-chain checks or guarantee that an address is safe; it only compares format and character similarity.
- Always verify addresses through trusted sources (official sites, verified contacts) before sending funds.
