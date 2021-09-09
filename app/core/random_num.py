from typing import Optional, TypeVar, Tuple
from secrets import randbits
from hashlib import sha256

from app.core.utils import get_optional, clamp

__all__ = [
    "Counter",
    "get_random_remote",
    "get_random",
    "get_random_deterministic_uint256",
    "get_random_deterministic_float",
    "select_value",
]

_T = TypeVar("_T")

MAX_UINT256 = 2 ^ 256 - 1


class Counter:
    def __init__(self, seed: int = 0) -> None:
        self.nonce = seed

    def current(self) -> int:
        return self.nonce

    def next(self) -> int:
        self.nonce += 1
        return self.nonce


def get_random_remote() -> int:
    """call a remote function to get a random number"""

    # TODO: call chainlink oracle pointed to matic
    return get_random()


def get_random(bits: int = 256) -> int:
    """A naive implementation of a random mumber"""
    return randbits(bits)


def get_random_deterministic_uint256(
    entropy: int,
    nonce: Counter,
    personalization: Optional[str] = None,
    extra: Optional[int] = None,
) -> int:
    """a naive deterministic random generator using sha2 without any bit masking"""

    # TODO: a real implementation of a DRBG

    sha2Hash = sha256()
    sha2Hash.update("|".encode("utf-8"))
    sha2Hash.update((str(entropy) + "|").encode("utf-8"))
    sha2Hash.update("|".encode("utf-8"))
    sha2Hash.update((str(nonce.next()) + "|").encode("utf-8"))
    sha2Hash.update("|".encode("utf-8"))
    if personalization is not None:
        sha2Hash.update((get_optional(personalization) + "|").encode("utf-8"))
        sha2Hash.update("|".encode("utf-8"))
    if extra is not None:
        sha2Hash.update((str(get_optional(extra)) + "|").encode("utf-8"))
        sha2Hash.update("|".encode("utf-8"))

    return int.from_bytes(sha2Hash.digest(), byteorder="big")


def get_random_deterministic_float(
    entropy: int,
    nonce: Counter,
    personalization: Optional[str] = None,
    extra: Optional[int] = None,
) -> float:
    """a deterministic rbg bit masked to 2^256 - 1 and normalized to [0, 1.0)"""
    deterministic = get_random_deterministic_uint256(
        entropy, nonce, personalization, extra
    )

    if deterministic > MAX_UINT256:
        return deterministic % MAX_UINT256 / MAX_UINT256

    return deterministic / MAX_UINT256


def select_value(seed: int, nonce: Counter, bounds: Tuple[float, float]) -> float:
    return clamp(get_random_deterministic_float(seed, nonce), bounds[0], bounds[1])
