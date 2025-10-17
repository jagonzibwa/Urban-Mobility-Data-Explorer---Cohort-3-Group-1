from typing import Callable, Iterable, List, Sequence, Tuple, TypeVar, Dict, Any

T = TypeVar('T')


def merge_sort(items: Sequence[T], key: Callable[[T], Any]) -> List[T]:
    """Stable merge sort implemented manually without relying on built-in sort.

    Args:
        items: Sequence of items to sort
        key: Function to extract comparison key

    Returns:
        New list sorted ascending by key
    """
    n = len(items)
    if n <= 1:
        return list(items)

    mid = n // 2
    left = merge_sort(items[:mid], key)
    right = merge_sort(items[mid:], key)
    return _merge(left, right, key)


def _merge(left: List[T], right: List[T], key: Callable[[T], Any]) -> List[T]:
    merged: List[T] = []
    i, j = 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    while i < len(left):
        merged.append(left[i])
        i += 1
    while j < len(right):
        merged.append(right[j])
        j += 1
    return merged


def compute_mean(values: Iterable[float]) -> float:
    total = 0.0
    count = 0
    for v in values:
        total += float(v)
        count += 1
    return total / count if count > 0 else 0.0


def compute_stddev(values: Iterable[float], mean: float) -> float:
    total = 0.0
    count = 0
    for v in values:
        diff = float(v) - mean
        total += diff * diff
        count += 1
    return (total / count) ** 0.5 if count > 0 else 0.0


def detect_anomalies_zscore(values: Sequence[float], z_threshold: float = 3.0) -> List[Tuple[int, float, float]]:
    """Detect anomalies using z-score (manual mean/stddev), return list of (index, value, z)."""
    if not values:
        return []
    mu = compute_mean(values)
    sigma = compute_stddev(values, mu)
    if sigma == 0:
        return []
    anomalies: List[Tuple[int, float, float]] = []
    for idx, val in enumerate(values):
        z = abs((float(val) - mu) / sigma)
        if z >= z_threshold:
            anomalies.append((idx, float(val), z))
    # Sort anomalies descending by z using merge_sort
    return list(reversed(merge_sort(anomalies, key=lambda t: t[2])))


def frequency_map(items: Iterable[Any]) -> Dict[Any, int]:
    """Manual frequency map without Counter."""
    freq: Dict[Any, int] = {}
    for item in items:
        if item in freq:
            freq[item] += 1
        else:
            freq[item] = 1
    return freq


