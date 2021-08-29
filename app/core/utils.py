from typing import Optional, TypeVar

_T = TypeVar("_T")

__all__ = [
    "get_optional",
    "clamp",
    "to_hex",
    "from_hex",
]


def get_optional(optional: Optional[_T]) -> _T:
    """
    General-purpose unwrapping function to handle `Optional`.
    """
    assert optional is not None, "Unwrap called on None"
    return optional


def get_or_else_optional(optional: Optional[_T], alt_value: _T) -> _T:
    """
    General-purpose getter for `Optional`.
    If it's `None`, returns the `alt_value`.
    Otherwise, returns the contents of `optional`.
    """
    if optional is None:
        return alt_value
    return optional


def clamp(entropy: float, start: float, end: float) -> float:
    """
    naive implementation of a range bound.
    expects entropy to be a 256 bit unsigned integer
    """
    return start + (end - start) * entropy


def to_hex(base_10: int) -> str:
    """convert the int to hex format"""
    in_hex = format(base_10, "02X")
    if len(in_hex) % 2:
        in_hex = "0" + in_hex
    return in_hex


def from_hex(in_hex: str) -> int:
    """convert the hext to int format"""
    base_10 = int(in_hex, 16)
    return base_10