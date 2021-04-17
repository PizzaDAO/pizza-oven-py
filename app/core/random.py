from typing import Optional, TypeVar
from secrets import randbits
from hashlib import sha256

__all__ = [
    "get_random_remote",
    "get_random",
    "get_random_deterministic",
    "get_optional",
    "clamp",
    "to_hex",
    "from_hex",
]

_T = TypeVar("_T")


def get_random_remote() -> int:
    """call a remote function to get a random number"""

    # TODO: call chainlink oracle pointed to matic
    return get_random()


def get_random(bits: int = 256) -> int:
    """A naive implementation of a random mumber"""
    return randbits(bits)


def get_random_deterministic(
    entropy: int,
    nonce: int,
    personalization: Optional[str] = None,
    extra: Optional[int] = None,
) -> int:
    """a naive deterministic random generator using sha2"""

    # TODO: a real implementation of a DRBG

    sha2Hash = sha256()
    sha2Hash.update("|".encode("utf-8"))
    sha2Hash.update((str(entropy) + "|").encode("utf-8"))
    sha2Hash.update("|".encode("utf-8"))
    sha2Hash.update((str(nonce) + "|").encode("utf-8"))
    sha2Hash.update("|".encode("utf-8"))
    if personalization is not None:
        sha2Hash.update((get_optional(personalization) + "|").encode("utf-8"))
        sha2Hash.update("|".encode("utf-8"))
    if extra is not None:
        sha2Hash.update((str(get_optional(extra)) + "|").encode("utf-8"))
        sha2Hash.update("|".encode("utf-8"))

    return int.from_bytes(sha2Hash.digest(), byteorder="big")


def get_optional(optional: Optional[_T]) -> _T:
    """
    General-purpose unwrapping function to handle `Optional`.
    """
    assert optional is not None, "Unwrap called on None"
    return optional


def clamp(entropy: int, start: float, end: float) -> float:
    """naive implementation of a range bound"""

    if end == 0.0:
        return 0.0
    modulo = float(entropy) % end
    if modulo < start:
        return start
    return modulo


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
