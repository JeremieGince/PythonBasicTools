from typing import Sequence, Any, List, Union, Optional


def ravel_dict(d: dict, key_sep: str = ".") -> dict:
    """
    Ravel a dictionary into a single level dictionary.

    :param d: The dictionary to ravel.
    :type d: dict
    :param key_sep: The separator to use between keys in the raveled dictionary.
    :type key_sep: str
    :return: The raveled dictionary.
    :rtype: dict
    """
    raveled_dict = {}
    for k, v in d.items():
        if isinstance(v, dict):
            raveled_v = ravel_dict(v, key_sep)
            for k_, v_ in raveled_v.items():
                raveled_dict[f"{k}{key_sep}{k_}"] = v_
        else:
            raveled_dict[k] = v
    return raveled_dict


def sequence_get(sequence: Sequence, idx: int, default: Any = None) -> Any:
    """
    Get an item from a sequence at a specific index. If the index is out of bounds, return a default value.

    :param sequence: The sequence to get the item from.
    :type sequence: Sequence
    :param idx: The index to get the item from.
    :type idx: int
    :param default: The default value to return if the index is out of bounds.
    :type default: Any

    :return: The item at the index or the default value.
    :rtype: Any
    """
    try:
        return sequence[idx]
    except IndexError:
        return default


def list_insert_replace_at(__list: List, idx: int, value: Any, default: Any = None) -> List:
    """
    Insert a value at a specific index.
    If there is already a value at this index, replace it.

    :param __list: The list to modify.
    :type __list: List
    :param idx: The index to insert the value.
    :type idx: int
    :param value: The value to insert.
    :type value: Any
    :param default: The default value to insert if the index is out of bounds.
    :type default: Any

    :return: The new list.
    :rtype: List
    """
    if idx < 0:
        idx = max(0, len(__list) + idx)
    if idx < len(__list):
        __list[idx] = value
    else:
        __list.extend([default] * (idx - len(__list)))
        __list.append(value)
    return __list


def unpack_singleton_dict(x: dict, default: Any = None) -> Optional[Any]:
    """
    Unpack a dictionary with a single key and value. If the dict has more than one key, a ValueError is raised.
    If the dict is empty, the default value is returned.

    :param x: The dictionary to unpack.
    :type x: dict
    :param default: The default value to return if the dictionary is empty.
    :type default: Any

    :return: The value of the single key in the dictionary.
    :rtype: Any
    """
    if len(x) > 1:
        raise ValueError("x must have a length of zero or one.")
    elif len(x) == 0:
        return default
    return x[list(x.keys())[0]]


def maybe_unpack_singleton_dict(x: Union[dict, Any], default: Any = None) -> Any:
    """
    Accept a dict or any other type. If x is a dict with one key and value, the singleton is unpacked. Otherwise, x is
    returned without being changed.

    :param x: The value to unpack to maybe unpack.
    :type x: Union[dict, Any]
    :param default: The default value to return if the dictionary is empty.
    :type default: Any

    :return: The unpacked value or the original value.
    :rtype: Any
    """
    if isinstance(x, dict) and len(x) <= 1:
        return unpack_singleton_dict(x, default=default)
    return x
