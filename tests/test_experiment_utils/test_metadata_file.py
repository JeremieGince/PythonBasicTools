import pytest

from pythonbasictools.experiment_utils.metadata_file import MetadataFile
from pythonbasictools.experiment_utils.run_output_file import RunOutputFile


class TestMetadataFile:
    @pytest.fixture
    def meta(self, tmp_path):
        return MetadataFile(tmp_path, data={"version": 1})

    def test_default_ext(self):
        assert MetadataFile.EXT == ".meta.json"

    def test_default_filename(self):
        assert MetadataFile.DEFAULT_FILENAME == "METADATA"

    def test_path_uses_meta_ext(self, tmp_path):
        meta = MetadataFile(tmp_path, save_every_set=False)
        assert meta.path.suffix == ".json"
        assert meta.path.name == "METADATA.meta.json"

    def test_custom_filename(self, tmp_path):
        meta = MetadataFile(tmp_path, filename="custom", save_every_set=False)
        assert meta.path.name == "custom.meta.json"

    def test_is_run_output_file_subclass(self, meta):
        assert isinstance(meta, RunOutputFile)

    def test_data_round_trip(self, tmp_path):
        MetadataFile(tmp_path, data={"k": "v"})
        loaded = MetadataFile(tmp_path, save_every_set=False)
        assert loaded["k"] == "v"

    def test_freeze_inherited(self, meta):
        meta.freeze()
        assert meta.frozen
        with pytest.raises(RuntimeError):
            meta["new_key"] = "x"

    def test_freeze_persisted(self, tmp_path):
        MetadataFile(tmp_path, data={"a": 1}).freeze()
        reloaded = MetadataFile(tmp_path, save_every_set=False)
        assert reloaded.frozen

    def test_env_captured(self, tmp_path, monkeypatch):
        monkeypatch.setenv("META_TEST_VAR", "hello")
        meta = MetadataFile(tmp_path)
        assert meta.get("ENV.META_TEST_VAR") == "hello"

    def test_env_preserved_on_reload(self, tmp_path, monkeypatch):
        monkeypatch.setenv("META_TEST_VAR", "original")
        MetadataFile(tmp_path)
        monkeypatch.setenv("META_TEST_VAR", "changed")
        reloaded = MetadataFile(tmp_path, save_every_set=False)
        assert reloaded.env.get("META_TEST_VAR") == "original"

    def test_update(self, meta):
        meta.update({"status": "done"}, print_updated=False)
        assert meta["status"] == "done"

    def test_get_missing_returns_default(self, meta):
        assert meta.get("nonexistent", 42) == 42
