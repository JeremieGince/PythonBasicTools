import enum
import glob
import os
from pathlib import Path
from typing import List, Optional, Tuple, Union

import pandas as pd
from tqdm import tqdm

from .metadata_file import MetadataFile
from .run_output_file import RunOutputFile


class ExperimentState(enum.Enum):
    UNKNOWN = "UNKNOWN"
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"


class ExperimentStateFile:
    FILENAME = "state"

    def __init__(
        self,
        folder: Union[str, Path],
        state: ExperimentState = ExperimentState.UNKNOWN,
    ):
        self._folder = Path(folder)
        if state == ExperimentState.UNKNOWN:
            state = self._load_state()
        self._state = state
        self._maybe_create()

    def write(self, new_text: str):
        self._folder.mkdir(parents=True, exist_ok=True)
        with self.path.open("w") as f:
            f.write(new_text)

    def append(self, new_text: str):
        self._folder.mkdir(parents=True, exist_ok=True)
        with self.path.open("a") as f:
            f.write(new_text)

    def read(self) -> str:
        return self.path.read_text()

    def _load_state(self):
        if not self._folder.exists():
            return ExperimentState.UNKNOWN
        files = glob.glob(f"{self._folder / self.FILENAME}.*")
        files = [Path(file) for file in files if Path(file).is_file()]
        if len(files) == 0:
            return ExperimentState.UNKNOWN
        state_str = files[0].suffix.replace(".", "")
        state = ExperimentState[state_str.upper()]
        return state

    def _maybe_create(self):
        if not self.path.exists():
            self.write("")
        return

    @property
    def path(self) -> Path:
        return self._folder / f"{self.FILENAME}.{self._state.value.lower()}"

    @property
    def state(self) -> ExperimentState:
        return self._state

    @state.setter
    def state(self, new_state: ExperimentState):
        """
        Delete the current file and create another with the new state.
        """
        try:
            os.remove(self.path)
        except FileNotFoundError:  # pragma: no cover
            pass
        self._state = new_state
        self._maybe_create()


class OutputFolder:
    @classmethod
    def root_folder_to_dataframe(
        cls,
        root_folder: Union[str, Path],
        metadata_ext: str = MetadataFile.EXT,
        data_ext: str = RunOutputFile.EXT,
        **kwargs,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Gather all the metadata files and data files and build two dataframes, one for metadata and
        a second for the data. Each row in the dataframe corresponds to the data of one file.
        The dataframes can be merge together using the `_output_folder` column.

        :Example:
        >>> metadata_df, data_df = OutputFolder.root_folder_to_dataframe("./data/root")
        >>> full_df = pd.merge(metadata_df, data_df, on="_output_folder")
        """
        kwargs.setdefault("save_every_set", False)
        root_folder = Path(root_folder)
        metadata_paths = list(root_folder.rglob(f"*{metadata_ext}"))
        data_paths = list(root_folder.rglob(f"*{data_ext}"))

        metadata_df = pd.DataFrame(
            [
                {
                    "_output_folder": p.parent.relative_to(root_folder),
                    **MetadataFile.raveled_state_from_file(p, **kwargs),  # type: ignore
                }
                for p in tqdm(metadata_paths, desc="Gathering metadata")
            ]
        )
        data_df = pd.DataFrame(
            [
                {
                    "_output_folder": p.parent.relative_to(root_folder),
                    **RunOutputFile.raveled_state_from_file(p, **kwargs),  # type: ignore
                }
                for p in tqdm(data_paths, desc="Gathering data")
            ]
        )
        return metadata_df, data_df

    @classmethod
    def gather_output_folders(
        cls,
        root_folder: Union[str, Path],
        metadata_ext: str = MetadataFile.EXT,
        data_ext: str = RunOutputFile.EXT,
        **kwargs,
    ) -> List["OutputFolder"]:
        kwargs.setdefault("metadata_kwargs", {})
        kwargs.setdefault("data_kwargs", {})
        kwargs["metadata_kwargs"].setdefault("save_every_set", False)
        kwargs["data_kwargs"].setdefault("save_every_set", False)

        root_folder = Path(root_folder)
        metadata_paths = list(root_folder.rglob(f"*{metadata_ext}"))
        data_paths = list(root_folder.rglob(f"*{data_ext}"))
        parent_paths = set(p.parent for p in (metadata_paths + data_paths))
        output_folders = [cls(p, **kwargs) for p in tqdm(parent_paths, desc="Gathering output folders")]
        return output_folders

    def __init__(
        self,
        path: Union[str, Path],
        metadata_file: Optional[MetadataFile] = None,
        data_file: Optional[RunOutputFile] = None,
        metadata_kwargs: Optional[dict] = None,
        data_kwargs: Optional[dict] = None,
    ):
        metadata_kwargs = metadata_kwargs or {}
        data_kwargs = data_kwargs or {}
        self._path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        if metadata_file is None:
            metadata_file = MetadataFile(self.path, **metadata_kwargs)
        if data_file is None:
            data_file = RunOutputFile(self.path, **data_kwargs)  # type: ignore
        self._metadata_file = metadata_file
        self._data_file = data_file
        self._state_file = ExperimentStateFile(self.path)

    def __fspath__(self):
        return os.fspath(self._path)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._path})"

    @property
    def frozen(self) -> bool:
        return self._metadata_file.frozen and self._data_file.frozen

    def freeze(self):
        """Lock both the metadata and data files. Persisted to disk."""
        self._metadata_file.freeze()
        self._data_file.freeze()
        return self

    def unfreeze(self):
        """Unlock both the metadata and data files. Persisted to disk."""
        self._metadata_file.unfreeze()
        self._data_file.unfreeze()
        return self

    def update_metadata(self, other: Optional[dict] = None, **kwargs):
        """
        Updates the metadata of the instance with information from the provided dictionary
        and any additional keyword arguments. If a dictionary is not provided, an empty
        dictionary is used. The method updates the instance's metadata with both the
        values from the given dictionary and the keyword arguments.

        :param other: Optional initial dictionary of metadata to update. Defaults to None.
        :type other: Optional[dict]
        :param kwargs: Additional metadata key-value pairs to update.
        :return: None
        """
        other = other or {}
        other.update(kwargs)
        self.metadata_file.update(other)

    def update_data(self, other: Optional[dict] = None, **kwargs):
        other = other or {}
        other.update(kwargs)
        self.data_file.update(other)

    def gather_files(
        self,
        pattern: str = "*",
    ) -> List[Path]:
        """
        Gather files in the output folder matching the given pattern.

        :param pattern: The glob pattern to match files.
        :return: A list of file paths matching the pattern.
        """
        return list(self.path.glob(pattern))

    @property
    def path(self) -> Path:
        return self._path

    @property
    def metadata_file(self) -> MetadataFile:
        return self._metadata_file

    @property
    def data_file(self) -> RunOutputFile:
        return self._data_file

    @property
    def state_file(self) -> ExperimentStateFile:
        return self._state_file

    @property
    def state(self) -> ExperimentState:
        return self.state_file.state

    @state.setter
    def state(self, new_state: ExperimentState):
        self.state_file.state = new_state
        return
