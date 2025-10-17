## Manual Algorithms Implemented

### 1) Merge Sort (stable)

Location: `Urbanmobility/Backend/utils/algorithms.py` (`merge_sort`)

Pseudocode:

```
function merge_sort(A, key):
  if |A| <= 1: return A
  mid = |A| // 2
  left = merge_sort(A[0:mid], key)
  right = merge_sort(A[mid:], key)
  return merge(left, right, key)

function merge(L, R, key):
  i = 0, j = 0, out = []
  while i < |L| and j < |R|:
    if key(L[i]) <= key(R[j]):
      out.append(L[i]); i++
    else:
      out.append(R[j]); j++
  append remaining L[i:], R[j:] to out
  return out
```

Complexity:
- Time: O(n log n)
- Space: O(n)

Used to sort vendor averages (descending) in `/api/chart/vendor_performance`.

### 2) Z-Score Anomaly Detection (manual mean/stddev)

Location: `Urbanmobility/Backend/utils/algorithms.py` (`detect_anomalies_zscore`)

Pseudocode:

```
function detect_anomalies_zscore(values, z):
  mu = mean(values)
  sigma = stddev(values, mu)
  if sigma == 0: return []
  anomalies = []
  for index, v in enumerate(values):
    zval = |(v - mu) / sigma|
    if zval >= z:
      anomalies.append((index, v, zval))
  return reverse(merge_sort(anomalies, key = third))
```

Complexity:
- Mean/stddev: O(n)
- Sorting anomalies: O(k log k), k ≤ n
- Overall: O(n log n) worst-case

Exposed via `/api/anomalies/speed?z=3.0`.

### 3) Frequency Map (manual)

Location: `Urbanmobility/Backend/utils/algorithms.py` (`frequency_map`)

Complexity:
- Time: O(n)
- Space: O(u)

## Integration Points

- `routes.py` vendor performance now sorts averages using `merge_sort`.
- New endpoint: `/api/anomalies/speed` returns z-score based speed anomalies.


