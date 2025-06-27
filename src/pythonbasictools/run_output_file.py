import datetime
import json
import logging
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional

import pandas as pd

from .collections_tools import ravel_dict
from .multiprocessing_tools import apply_func_multiprocess


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
    RAVEL_DICT_KEY_SEP = "."  # The separator used to ravel the dictionary

    @classmethod
    def parse_results_from_dir_to_dataframe(
        cls,
        root_dir: str,
        requires_columns: Optional[List[str]] = None,
        file_column: str = "_file",
        mp_kwargs: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """
        Parse the results from a root directory. If requires_columns is not None, the rows that do not contain all the
        required columns will be removed.

        :param root_dir: The directory containing the results.
        :type root_dir: str
        :param requires_columns: The columns that are required in the DataFrame. If None, no columns are required.
            If a row does not contain all the required columns, it will be removed from the final DataFrame.
        :type requires_columns: Optional[List[str]]
        :param file_column: The name of the column that contains the file path.
        :type file_column: str
        :param mp_kwargs: The keyword arguments to pass to the multiprocessing function.
        :type mp_kwargs: Optional[Dict[str, Any]]
        :return: The DataFrame containing the results.
        """
        if mp_kwargs is None:
            mp_kwargs = {}
        all_files = [
            os.path.join(root, file) for root, _, files in os.walk(root_dir) for file in files if file.endswith(cls.EXT)
        ]
        results = apply_func_multiprocess(
            func=cls.raveled_state_from_file,
            iterable_of_args=[(file, False) for file in all_files],
            iterable_of_kwargs=[{"save_every_set": False, file_column: file} for file in all_files],
            desc=f"Processing files '{cls.EXT}' in {os.path.abspath(root_dir)}",
            **mp_kwargs,
        )
        df = pd.DataFrame(results)
        if requires_columns is not None:
            df = df.dropna(subset=requires_columns)
        return df

    @classmethod
    def raveled_state_from_file(cls, path: str, raise_on_error: bool = False, **kwargs) -> dict:
        """
        Get the raveled state of the data in the file.

        :param path: The path to the file.
        :type path: str
        :param raise_on_error: If True, raise an error if an error occurs while loading the file.
            If False, return an empty dictionary if an error occurs.
        :type raise_on_error: bool
        :param kwargs: Additional keyword arguments.
        :return: The raveled state of the data in the file.
        :rtype: dict
        """
        try:
            return cls.from_file(path, **kwargs).raveled_state
        except Exception as e:
            if raise_on_error:
                raise e
            return {}

    def __init__(
        self,
        output_dir: str,
        filename: str = DEFAULT_FILENAME,
        data: Optional[dict] = None,
        save_every_set: bool = True,
        **kwargs,
    ):
        self.output_dir = output_dir
        self.filename = filename
        self.save_every_set = save_every_set
        self.data = {}
        self.logs: Dict[str, list] = defaultdict(list)
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

    @property
    def raveled_state(self):
        return self.get_raveled_state()

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

    def update(
        self,
        other: Dict[str, Any],
        print_updated: bool = True,
        print_header: str = "New Data",
    ):
        self.data.update(other)
        self.save_if_save_every_set()
        if print_updated:
            print(f"{print_header}:\n{json.dumps(other, indent=4, default=str)}\n")
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
            "ENV": dict(os.environ),
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
            try:
                self.load()
            except (json.JSONDecodeError, FileNotFoundError):
                pass
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

    def get_raveled_state(self, key_sep: Optional[str] = None):
        if key_sep is None:
            key_sep = self.RAVEL_DICT_KEY_SEP
        raveled_state = self.data.copy()
        return ravel_dict(raveled_state, key_sep=key_sep)

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
