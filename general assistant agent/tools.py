"""
Lightweight tools for the general assistant: time and safe arithmetic.
"""
from __future__ import annotations

import ast
import operator
from datetime import datetime, timezone
from typing import Any, Union
from zoneinfo import ZoneInfo, available_timezones

from langchain_core.tools import tool

# Safe numeric expression evaluation (no names, no calls, no attributes)
_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _eval_num(node: ast.AST) -> Union[int, float]:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        raise ValueError("only numbers allowed")
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval_num(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left = _eval_num(node.left)
        right = _eval_num(node.right)
        if type(node.op) in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
            raise ZeroDivisionError("division by zero")
        return _BIN_OPS[type(node.op)](left, right)
    raise ValueError("unsupported expression")


def safe_calculate_impl(expression: str) -> str:
    """Parse and evaluate a numeric expression with + - * / // % ** and parentheses."""
    expr = (expression or "").strip()
    if not expr:
        return "Error: empty expression"
    try:
        tree = ast.parse(expr, mode="eval")
        if not isinstance(tree, ast.Expression):
            return "Error: invalid parse"
        result = _eval_num(tree.body)
        return f"{result}"
    except ZeroDivisionError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error: {e}"


@tool
def get_current_time(timezone_name: str = "UTC") -> str:
    """Return the current date and time in ISO format for the given IANA timezone name.

    Use for scheduling, deadlines, or when the user asks what time it is.
    Examples of timezone_name: UTC, America/New_York, Europe/London, Asia/Tokyo.

    Args:
        timezone_name: IANA zone id (default UTC).
    """
    tz_name = (timezone_name or "UTC").strip() or "UTC"
    try:
        if tz_name.upper() == "UTC":
            tz: Any = timezone.utc
        else:
            if tz_name not in available_timezones():
                return (
                    f"Unknown timezone '{tz_name}'. Use an IANA name like "
                    "America/New_York or UTC."
                )
            tz = ZoneInfo(tz_name)
        now = datetime.now(tz)
        return now.isoformat(timespec="seconds")
    except Exception as e:
        return f"Error resolving time: {e}"


@tool
def safe_calculate(expression: str) -> str:
    """Evaluate a numeric arithmetic expression safely (no variables, no imports).

    Allowed: digits, + - * / // % ** parentheses. Example: (2 + 3) * 4

    Args:
        expression: Arithmetic string to evaluate.
    """
    return safe_calculate_impl(expression)


def get_general_assistant_tools():
    return [get_current_time, safe_calculate]
