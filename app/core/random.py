from typing import Optional, TypeVar
from secrets import randbits
from hashlib import sha256

_T = TypeVar("_T")


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