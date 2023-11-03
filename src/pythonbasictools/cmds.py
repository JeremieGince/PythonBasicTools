from typing import Dict


def get_cmd_kwargs(defaults: Dict = None):
    import sys
    import argparse

    if defaults is None:
        defaults = {}
    cmd_kwargs = {i: v for i, v in enumerate(sys.argv)}
    parser = argparse.ArgumentParser()
    for pos_arg in sorted([k for k in defaults.keys() if isinstance(k, int)]):
        if pos_arg in cmd_kwargs:
            parser.add_argument(f"argv_{pos_arg}", type=str, default=defaults[pos_arg])
    for k, v in defaults.items():
        if isinstance(k, int):
            cmd_kwargs[k] = cmd_kwargs.get(k, v)
        else:
            parser.add_argument(f"--{k}", type=type(v), default=v)
    args = parser.parse_args()
    cmd_kwargs.update(vars(args))
    return cmd_kwargs


