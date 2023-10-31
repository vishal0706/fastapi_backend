import hashlib
from typing import Optional


def sha256(text: Optional[str]):
    """
    Computes the SHA256 digest of the given string.

    Args:
        text (str): The string to be hashed.

    Returns:
        The SHA256 digest of the input text string as a hexadecimal string.
    """
    text = hashlib.sha256(text.encode())
    return text.hexdigest()


def sha1(text: Optional[str]):
    """
    Calculates the SHA-1 digest of the given text string.
    Args:
        text (str): The string to be hashed.
    Returns:
        str: The SHA-1 digest of the input text string as a hexadecimal string.
    """
    text = hashlib.sha1(text.encode())
    return text.hexdigest()


def sha512(text: Optional[str]):
    """
    Calculates the SHA-512 digest of the given text.

    Args:
        text: (str) The string to be hashed.

    Returns:
        str: The SHA512 digest of the input text string as a hexadecimal string.
    """
    text = hashlib.sha512(text.encode())
    return text.hexdigest()
