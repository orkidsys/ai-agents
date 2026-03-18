"""
Tools for Web3 wallet poisoning detection and education.

Provides address similarity analysis (lookalike detection), validation,
and structured facts about address poisoning attacks.
"""
import re
from typing import Optional, Tuple
from langchain_core.tools import tool
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Address similarity (EVM 0x addresses)
# ---------------------------------------------------------------------------

def _normalize_evm_address(addr: str) -> Optional[str]:
    """Normalize EVM address to lowercase without 0x for comparison."""
    if not addr or len(addr) < 10:
        return None
    s = addr.strip()
    if s.startswith("0x") or s.startswith("0X"):
        s = s[2:]
    if len(s) != 40 or not re.match(r"^[0-9a-fA-F]{40}$", s):
        return None
    return s.lower()


def _similarity_analysis(addr1: str, addr2: str) -> dict:
    """
    Analyze two EVM addresses for lookalike (poisoning) risk.
    Poisoning often uses matching first and last N characters.
    """
    a = _normalize_evm_address(addr1)
    b = _normalize_evm_address(addr2)
    if not a or not b:
        return {
            "valid": False,
            "reason": "One or both addresses are not valid 40-char hex EVM addresses.",
            "prefix_match_len": 0,
            "suffix_match_len": 0,
            "identical": False,
            "risk_note": None,
        }
    if a == b:
        return {
            "valid": True,
            "reason": "Addresses are identical.",
            "prefix_match_len": 20,
            "suffix_match_len": 20,
            "identical": True,
            "risk_note": "Same address — no poisoning risk for this pair.",
        }
    prefix = 0
    for i in range(min(len(a), len(b))):
        if a[i] == b[i]:
            prefix += 1
        else:
            break
    suffix = 0
    for i in range(1, min(len(a), len(b)) + 1):
        if a[-i] == b[-i]:
            suffix += 1
        else:
            break
    # Heuristic: high prefix + suffix match with different middle = common poisoning pattern
    high_similarity = (prefix >= 4 and suffix >= 4) or (prefix >= 6 or suffix >= 6)
    risk_note = None
    if high_similarity:
        risk_note = (
            "High lookalike risk: first and/or last characters match. "
            "Always verify the FULL address before sending funds."
        )
    return {
        "valid": True,
        "reason": "Addresses are different.",
        "prefix_match_len": prefix,
        "suffix_match_len": suffix,
        "identical": False,
        "risk_note": risk_note,
    }


class AddressCheckInput(BaseModel):
    """Input for address similarity check."""
    address_known_or_trusted: str = Field(
        description="The address you believe is correct (e.g. from your contacts or a previous transfer)"
    )
    address_to_check: str = Field(
        description="The destination address you are about to send funds to (e.g. from copy-paste or history)"
    )


@tool(args_schema=AddressCheckInput)
def check_address_similarity(address_known_or_trusted: str, address_to_check: str) -> str:
    """
    Compare two EVM (0x) addresses for lookalike/poisoning risk.
    Use when you have a trusted address and want to verify a destination address
    is not a poisoned lookalike (matching first/last chars but different in the middle).
    """
    result = _similarity_analysis(address_known_or_trusted, address_to_check)
    lines = [
        f"Valid comparison: {result['valid']}.",
        result["reason"],
        f"Prefix matching characters: {result['prefix_match_len']}.",
        f"Suffix matching characters: {result['suffix_match_len']}.",
    ]
    if result.get("risk_note"):
        lines.append(f"Risk note: {result['risk_note']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Poisoning education / facts
# ---------------------------------------------------------------------------

POISONING_FACTS = """
Address poisoning (wallet poisoning) in Web3:

- What it is: A social engineering attack where attackers create addresses that look like a victim's real address (same first and last several characters) and send tiny "dust" transfers to the victim. The victim then sees this address in their history and may copy it by mistake when sending funds later.

- How it works:
  1. Attacker monitors on-chain transfers and picks a target address.
  2. They generate a "vanity" address that matches the start and end of the victim's address.
  3. They send a negligible (dust) transfer from the fake address to the victim.
  4. The victim's transaction history now shows the fake address. When they copy-paste what they think is their own or a known address, they may send to the attacker.

- Common tactics: Address spoofing (lookalike addresses), token spoofing (fake token names/symbols), dust transfers, and event spoofing.

- Defense: Always verify the FULL address before sending; do not rely on first/last characters. Use address book or verified contacts when possible. For large amounts, use a dedicated vault wallet and double-check on a second device or source.
"""


@tool
def get_poisoning_facts() -> str:
    """
    Returns concise, factual information about Web3 address (wallet) poisoning:
    what it is, how it works, common tactics, and how to defend.
    Use when the user asks what wallet poisoning is or how to protect themselves.
    """
    return POISONING_FACTS.strip()


# ---------------------------------------------------------------------------
# EVM address format validation
# ---------------------------------------------------------------------------

class ValidateAddressInput(BaseModel):
    """Input for address validation."""
    address: str = Field(description="An EVM address (0x followed by 40 hex characters)")


@tool(args_schema=ValidateAddressInput)
def validate_evm_address(address: str) -> str:
    """
    Validate an EVM address format (0x + 40 hex chars). Optionally check EIP-55 checksum.
    Does not check if the address is a known poisoner; use check_address_similarity for that.
    """
    s = address.strip()
    if not s.startswith("0x") and not s.startswith("0X"):
        return "Invalid: EVM addresses must start with 0x."
    body = s[2:]
    if len(body) != 40:
        return f"Invalid: expected 40 hex characters after 0x, got {len(body)}."
    if not re.match(r"^[0-9a-fA-F]{40}$", body):
        return "Invalid: address must contain only hexadecimal characters (0-9, a-f)."
    return "Valid EVM address format. Always verify the full address before sending funds."


# Export list for the agent
all_tools = [check_address_similarity, get_poisoning_facts, validate_evm_address]
