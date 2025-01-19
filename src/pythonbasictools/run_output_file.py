import datetime
import logging
import os
from collections import defaultdict
from typing import Dict, Any

import pandas as pd


class RunOutputFile:
    """

    This object is used to save and load data of a script run to a JSON file. The data is saved as a dictionary and can
    be accessed as an attribute of the object. The data is saved to a JSON file in the output directory of the script.
    It is useful when you want to store some data or state of the script run to a file and load it later.

    Example:

        ```python
        from run_output_file import RunOutputFile

        output = RunOutputFile("output_dir", save_every_set=True)
        output_file.update({"status": "STARTING"})
        print("Doing some work...")
        work = 1 + 1
        output_file.update({"status": "WORKING", "work": work})
        print("Doing some other stuff...")
        stuff = 2 + 2
        output_file.update({"status": "WORKING", "stuff": stuff})
        print("Done working.")
        output_file.update({"status": "DONE"})
        ```

    :param output_dir: The directory where the output file will be saved.
    :type output_dir: str
    :param filename: The name of the output file. Default is "run_output".
    :type filename: str
    :param data: The initial data to be saved to the output file.
    :type data: dict
    :param save_every_set: If True, the data will be saved to the output file every time an item is added or updated.
    :type save_every_set: bool
    :param kwargs: Additional keyword arguments
    """
    EXT: str = ".out.json"
    DEFAULT_FILENAME: str = "run_output"

    def __init__(
            self,
            output_dir: str,
            filename: str = DEFAULT_FILENAME,
            data: dict = None,
            save_every_set: bool = True,
            **kwargs
    ):
        self.output_dir = output_dir
        self.filename = filename
        self.save_every_set = save_every_set
        self.data = {}
        self.logs = defaultdict(list)
        self.load_if_exists()
        if data is not None:
            self.data.update(data)
        self.save_if_save_every_set()
        self.kwargs = kwargs

    @property
    def path(self):
        return os.path.join(self.output_dir, self.filename + self.EXT)

    @property
    def exists(self):
        return os.path.exists(self.path)

    @classmethod
    def from_file(cls, path: str, **kwargs):
        output_dir, filename = os.path.split(path)
        filename = filename.replace(cls.EXT, "")
        return cls(output_dir, filename, **kwargs)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save_if_save_every_set()

    def __delitem__(self, key):
        del self.data[key]
        self.save_if_save_every_set()

    def get(self, key, default=None):
        return self.data.get(key, default)

    def __contains__(self, key):
        return key in self.data

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __add__(self, other):
        self.data.update(other)
        self.save_if_save_every_set()
        return self

    def __sub__(self, other):
        for key in other:
            self.data.pop(key, None)
        self.save_if_save_every_set()
        return self

    def __repr__(self):
        """
        Return a string representation of the dict as a JSON string with indentation and save path.
        """
        import json

        _str = json.dumps(self.data, indent=4)
        _str += f"\n\nSaved to: {self.path}"
        return _str

    def update(self, other):
        self.data.update(other)
        self.save_if_save_every_set()
        return self

    def save_if_save_every_set(self):
        if self.save_every_set:
            self.save()
        return self

    def __getstate__(self):
        return {
            "datetime": str(datetime.datetime.now()),
            "data": self.data,
            "logs": self.logs,
            f"path": self.path,
        }

    def __setstate__(self, state: Dict[str, Any]):
        self.data.update(state.get("data", {}))
        self.logs.update(state.get("logs", {}))
        return self

    def save(self):
        import json
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
        save_data = self.__getstate__()
        with open(self.path, "w") as f:
            json.dump(save_data, f, indent=4)
        return self

    def load(self):
        import json

        with open(self.path, "r") as f:
            saved_data = json.load(f)

        if "data" not in saved_data or "logs" not in saved_data:
            return self.legacy_load()

        self.__setstate__(saved_data)
        return self

    def legacy_load(self):
        import json

        with open(self.path, "r") as f:
            self.data.update(json.load(f))
        return self

    def load_if_exists(self):
        if self.exists:
            self.load()
        return self

    def as_dataframe(self, add_path: bool = True) -> pd.DataFrame:
        data = self.data.copy()
        if add_path:
            data[f"{self.EXT}_path"] = self.path
        return pd.DataFrame([data])

    def as_series(self, add_path: bool = True) -> pd.Series:
        data = self.data.copy()
        if add_path:
            data[f"{self.EXT}_path"] = self.path
        return pd.Series(data)

    def log(self, msg: str, level=logging.INFO, print_msg: bool = True, **kwargs):
        import warnings
        msg = str(msg)
        self.logs[level].append(msg)
        if print_msg:
            if level == logging.INFO:
                print(msg)
            elif level == logging.WARNING:
                warnings.warn(msg)
            elif level == logging.ERROR:
                warnings.warn(msg, UserWarning)
            else:
                print(f"[{level}] {msg}")
        self.save_if_save_every_set()
        return self

    def print_logs(self, level=logging.INFO, sep: str = "\n"):
        full_str = sep.join(self.logs[level])
        print(full_str)
        return self
