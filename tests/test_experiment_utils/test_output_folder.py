import os
from pathlib import Path

import pandas as pd
import pytest

from pythonbasictools.experiment_utils.metadata_file import MetadataFile
from pythonbasictools.experiment_utils.output_folder import (
    ExperimentState,
    ExperimentStateFile,
    OutputFolder,
)
from pythonbasictools.experiment_utils.run_output_file import RunOutputFile

# ---------------------------------------------------------------------------
# ExperimentStateFile
# ---------------------------------------------------------------------------


class TestExperimentStateFile:
    @pytest.fixture
    def state_file(self, tmp_path):
        return ExperimentStateFile(tmp_path / "state_dir")

    def test_initial_state_unknown_no_folder(self, tmp_path):
        sf = ExperimentStateFile(tmp_path / "nonexistent")
        assert sf.state == ExperimentState.UNKNOWN

    def test_initial_state_unknown_empty_folder(self, tmp_path):
        folder = tmp_path / "empty"
        folder.mkdir()
        sf = ExperimentStateFile(folder)
        assert sf.state == ExperimentState.UNKNOWN

    def test_explicit_non_unknown_state_skips_load(self, tmp_path):
        sf = ExperimentStateFile(tmp_path / "explicit", state=ExperimentState.RUNNING)
        assert sf.state == ExperimentState.RUNNING

    def test_path_reflects_state(self, state_file):
        assert state_file.path.name == f"state.{ExperimentState.UNKNOWN.value.lower()}"

    def test_write(self, state_file):
        state_file.write("hello")
        assert state_file.read() == "hello"

    def test_write_overwrites(self, state_file):
        state_file.write("first")
        state_file.write("second")
        assert state_file.read() == "second"

    def test_append(self, state_file):
        state_file.write("first")
        state_file.append(" second")
        assert state_file.read() == "first second"

    def test_state_setter_changes_state(self, state_file):
        state_file.state = ExperimentState.FINISHED
        assert state_file.state == ExperimentState.FINISHED

    def test_state_setter_creates_new_file(self, state_file):
        old_path = state_file.path
        state_file.state = ExperimentState.RUNNING
        assert state_file.path.exists()
        assert not old_path.exists()
        assert state_file.path.name == f"state.{ExperimentState.RUNNING.value.lower()}"

    def test_load_state_from_disk(self, tmp_path):
        folder = tmp_path / "run"
        ExperimentStateFile(folder, state=ExperimentState.FINISHED)
        reloaded = ExperimentStateFile(folder)
        assert reloaded.state == ExperimentState.FINISHED

    def test_state_file_created_on_init(self, state_file):
        assert state_file.path.exists()


# ---------------------------------------------------------------------------
# OutputFolder
# ---------------------------------------------------------------------------


