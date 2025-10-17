from Urbanmobility.Backend.utils import merge_sort, detect_anomalies_zscore, frequency_map


def test_merge_sort_basic():
    items = [("b", 2), ("a", 1), ("c", 3)]
    out = merge_sort(items, key=lambda x: x[1])
    assert [k for k, _ in out] == ["a", "b", "c"]


def test_frequency_map():
    data = ['a', 'b', 'a', 'c', 'b', 'a']
    freq = frequency_map(data)
    assert freq == {'a': 3, 'b': 2, 'c': 1}


def test_detect_anomalies_zscore_empty():
    assert detect_anomalies_zscore([]) == []


