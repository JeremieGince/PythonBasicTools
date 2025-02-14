from typing import Sequence, Any, List


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
    if idx < len(__list):
        __list[idx] = value
    else:
        __list.extend([default] * (idx - len(__list)))
        __list.append(value)
    return __list