class TestOutputFolder:
    @pytest.fixture
    def output_folder(self, tmp_path):
        return OutputFolder(tmp_path / "test_output_folder")

    def test_path_created_on_init(self, output_folder):
        assert output_folder.path.exists()

    def test_repr(self, output_folder):
        r = repr(output_folder)
        assert "OutputFolder" in r
        assert str(output_folder.path) in r

    def test_fspath(self, output_folder):
        path_str = os.fspath(output_folder.path)
        assert isinstance(path_str, str)
        assert path_str == os.fspath(output_folder)

    def test_metadata_file_property(self, output_folder):
        meta = output_folder.metadata_file
        assert isinstance(meta, MetadataFile)
        assert meta.path.exists()
        assert meta.path.name == "METADATA.meta.json"

    def test_data_file_property(self, output_folder):
        data_file = output_folder.data_file
        assert isinstance(data_file, RunOutputFile)
        assert data_file.path.exists()
        assert data_file.path == output_folder.path / "run_output.out.json"

    def test_update_metadata(self, output_folder):
        output_folder.update_metadata({"key": "value"})
        assert output_folder.metadata_file["key"] == "value"

    def test_update_metadata_with_kwargs(self, output_folder):
        output_folder.update_metadata(experiment="test", seed=42)
        assert output_folder.metadata_file["experiment"] == "test"
        assert output_folder.metadata_file["seed"] == 42

    def test_update_metadata_dict_and_kwargs_merged(self, output_folder):
        output_folder.update_metadata({"a": 1}, b=2)
        assert output_folder.metadata_file["a"] == 1
        assert output_folder.metadata_file["b"] == 2

    def test_update_data(self, output_folder):
        output_folder.update_data({"metric": 0.99})
        assert output_folder.data_file["metric"] == 0.99

    def test_update_data_with_kwargs(self, output_folder):
        output_folder.update_data(loss=0.1, accuracy=0.9)
        assert output_folder.data_file["loss"] == 0.1
        assert output_folder.data_file["accuracy"] == 0.9

    def test_state_initial(self, output_folder):
        assert output_folder.state == ExperimentState.UNKNOWN

    def test_state_setter(self, output_folder):
        output_folder.state = ExperimentState.FINISHED
        assert output_folder.state == ExperimentState.FINISHED
        assert output_folder.state_file.path.exists()

    def test_gather_files_all(self, output_folder):
        files = output_folder.gather_files()
        assert isinstance(files, list)
        # METADATA.meta.json, run_output.out.json, state.unknown
        assert len(files) == 3

    def test_gather_files_pattern(self, output_folder):
        (output_folder.path / "extra.txt").write_text("hi")
        files = output_folder.gather_files("*.txt")
        assert len(files) == 1
        assert files[0].name == "extra.txt"

    def test_gather_files_metadata_included(self, output_folder):
        files = output_folder.gather_files()
        names = [f.name for f in files]
        assert output_folder.metadata_file.path.name in names

    def test_explicit_metadata_and_data_file(self, tmp_path):
        meta = MetadataFile(tmp_path, save_every_set=False)
        data = RunOutputFile(tmp_path, save_every_set=False)
        folder = OutputFolder(tmp_path, metadata_file=meta, data_file=data)
        assert folder.metadata_file is meta
        assert folder.data_file is data

    def test_root_folder_to_dataframe(self, output_folder, tmp_path):
        meta_df, data_df = OutputFolder.root_folder_to_dataframe(tmp_path)
        assert isinstance(meta_df, pd.DataFrame)
        assert isinstance(data_df, pd.DataFrame)
        assert not meta_df.empty
        assert not data_df.empty

    def test_root_folder_to_dataframe_output_folder_column(self, output_folder, tmp_path):
        meta_df, data_df = OutputFolder.root_folder_to_dataframe(tmp_path)
        assert "_output_folder" in meta_df.columns
        assert "_output_folder" in data_df.columns

    def test_gather_output_folders(self, output_folder, tmp_path):
        folders = OutputFolder.gather_output_folders(tmp_path)
        assert isinstance(folders, list)
        assert len(folders) >= 1
        assert all(isinstance(f, OutputFolder) for f in folders)

    def test_gather_output_folders_multiple(self, tmp_path):
        OutputFolder(tmp_path / "run_a")
        OutputFolder(tmp_path / "run_b")
        folders = OutputFolder.gather_output_folders(tmp_path)
        assert len(folders) == 2

    # --- freeze / unfreeze ---

    def test_new_folder_starts_unfrozen(self, output_folder):
        assert not output_folder.frozen

    def test_freeze_locks_both_files(self, output_folder):
        output_folder.freeze()
        assert output_folder.frozen
        assert output_folder.metadata_file.frozen
        assert output_folder.data_file.frozen

    def test_freeze_returns_self(self, output_folder):
        assert output_folder.freeze() is output_folder

    def test_freeze_prevents_metadata_update(self, output_folder):
        output_folder.freeze()
        with pytest.raises(RuntimeError):
            output_folder.update_metadata({"key": "value"})

    def test_freeze_prevents_data_update(self, output_folder):
        output_folder.freeze()
        with pytest.raises(RuntimeError):
            output_folder.update_data({"metric": 1.0})

    def test_unfreeze_allows_writes_again(self, output_folder):
        output_folder.freeze()
        output_folder.unfreeze()
        assert not output_folder.frozen
        output_folder.update_metadata({"key": "value"})
        output_folder.update_data({"metric": 1.0})
        assert output_folder.metadata_file["key"] == "value"
        assert output_folder.data_file["metric"] == 1.0

    def test_unfreeze_returns_self(self, output_folder):
        output_folder.freeze()
        assert output_folder.unfreeze() is output_folder

    def test_freeze_persisted_to_disk(self, tmp_path):
        OutputFolder(tmp_path / "run").freeze()
        reloaded = OutputFolder(tmp_path / "run")
        assert reloaded.frozen

    def test_unfreeze_persisted_to_disk(self, tmp_path):
        folder = OutputFolder(tmp_path / "run")
        folder.freeze()
        folder.unfreeze()
        reloaded = OutputFolder(tmp_path / "run")
        assert not reloaded.frozen

    def test_frozen_false_when_only_metadata_frozen(self, output_folder):
        output_folder.metadata_file.freeze()
        assert not output_folder.frozen

    def test_frozen_false_when_only_data_frozen(self, output_folder):
        output_folder.data_file.freeze()
        assert not output_folder.frozen
