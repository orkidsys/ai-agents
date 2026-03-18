"""
Example usage of the Wallet Poisoning Agent.

Run from the agent directory:
  python example.py
"""
from main import WalletPoisoningAgent


def main():
    agent = WalletPoisoningAgent(model_name="gpt-4", temperature=0.3)

    # 1) Explain what wallet poisoning is
    print("Example 1: What is wallet poisoning?\n")
    result = agent.ask(
        "What is address poisoning in Web3 and how do I protect myself?",
        verbose=True,
    )
    agent.print_report(result)

    # 2) Compare two addresses (lookalike risk)
    print("\nExample 2: Compare two EVM addresses\n")
    trusted = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
    # Same first/last chars, different middle = typical poisoning pattern (40 hex chars)
    suspect = "0x742d35" + "a" * 30 + "d8b6"  # 40 hex chars; same start/end as trusted
    check = agent.check_address(trusted, suspect, verbose=True)
    if check.get("address_check_result"):
        print("Structured result:", check["address_check_result"])

    # 3) Validate an address format
    print("\nExample 3: Validate address format\n")
    from tools import validate_evm_address
    out = validate_evm_address.invoke({"address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"})
    print("Validation:", out)


if __name__ == "__main__":
    main()
