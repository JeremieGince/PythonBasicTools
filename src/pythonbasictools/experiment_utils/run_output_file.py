import datetime
import json
import logging
import os
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from ..collections_tools import ravel_dict
from ..multiprocessing_tools import apply_func_multiprocess


class RunOutputFile:
    """
    This object is used to save and load data of a script run to a JSON file. The data is saved as a dictionary and can
    be accessed as an attribute of the object. The data is saved to a JSON file in the output directory of the script.
    It is useful when you want to store some data or state of the script run to a file and load it later.

    Example:

        ```python
        from run_output_file import RunOutputFile

        output = RunOutputFile("output_dir")
        output.update({"status": "STARTING"})
        print("Doing some work...")
        work = 1 + 1
        output.update({"status": "WORKING", "work": work})
        print("Doing some other stuff...")
        stuff = 2 + 2
        output.update({"status": "WORKING", "stuff": stuff})
        print("Done working.")
        output.update({"status": "DONE"})
        output.freeze()  # Lock the file — no further changes allowed
        ```

    ENV is captured once at file creation and preserved across runs. Access it via ``get("ENV.key")``.

    Freeze state is persisted to disk: a file created with :meth:`freeze` will be loaded already frozen.
    Call :meth:`unfreeze` to allow changes again.

    :param output_dir: The directory where the output file will be saved.
    :type output_dir: Union[str, Path]
    :param filename: The name of the output file. Default is "run_output".
    :type filename: str
    :param data: The initial data to be saved to the output file.
    :type data: dict
    :param save_every_set: If True, the data will be saved every time an item is added or updated. Default is True.
    :type save_every_set: bool
    :param kwargs: Additional keyword arguments
    """

    EXT: str = ".out.json"
    DEFAULT_FILENAME: str = "run_output"
    RAVEL_DICT_KEY_SEP = "."  # The separator used to ravel the dictionary

    @classmethod
    def parse_results_from_dir_to_dataframe(
        cls,
        root_dir: Union[str, Path],
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
    def raveled_state_from_file(cls, path: Union[str, Path], raise_on_error: bool = False, **kwargs) -> dict:
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
        output_dir: Union[str, Path],
        filename: str = DEFAULT_FILENAME,
        data: Optional[dict] = None,
        save_every_set: bool = True,
        **kwargs,
    ):
        self.output_dir = Path(output_dir)
        self.filename = filename
        self.save_every_set = save_every_set
        self.data = {}
        self.logs: Dict[str, list] = defaultdict(list)
        self.env: Dict[str, str] = {}
        self._frozen: bool = False

        file_exists = self.exists
        self.load_if_exists()

        if not file_exists:
            # Capture ENV only once at file creation; preserved on subsequent loads
            self.env = dict(os.environ)

        if data is not None:
            self._check_not_frozen()
            self.data.update(data)

        self.save_if_save_every_set()
        self.kwargs = kwargs

    @property
    def path(self) -> Path:
        return self.output_dir / (self.filename + self.EXT)

    @property
    def exists(self) -> bool:
        return self.path.exists()

    @property
    def frozen(self) -> bool:
        return self._frozen

    @property
    def raveled_state(self):
        return self.get_raveled_state()

    @classmethod
    def from_file(cls, path: Union[str, Path], **kwargs):
        path = Path(path)
        output_dir = path.parent
        filename = path.name.replace(cls.EXT, "")
        return cls(output_dir, filename, **kwargs)

    def _check_not_frozen(self):
        if self._frozen:
            raise RuntimeError(f"RunOutputFile at '{self.path}' is frozen. Call unfreeze() to allow changes.")

    def freeze(self):
        """Lock this file: no data changes are allowed until :meth:`unfreeze` is called. Persisted to disk."""
        self._frozen = True
        self.save()
        return self

    def unfreeze(self):
        """Unlock this file and allow data changes again. Persisted to disk."""
        self._frozen = False
        self.save()
        return self

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self._check_not_frozen()
        self.data[key] = value
        self.save_if_save_every_set()

    def __delitem__(self, key):
        self._check_not_frozen()
        del self.data[key]
        self.save_if_save_every_set()

    def get(self, key, default=None):
        """
        Get a value by key. Looks in ``data`` first.

        Supports a ``"META_KEY.KEY"`` format to retrieve values from internal meta-dicts:

        - ``get("ENV.HOME")`` → value from the captured environment dict
        - ``get("logs.20")`` → value from the logs dict (key is the log level integer as string)

        :param key: The key to look up.
        :param default: The value to return if the key is not found.
        :return: The value associated with the key, or ``default``.
        """
        if key in self.data:
            return self.data[key]
        if self.RAVEL_DICT_KEY_SEP in key:
            meta_key, sub_key = key.split(self.RAVEL_DICT_KEY_SEP, 1)
            meta_dict = self._get_meta_dict(meta_key)
            if meta_dict is not None:
                return meta_dict.get(sub_key, default)
        return default

    def _get_meta_dict(self, meta_key: str) -> Optional[dict]:
        upper = meta_key.upper()
        if upper == "ENV":
            return self.env
        if upper in ("LOGS", "LOG"):
            return dict(self.logs)
        return None

    def __contains__(self, key):
        return key in self.data

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __add__(self, other):
        self._check_not_frozen()
        self.data.update(other)
        self.save_if_save_every_set()
        return self

    def __sub__(self, other):
        self._check_not_frozen()
        for key in other:
            self.data.pop(key, None)
        self.save_if_save_every_set()
        return self

    def __repr__(self):
        """
        Return a string representation of the dict as a JSON string with indentation and save path.
        """
        _str = json.dumps(self.data, indent=4)
        _str += f"\n\nSaved to: {self.path}"
        _str += f"\nFrozen: {self._frozen}"
        return _str

    def __fspath__(self):
        return os.fspath(self.path)

    def update(
        self,
        other: Dict[str, Any],
        print_updated: bool = True,
        print_header: str = "New Data",
    ):
        self._check_not_frozen()
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
            "path": str(self.path),
            "ENV": self.env,
            "frozen": self._frozen,
        }

    def __setstate__(self, state: Dict[str, Any]):
        self.data.update(state.get("data", {}))
        self.logs.update(state.get("logs", {}))
        self.env = state.get("ENV", {})
        self._frozen = state.get("frozen", False)
        return self

    def save(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        save_data = self.__getstate__()
        with open(self.path, "w") as f:
            json.dump(save_data, f, indent=4)
        return self

    def load(self):
        with open(self.path, "r") as f:
            saved_data = json.load(f)

        if "data" not in saved_data or "logs" not in saved_data:
            return self.legacy_load()

        self.__setstate__(saved_data)
        return self

    def legacy_load(self):
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
        self._check_not_frozen()
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
