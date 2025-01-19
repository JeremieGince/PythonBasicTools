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
