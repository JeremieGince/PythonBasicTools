def hash_dict(d: dict) -> str:
    """
    Hash a dictionary using the SHA256 algorithm.

    Args:
        d (dict): The dictionary to hash.

    Returns:
        str: The hash of the dictionary.
    """
    import hashlib
    import json

    return hashlib.sha256(json.dumps(d, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
