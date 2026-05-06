import json
import logging
import os

import pandas as pd
import pytest

from pythonbasictools.experiment_utils.run_output_file import RunOutputFile


class TestRunOutputFile:
    @pytest.fixture
    def rof(self, tmp_path):
        return RunOutputFile(tmp_path, data={"initial": 1})

    # --- dunder methods ---

    def test_setitem(self, rof):
        rof["key"] = "value"
        assert rof["key"] == "value"

    def test_delitem(self, rof):
        del rof["initial"]
        assert "initial" not in rof.data

    def test_get(self, rof):
        assert rof.get("initial") == 1
        assert rof.get("missing", "default") == "default"

    def test_contains(self, rof):
        assert "initial" in rof
        assert "missing" not in rof

    def test_iter(self, rof):
        assert "initial" in list(rof)

    def test_len(self, rof):
        assert len(rof) == 1

    def test_add(self, rof):
        result = rof + {"extra": 2}
        assert result["extra"] == 2
        assert rof["extra"] == 2

    def test_sub(self, rof):
        rof - ["initial"]
        assert "initial" not in rof.data

    def test_repr(self, rof):
        r = repr(rof)
        assert "initial" in r
        assert "Saved to" in r
        assert "Frozen" in r

    def test_fspath(self, rof):
        fspath = os.fspath(rof)
        assert isinstance(fspath, str)
        assert "run_output" in fspath

    # --- update ---

    def test_update_no_print(self, rof, capsys):
        rof.update({"key": "value"}, print_updated=False)
        assert rof["key"] == "value"
        captured = capsys.readouterr()
        assert "key" not in captured.out

    # --- save_if_save_every_set with save_every_set=False ---

    def test_save_every_set_false_skips_save(self, tmp_path):
        rof = RunOutputFile(tmp_path / "no_save", save_every_set=False)
        rof["key"] = "value"
        assert rof["key"] == "value"
        assert not rof.path.exists()

    # --- legacy_load ---

    def test_legacy_load(self, tmp_path):
        legacy_data = {"result": 42, "status": "done"}
        rof_path = tmp_path / (RunOutputFile.DEFAULT_FILENAME + RunOutputFile.EXT)
        with open(rof_path, "w") as f:
            json.dump(legacy_data, f)
        rof = RunOutputFile(tmp_path, save_every_set=False)
        assert rof["result"] == 42
        assert rof["status"] == "done"

    # --- raveled_state_from_file error branch ---

    def test_raveled_state_from_file_returns_empty_on_error(self):
        result = RunOutputFile.raveled_state_from_file("nonexistent/path.out.json", data=42)
        assert result == {}

    def test_raveled_state_from_file_raises_on_error(self):
        with pytest.raises(TypeError):
            RunOutputFile.raveled_state_from_file("nonexistent/path.out.json", data=42, raise_on_error=True)

    # --- as_dataframe / as_series ---

    def test_as_dataframe(self, rof):
        df = rof.as_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert f"{rof.EXT}_path" in df.columns

    def test_as_dataframe_no_path(self, rof):
        df = rof.as_dataframe(add_path=False)
        assert isinstance(df, pd.DataFrame)
        assert f"{rof.EXT}_path" not in df.columns

    def test_as_series(self, rof):
        s = rof.as_series()
        assert isinstance(s, pd.Series)
        assert f"{rof.EXT}_path" in s.index

    def test_as_series_no_path(self, rof):
        s = rof.as_series(add_path=False)
        assert isinstance(s, pd.Series)
        assert f"{rof.EXT}_path" not in s.index

    # --- get_raveled_state with explicit key_sep ---

    def test_get_raveled_state_custom_sep(self, rof):
        rof["nested"] = {"a": 1}
        result = rof.get_raveled_state(key_sep="-")
        assert isinstance(result, dict)
        assert "nested-a" in result

    # --- log ---

    def test_log_info(self, rof, capsys):
        rof.log("info message", level=logging.INFO)
        captured = capsys.readouterr()
        assert "info message" in captured.out

    def test_log_warning(self, rof):
        with pytest.warns(UserWarning, match="warning message"):
            rof.log("warning message", level=logging.WARNING)

    def test_log_error(self, rof):
        with pytest.warns(UserWarning, match="error message"):
            rof.log("error message", level=logging.ERROR)

    def test_log_custom_level(self, rof, capsys):
        rof.log("custom message", level=99)
        captured = capsys.readouterr()
        assert "custom message" in captured.out

    def test_log_no_print(self, rof, capsys):
        rof.log("silent", print_msg=False)
        captured = capsys.readouterr()
        assert "silent" not in captured.out
        assert "silent" in rof.logs[logging.INFO]

    # --- print_logs ---

    def test_print_logs(self, rof, capsys):
        rof.log("line 1", print_msg=False)
        rof.log("line 2", print_msg=False)
        rof.print_logs()
        captured = capsys.readouterr()
        assert "line 1" in captured.out
        assert "line 2" in captured.out

    # --- parse_results_from_dir_to_dataframe ---

    def test_parse_results_from_dir_to_dataframe(self, rof, tmp_path):
        df = RunOutputFile.parse_results_from_dir_to_dataframe(tmp_path, mp_kwargs={"nb_workers": 0})
        assert isinstance(df, pd.DataFrame)

    def test_parse_results_with_requires_columns(self, rof, tmp_path):
        df = RunOutputFile.parse_results_from_dir_to_dataframe(
            tmp_path, requires_columns=["initial"], mp_kwargs={"nb_workers": 0}
        )
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert df["initial"].notna().all()

    # --- freeze / unfreeze ---

    def test_new_file_starts_unfrozen(self, tmp_path):
        rof = RunOutputFile(tmp_path / "fresh")
        assert not rof.frozen

    def test_freeze_sets_flag(self, rof):
        assert not rof.frozen
        rof.freeze()
        assert rof.frozen

    def test_freeze_persisted_to_disk(self, tmp_path):
        rof = RunOutputFile(tmp_path)
        rof.freeze()
        reloaded = RunOutputFile(tmp_path)
        assert reloaded.frozen

    def test_unfreeze_clears_flag(self, tmp_path):
        rof = RunOutputFile(tmp_path)
        rof.freeze()
        rof.unfreeze()
        assert not rof.frozen

    def test_unfreeze_persisted_to_disk(self, tmp_path):
        rof = RunOutputFile(tmp_path)
        rof.freeze()
        rof.unfreeze()
        reloaded = RunOutputFile(tmp_path)
        assert not reloaded.frozen

    def test_setitem_raises_when_frozen(self, rof):
        rof.freeze()
        with pytest.raises(RuntimeError):
            rof["key"] = "value"

    def test_delitem_raises_when_frozen(self, rof):
        rof.freeze()
        with pytest.raises(RuntimeError):
            del rof["initial"]

    def test_add_raises_when_frozen(self, rof):
        rof.freeze()
        with pytest.raises(RuntimeError):
            rof + {"extra": 2}

    def test_sub_raises_when_frozen(self, rof):
        rof.freeze()
        with pytest.raises(RuntimeError):
            rof - ["initial"]

    def test_update_raises_when_frozen(self, rof):
        rof.freeze()
        with pytest.raises(RuntimeError):
            rof.update({"key": "value"})

    def test_log_raises_when_frozen(self, rof):
        rof.freeze()
        with pytest.raises(RuntimeError):
            rof.log("msg")

    def test_init_with_data_raises_when_frozen(self, tmp_path):
        rof = RunOutputFile(tmp_path)
        rof.freeze()
        with pytest.raises(RuntimeError):
            RunOutputFile(tmp_path, data={"extra": 1})

    def test_unfreeze_allows_writes_again(self, rof):
        rof.freeze()
        rof.unfreeze()
        rof["key"] = "value"
        assert rof["key"] == "value"

    def test_legacy_file_loads_unfrozen(self, tmp_path):
        legacy_data = {"result": 42}
        rof_path = tmp_path / (RunOutputFile.DEFAULT_FILENAME + RunOutputFile.EXT)
        with open(rof_path, "w") as f:
            json.dump(legacy_data, f)
        rof = RunOutputFile(tmp_path, save_every_set=False)
        assert not rof.frozen

    # --- ENV preservation ---

    def test_env_captured_on_creation(self, tmp_path):
        rof = RunOutputFile(tmp_path)
        assert isinstance(rof.env, dict)
        assert len(rof.env) > 0

    def test_env_contains_known_var(self, tmp_path, monkeypatch):
        monkeypatch.setenv("ROF_TEST_VAR", "hello")
        rof = RunOutputFile(tmp_path)
        assert rof.env.get("ROF_TEST_VAR") == "hello"

    def test_env_preserved_on_reload(self, tmp_path, monkeypatch):
        monkeypatch.setenv("ROF_TEST_VAR", "original")
        rof = RunOutputFile(tmp_path)
        original_env = rof.env.copy()

        monkeypatch.setenv("ROF_TEST_VAR", "changed")
        reloaded = RunOutputFile(tmp_path)
        assert reloaded.env.get("ROF_TEST_VAR") == "original"
        assert reloaded.env == original_env

    def test_env_not_captured_again_on_reload(self, tmp_path, monkeypatch):
        monkeypatch.setenv("ROF_ONLY_FIRST", "yes")
        RunOutputFile(tmp_path)

        monkeypatch.delenv("ROF_ONLY_FIRST")
        reloaded = RunOutputFile(tmp_path)
        assert reloaded.env.get("ROF_ONLY_FIRST") == "yes"

    # --- get() with META_KEY.KEY format ---

    def test_get_env_key(self, tmp_path, monkeypatch):
        monkeypatch.setenv("ROF_TEST_VAR", "myvalue")
        rof = RunOutputFile(tmp_path)
        assert rof.get("ENV.ROF_TEST_VAR") == "myvalue"

    def test_get_env_missing_key_returns_default(self, rof):
        assert rof.get("ENV.NONEXISTENT_KEY_XYZ", "fallback") == "fallback"

    def test_get_data_takes_priority_over_meta(self, tmp_path, monkeypatch):
        monkeypatch.setenv("ROF_TEST_VAR", "env_value")
        rof = RunOutputFile(tmp_path, save_every_set=False)
        rof.data["ENV.ROF_TEST_VAR"] = "data_value"
        assert rof.get("ENV.ROF_TEST_VAR") == "data_value"

    def test_get_env_case_insensitive_prefix(self, tmp_path, monkeypatch):
        monkeypatch.setenv("ROF_TEST_VAR", "myvalue")
        rof = RunOutputFile(tmp_path)
        assert rof.get("env.ROF_TEST_VAR") == "myvalue"

    def test_get_plain_key_still_works(self, rof):
        assert rof.get("initial") == 1
        assert rof.get("missing") is None
        assert rof.get("missing", 42) == 42

    def test_get_unknown_meta_prefix_returns_default(self, rof):
        assert rof.get("UNKNOWN.key", "default") == "default"
