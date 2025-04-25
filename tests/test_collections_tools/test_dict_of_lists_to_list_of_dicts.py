import pythonbasictools as pbt
import pytest


handmade_dict_of_lists = [
    ({"a": [1, 2, 3], "b": [9, 8, 7]}, [{"a": 1, "b": 9}, {"a": 2, "b": 8}, {"a": 3, "b": 7}]),
    ({"x": [1], "y": [2]}, [{"x": 1, "y": 2}]),
    ({"x": [], "y": []}, []),
    ({"x": [1, 2], "y": [3]}, [{"x": 1, "y": 3}, {"x": 2}]),
]


@pytest.mark.parametrize(
    "inputs, expected_output", handmade_dict_of_lists,
)
def test_dict_of_lists_to_list_of_dicts_with_handmade_data(inputs, expected_output):
    """
    Test the dict_of_lists_to_list_of_dicts function with handmade data.
    """
    result = pbt.collections_tools.dict_of_lists_to_list_of_dicts(inputs)
    assert result == expected_output


