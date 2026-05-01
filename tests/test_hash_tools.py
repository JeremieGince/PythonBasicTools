import pytest

import pythonbasictools as pbt


class TestHashTools:
    def test_returns_string(self):
        result = pbt.hash_dict({"a": 1})
        assert isinstance(result, str)

    def test_returns_sha256_hex_length(self):
        result = pbt.hash_dict({"a": 1})
        assert len(result) == 64

    def test_empty_dict(self):
        result = pbt.hash_dict({})
        assert isinstance(result, str)
        assert len(result) == 64

    def test_deterministic(self):
        d = {"key": "value", "num": 42}
        assert pbt.hash_dict(d) == pbt.hash_dict(d)

    def test_key_order_independent(self):
        d1 = {"a": 1, "b": 2}
        d2 = {"b": 2, "a": 1}
        assert pbt.hash_dict(d1) == pbt.hash_dict(d2)

    def test_different_dicts_produce_different_hashes(self):
        assert pbt.hash_dict({"a": 1}) != pbt.hash_dict({"a": 2})

    def test_nested_dict(self):
        d = {"outer": {"inner": 1}}
        result = pbt.hash_dict(d)
        assert isinstance(result, str)
        assert len(result) == 64

    def test_non_string_values_via_default_str(self):
        import datetime

        d = {"date": datetime.date(2024, 1, 1)}
        result = pbt.hash_dict(d)
        assert isinstance(result, str)
        assert len(result) == 64

    @pytest.mark.parametrize(
        "d1, d2, should_match",
        [
            ({"x": 1}, {"x": 1}, True),
            ({"x": 1}, {"x": 2}, False),
            ({"a": 1, "b": 2}, {"b": 2, "a": 1}, True),
            ({}, {}, True),
            ({"a": None}, {"a": None}, True),
            ({"a": None}, {"a": 0}, False),
        ],
    )
    def test_hash_equality(self, d1, d2, should_match):
        if should_match:
            assert pbt.hash_dict(d1) == pbt.hash_dict(d2)
        else:
            assert pbt.hash_dict(d1) != pbt.hash_dict(d2)
