import os
import shutil
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


class TestExperimentStateFile:
    @pytest.fixture(autouse=True, scope="class")
    def state_file(self):
        return ExperimentStateFile(".tmp/output_folder/test_state_file")

    @pytest.fixture(autouse=True, scope="class")
    def setup_and_teardown(self, state_file):
        os.makedirs(".tmp/output_folder/test_state_file", exist_ok=True)
        yield
        shutil.rmtree(".tmp/output_folder/test_state_file", ignore_errors=True)

    def test_append(self, state_file):
        state_file.append("Test content")
        content = state_file.read()
        assert content == "Test content", "Content was not appended correctly."

    def test_state_setter(self, state_file):
        state_file.state = ExperimentState.FINISHED
        assert state_file.state == ExperimentState.FINISHED, "State was not set correctly."
        assert state_file.path.exists(), "State file was not created correctly."

    def test_explicit_non_unknown_state_skips_load(self, tmp_path):
        sf = ExperimentStateFile(tmp_path / "explicit_state", state=ExperimentState.RUNNING)
        assert sf.state == ExperimentState.RUNNING


class TestOutputFolder:
    @pytest.fixture
    def output_folder(self, tmp_path):
        return OutputFolder(tmp_path / "test_output_folder")

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, output_folder):
        yield

    def test_update_metadata(self, output_folder):
        output_folder.update_metadata({"key": "value"})
        assert output_folder.metadata_file["key"] == "value", "Metadata was not updated correctly."

    def test_gather_files(self, output_folder):
        files = output_folder.gather_files()
        assert isinstance(files, list), "gather_files should return a list."
        assert len(files) == 3, "gather_files should return 3 files in the output folder."
        assert os.path.basename(output_folder.metadata_file.path) in [
            os.path.basename(f) for f in files
        ], "Metadata file should be included in the gathered files."

        with open(os.path.join(output_folder.path, "test_file.txt"), "w+") as f:
            f.write("Test content")

        files = output_folder.gather_files("*.txt")
        assert len(files) == 1, "gather_files should return one file matching the pattern."
        assert os.path.basename(files[0]) == "test_file.txt", "gather_files did not return the expected file."

    def test_root_folder_to_dataframe(self, output_folder, tmp_path):
        meta_df, df = OutputFolder.root_folder_to_dataframe(tmp_path)
        assert df is not None, "root_folder_to_dataframe should return a DataFrame."
        assert isinstance(df, pd.DataFrame), "root_folder_to_dataframe should return a DataFrame."
        assert meta_df is not None, "root_folder_to_dataframe should return a metadata DataFrame."
        assert isinstance(meta_df, pd.DataFrame), "root_folder_to_dataframe should return a metadata DataFrame."

    def test_fspath(self, output_folder):
        path_str = os.fspath(output_folder.path)
        assert isinstance(path_str, str), "fspath should return a string."
        assert path_str == os.fspath(output_folder), "fspath should return the same string as the output folder's path."

    def test_state_setter(self, output_folder):
        output_folder.state = ExperimentState.FINISHED
        assert output_folder.state == ExperimentState.FINISHED, "State was not set correctly."
        assert output_folder.state_file.path.exists(), "State file was not created correctly."

    def test_data_file_property(self, output_folder):
        data_file = output_folder.data_file
        assert Path(data_file.path).exists(), "Data file was not created correctly."
        assert Path(data_file.path) == output_folder.path / "run_output.out.json", "Data file path is incorrect."

    def test_update_data(self, output_folder):
        output_folder.update_data({"metric": 0.99})
        assert output_folder.data_file["metric"] == 0.99, "Data was not updated correctly."

    def test_update_data_with_kwargs(self, output_folder):
        output_folder.update_data(loss=0.1, accuracy=0.9)
        assert output_folder.data_file["loss"] == 0.1
        assert output_folder.data_file["accuracy"] == 0.9

    def test_explicit_metadata_and_data_file(self, tmp_path):
        meta = MetadataFile(tmp_path)
        data = RunOutputFile(tmp_path)
        folder = OutputFolder(tmp_path, metadata_file=meta, data_file=data)
        assert folder.metadata_file is meta
        assert folder.data_file is data

    def test_gather_output_folders(self, output_folder, tmp_path):
        folders = OutputFolder.gather_output_folders(tmp_path)
        assert isinstance(folders, list)
        assert len(folders) >= 1
        assert all(isinstance(f, OutputFolder) for f in folders)
