"""Example: validate a Move module with the multi-agent validator."""
import os
import sys

from dotenv import load_dotenv

_AGENT = os.path.dirname(os.path.abspath(__file__))
if _AGENT not in sys.path:
    sys.path.insert(0, _AGENT)

load_dotenv(dotenv_path=os.path.join(_AGENT, ".env"))

from main import MoveContractValidator


def example_inline() -> None:
    src = """
module 0xcafe::vault {
    use std::signer;

    struct Vault has key {
        balance: u64
    }

    public entry fun deposit(account: &signer, amount: u64) acquires Vault {
        let v = borrow_global_mut<Vault>(signer::address_of(account));
        v.balance = v.balance + amount;
    }
}
"""
    v = MoveContractValidator()
    r = v.validate(source_code=src, contract_name="vault.move", verbose=True)
    v.print_report(r)


if __name__ == "__main__":
    example_inline()
