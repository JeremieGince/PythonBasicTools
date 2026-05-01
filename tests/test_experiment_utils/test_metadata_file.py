import os
import shutil

import pytest

from pythonbasictools.experiment_utils.metadata_file import MetadataFile


class TestMetadataFile:
    @pytest.fixture
    def metadata_file(self):
        return MetadataFile(
            output_dir=".tmp/metadata/test_metadata_file",
        )

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, metadata_file):
        os.makedirs(".tmp/metadata/test_metadata_file", exist_ok=True)
        yield
        shutil.rmtree(".tmp/metadata", ignore_errors=True)

    def test_getstate(self, monkeypatch, metadata_file):
        monkeypatch.setenv("TEST_ENV_VAR", "test_value")
        state = metadata_file.__getstate__()
        assert isinstance(state, dict)
        assert state["ENV"]["TEST_ENV_VAR"] == "test_value"
