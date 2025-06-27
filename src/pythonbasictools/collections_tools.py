import itertools
from typing import Any, Dict, List, Optional, Sequence, Union


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


def list_of_dicts_to_dict_of_lists(list_of_dicts: List[dict], default: Any = None) -> dict:
    """
    Convert a list of dictionaries to a dictionary of lists.
    The keys of the dictionaries are used as keys in the dictionary of lists.
    The values of the dictionaries are inserted into the lists at the same index as the dictionary.
    This means that every list in the dictionary of lists will have the same length as the list of dictionaries.

    :param list_of_dicts: The list of dictionaries to convert.
    :type list_of_dicts: List[dict]
    :param default: The default value to insert if a key is not present in a dictionary.
    :type default: Any

    :return: The dictionary of lists.
    :rtype: dict
    """
    dict_of_lists: Dict[str, List[Any]] = {}
    for i, d in enumerate(list_of_dicts):
        for k, v in d.items():
            dict_of_lists[k] = list_insert_replace_at(dict_of_lists.get(k, []), i, v, default=default)
    return dict_of_lists


def dict_of_lists_to_list_of_dicts(dict_of_lists: Dict) -> List[dict]:
    """
    Convert a dictionary of lists to a list of dictionaries.
    The keys of the dictionary are used as keys in the dictionaries.
    The values of the dictionary are inserted into the dictionaries at the same index as the list.

    :Example:
        >>> dict_of_lists = {
        ...    "a": [1, 2, 3],
        ...    "b": [9, 8, 7],
        ...    "c": [True, False, True],
        ...}
        >>> list_of_dicts = dict_of_lists_to_list_of_dicts(dict_of_lists)
        >>> print(list_of_dicts)
        [{'a': 1, 'b': 9, 'c': True}, {'a': 2, 'b': 8, 'c': False}, {'a': 3, 'b': 7, 'c': True}]

    :Note:
        If the lists in the dictionary have different lengths, the last directories will have less keys than the
        first ones.

    :param dict_of_lists: The dictionary of lists to convert.
    :type dict_of_lists: dict

    :return: The list of dictionaries.
    :rtype: List[dict]
    """
    keys = list(dict_of_lists.keys())
    list_of_dict_of_parameters: List[dict] = []
    for key in keys:
        values = dict_of_lists[key]
        for i, value in enumerate(values):
            old_dict = sequence_get(list_of_dict_of_parameters, idx=i, default={})
            new_dict = {**old_dict, key: value}
            list_insert_replace_at(list_of_dict_of_parameters, i, new_dict, default={})
    return list_of_dict_of_parameters


def dict_of_lists_to_product_list_of_dicts(dict_of_lists: Dict) -> List[dict]:
    """
    Convert a dictionary of lists to a list of dictionaries as the Cartesian product of the lists.

    :Example:
        >>> dict_of_lists = {
        ...    "a": [1, 2],
        ...    "b": [9, 8],
        ...}
        >>> list_of_dicts = dict_of_lists_to_product_dict_of_lists(dict_of_lists)
        >>> print(list_of_dicts)
        [{'a': 1, 'b': 9}, {'a': 1, 'b': 8}, {'a': 2, 'b': 9}, {'a': 2, 'b': 8}]

    :param dict_of_lists: The dictionary of lists to convert.
    :type dict_of_lists: dict

    :return: The list of dictionaries.
    :rtype: List[dict]
    """
    keys = list(dict_of_lists.keys())
    list_of_dict_of_parameters = [
        dict(zip(keys, values)) for values in itertools.product(*[dict_of_lists[key] for key in keys])
    ]
    return list_of_dict_of_parameters
