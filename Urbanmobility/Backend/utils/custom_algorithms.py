"""
Custom Data Structures and Algorithms for Urban Mobility Data Explorer
Manual implementations without relying on built-in libraries
"""

from typing import List, Tuple, Dict, Any, Callable, Optional, Sequence, TypeVar

T = TypeVar('T')


# ============================================================================
# ALGORITHM 1: QUICK SELECT (k-th Smallest Element)
# ============================================================================

def quick_select(arr: List[float], k: int) -> float:
    """
    Find the k-th smallest element using QuickSelect algorithm.
    Used for percentile calculation without sorting entire array.
    
    Real-world use: Calculate 95th percentile trip duration for SLA monitoring
    
    Time Complexity: O(n) average, O(n²) worst case
    Space Complexity: O(1) in-place
    
    Args:
        arr: List of numbers
        k: Index of element to find (0-based)
    
    Returns:
        The k-th smallest element
    """
    if not arr or k < 0 or k >= len(arr):
        raise ValueError("Invalid input")
    
    def partition(left: int, right: int, pivot_idx: int) -> int:
        """Partition array around pivot, return pivot's final position"""
        pivot_value = arr[pivot_idx]
        # Move pivot to end
        arr[pivot_idx], arr[right] = arr[right], arr[pivot_idx]
        
        store_idx = left
        for i in range(left, right):
            if arr[i] < pivot_value:
                arr[store_idx], arr[i] = arr[i], arr[store_idx]
                store_idx += 1
        
        # Move pivot to final position
        arr[right], arr[store_idx] = arr[store_idx], arr[right]
        return store_idx
    
    def select(left: int, right: int, k_smallest: int) -> float:
        """Recursive selection"""
        if left == right:
            return arr[left]
        
        # Choose pivot (middle element for better average performance)
        pivot_idx = (left + right) // 2
        pivot_idx = partition(left, right, pivot_idx)
        
        if k_smallest == pivot_idx:
            return arr[k_smallest]
        elif k_smallest < pivot_idx:
            return select(left, pivot_idx - 1, k_smallest)
        else:
            return select(pivot_idx + 1, right, k_smallest)
    
    return select(0, len(arr) - 1, k)


def calculate_percentile(values: List[float], percentile: int) -> float:
    """
    Calculate percentile without sorting (using QuickSelect).
    
    Args:
        values: List of numeric values
        percentile: Percentile to calculate (0-100)
    
    Returns:
        Value at given percentile
    """
    if not values:
        return 0.0
    
    # Create copy to avoid modifying original
    arr = values.copy()
    k = int((percentile / 100.0) * (len(arr) - 1))
    return quick_select(arr, k)


# ============================================================================
# ALGORITHM 2: BINARY SEARCH TREE (for Range Queries)
# ============================================================================

class BSTNode:
    """Node in Binary Search Tree"""
    def __init__(self, key: float, value: Any):
        self.key = key
        self.value = value
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None


class BinarySearchTree:
    """
    Binary Search Tree for efficient range queries.
    Used for finding trips within specific duration/distance ranges.
    
    Time Complexity:
        - insert: O(log n) average, O(n) worst
        - search: O(log n) average, O(n) worst
        - range_query: O(log n + k) where k is result size
    """
    
    def __init__(self):
        self.root: Optional[BSTNode] = None
    
    def insert(self, key: float, value: Any) -> None:
        """Insert key-value pair into BST"""
        if self.root is None:
            self.root = BSTNode(key, value)
        else:
            self._insert_recursive(self.root, key, value)
    
    def _insert_recursive(self, node: BSTNode, key: float, value: Any) -> None:
        """Recursive insertion helper"""
        if key < node.key:
            if node.left is None:
                node.left = BSTNode(key, value)
            else:
                self._insert_recursive(node.left, key, value)
        else:
            if node.right is None:
                node.right = BSTNode(key, value)
            else:
                self._insert_recursive(node.right, key, value)
    
    def range_query(self, min_key: float, max_key: float) -> List[Tuple[float, Any]]:
        """
        Find all (key, value) pairs where min_key <= key <= max_key
        
        Real-world use: Find all trips with duration between 10-20 minutes
        """
        results = []
        self._range_query_recursive(self.root, min_key, max_key, results)
        return results
    
    def _range_query_recursive(self, node: Optional[BSTNode], 
                               min_key: float, max_key: float, 
                               results: List[Tuple[float, Any]]) -> None:
        """Recursive range query helper"""
        if node is None:
            return
        
        # If current node is in range, add it
        if min_key <= node.key <= max_key:
            results.append((node.key, node.value))
        
        # Recursively search left subtree if needed
        if node.key > min_key and node.left:
            self._range_query_recursive(node.left, min_key, max_key, results)
        
        # Recursively search right subtree if needed
        if node.key < max_key and node.right:
            self._range_query_recursive(node.right, min_key, max_key, results)


# ============================================================================
# ALGORITHM 3: SLIDING WINDOW (for Moving Averages)
# ============================================================================

class SlidingWindow:
    """
    Efficient sliding window for calculating moving statistics.
    Used for traffic pattern analysis with rolling averages.
    
    Time Complexity: O(1) per add operation
    Space Complexity: O(window_size)
    """
    
    def __init__(self, window_size: int):
        if window_size <= 0:
            raise ValueError("Window size must be positive")
        
        self.window_size = window_size
        self.window: List[float] = []
        self.sum = 0.0
    
    def add(self, value: float) -> float:
        """
        Add value to window and return current average.
        
        Returns:
            Moving average after adding value
        """
        self.window.append(value)
        self.sum += value
        
        # Remove oldest value if window exceeds size
        if len(self.window) > self.window_size:
            removed = self.window.pop(0)
            self.sum -= removed
        
        return self.get_average()
    
    def get_average(self) -> float:
        """Get current window average"""
        if not self.window:
            return 0.0
        return self.sum / len(self.window)
    
    def get_min(self) -> float:
        """Get minimum value in current window"""
        return min(self.window) if self.window else 0.0
    
    def get_max(self) -> float:
        """Get maximum value in current window"""
        return max(self.window) if self.window else 0.0


# ============================================================================
# ALGORITHM 4: CUSTOM HASH TABLE (for Fast Lookups)
# ============================================================================

class CustomHashTable:
    """
    Custom hash table implementation with separate chaining.
    Used for fast vendor/location lookup without Python dict.
    
    Time Complexity:
        - insert: O(1) average, O(n) worst
        - get: O(1) average, O(n) worst
        - delete: O(1) average, O(n) worst
    
    Space Complexity: O(n + m) where n=items, m=buckets
    """
    
    def __init__(self, size: int = 100):
        self.size = size
        self.buckets: List[List[Tuple[Any, Any]]] = [[] for _ in range(size)]
        self.count = 0
    
    def _hash(self, key: Any) -> int:
        """Custom hash function"""
        if isinstance(key, str):
            # String hashing: sum of char codes weighted by position
            hash_val = 0
            for i, char in enumerate(key):
                hash_val += ord(char) * (31 ** i)
            return hash_val % self.size
        elif isinstance(key, (int, float)):
            # Numeric hashing
            return int(key) % self.size
        else:
            # Use Python's hash as fallback
            return hash(key) % self.size
    
    def insert(self, key: Any, value: Any) -> None:
        """Insert key-value pair"""
        bucket_idx = self._hash(key)
        bucket = self.buckets[bucket_idx]
        
        # Update if key exists
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        
        # Insert new key-value
        bucket.append((key, value))
        self.count += 1
    
    def get(self, key: Any) -> Optional[Any]:
        """Get value by key"""
        bucket_idx = self._hash(key)
        bucket = self.buckets[bucket_idx]
        
        for k, v in bucket:
            if k == key:
                return v
        return None
    
    def delete(self, key: Any) -> bool:
        """Delete key-value pair, return True if found"""
        bucket_idx = self._hash(key)
        bucket = self.buckets[bucket_idx]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self.count -= 1
                return True
        return False
    
    def __len__(self) -> int:
        return self.count
    
    def load_factor(self) -> float:
        """Calculate load factor (avg items per bucket)"""
        return self.count / self.size


# ============================================================================
# ALGORITHM 5: TOP-K ELEMENTS (using Min Heap)
# ============================================================================

class MinHeap:
    """
    Manual min heap implementation for top-k algorithm.
    No use of heapq library.
    """
    
    def __init__(self):
        self.heap: List[Tuple[float, Any]] = []
    
    def push(self, priority: float, item: Any) -> None:
        """Add item to heap"""
        self.heap.append((priority, item))
        self._bubble_up(len(self.heap) - 1)
    
    def pop(self) -> Tuple[float, Any]:
        """Remove and return minimum item"""
        if not self.heap:
            raise IndexError("Heap is empty")
        
        # Swap first and last
        self.heap[0], self.heap[-1] = self.heap[-1], self.heap[0]
        min_item = self.heap.pop()
        
        if self.heap:
            self._bubble_down(0)
        
        return min_item
    
    def peek(self) -> Tuple[float, Any]:
        """View minimum item without removing"""
        return self.heap[0] if self.heap else None
    
    def _bubble_up(self, idx: int) -> None:
        """Restore heap property upward"""
        while idx > 0:
            parent_idx = (idx - 1) // 2
            if self.heap[idx][0] < self.heap[parent_idx][0]:
                self.heap[idx], self.heap[parent_idx] = self.heap[parent_idx], self.heap[idx]
                idx = parent_idx
            else:
                break
    
    def _bubble_down(self, idx: int) -> None:
        """Restore heap property downward"""
        while True:
            smallest = idx
            left = 2 * idx + 1
            right = 2 * idx + 2
            
            if left < len(self.heap) and self.heap[left][0] < self.heap[smallest][0]:
                smallest = left
            
            if right < len(self.heap) and self.heap[right][0] < self.heap[smallest][0]:
                smallest = right
            
            if smallest != idx:
                self.heap[idx], self.heap[smallest] = self.heap[smallest], self.heap[idx]
                idx = smallest
            else:
                break
    
    def __len__(self) -> int:
        return len(self.heap)


def find_top_k(items: List[Tuple[float, Any]], k: int) -> List[Tuple[float, Any]]:
    """
    Find top k items by value using min heap.
    
    Real-world use: Find top 10 busiest locations
    
    Time Complexity: O(n log k)
    Space Complexity: O(k)
    
    Args:
        items: List of (value, data) tuples
        k: Number of top items to find
    
    Returns:
        List of top k items sorted descending by value
    """
    if k <= 0:
        return []
    
    if k >= len(items):
        # If k >= n, just sort all items
        return sorted(items, key=lambda x: x[0], reverse=True)
    
    # Use min heap of size k
    heap = MinHeap()
    
    for value, data in items:
        if len(heap) < k:
            heap.push(value, data)
        elif value > heap.peek()[0]:
            heap.pop()
            heap.push(value, data)
    
    # Extract all and reverse for descending order
    result = []
    while len(heap) > 0:
        result.append(heap.pop())
    
    return list(reversed(result))


# ============================================================================
# ALGORITHM 6: STRING PATTERN MATCHING (Rabin-Karp)
# ============================================================================

def rabin_karp_search(text: str, pattern: str) -> List[int]:
    """
    Find all occurrences of pattern in text using Rabin-Karp algorithm.
    
    Real-world use: Search for specific location names or vendor codes
    
    Time Complexity: O(n + m) average, O(nm) worst case
    Space Complexity: O(1)
    
    Args:
        text: Text to search in
        pattern: Pattern to find
    
    Returns:
        List of starting indices where pattern occurs
    """
    if not pattern or not text or len(pattern) > len(text):
        return []
    
    # Constants for hashing
    d = 256  # Number of characters in alphabet
    q = 101  # Prime number for modulo
    
    m = len(pattern)
    n = len(text)
    pattern_hash = 0
    text_hash = 0
    h = 1
    results = []
    
    # Calculate h = d^(m-1) % q
    for i in range(m - 1):
        h = (h * d) % q
    
    # Calculate initial hash values
    for i in range(m):
        pattern_hash = (d * pattern_hash + ord(pattern[i])) % q
        text_hash = (d * text_hash + ord(text[i])) % q
    
    # Slide pattern over text
    for i in range(n - m + 1):
        # Check if hash values match
        if pattern_hash == text_hash:
            # Verify actual match (avoid hash collisions)
            if text[i:i + m] == pattern:
                results.append(i)
        
        # Calculate hash for next window
        if i < n - m:
            text_hash = (d * (text_hash - ord(text[i]) * h) + ord(text[i + m])) % q
            if text_hash < 0:
                text_hash += q
    
    return results


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def manual_median(values: List[float]) -> float:
    """
    Calculate median without using statistics library.
    Uses QuickSelect for O(n) average performance.
    
    Args:
        values: List of numbers
    
    Returns:
        Median value
    """
    if not values:
        return 0.0
    
    arr = values.copy()
    n = len(arr)
    
    if n % 2 == 1:
        # Odd length: return middle element
        return quick_select(arr, n // 2)
    else:
        # Even length: return average of two middle elements
        left_mid = quick_select(arr.copy(), n // 2 - 1)
        right_mid = quick_select(arr, n // 2)
        return (left_mid + right_mid) / 2.0


def detect_outliers_iqr(values: List[float]) -> List[Tuple[int, float]]:
    """
    Detect outliers using Interquartile Range (IQR) method.
    
    Outlier if: value < Q1 - 1.5*IQR  OR  value > Q3 + 1.5*IQR
    
    Time Complexity: O(n) average (using QuickSelect for quartiles)
    
    Args:
        values: List of numeric values
    
    Returns:
        List of (index, value) tuples for outliers
    """
    if len(values) < 4:
        return []
    
    # Calculate quartiles using QuickSelect
    arr = values.copy()
    q1 = quick_select(arr.copy(), len(arr) // 4)
    q3 = quick_select(arr.copy(), 3 * len(arr) // 4)
    iqr = q3 - q1
    
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    outliers = []
    for idx, val in enumerate(values):
        if val < lower_bound or val > upper_bound:
            outliers.append((idx, val))
    
    return outliers


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'quick_select',
    'calculate_percentile',
    'BinarySearchTree',
    'SlidingWindow',
    'CustomHashTable',
    'find_top_k',
    'rabin_karp_search',
    'manual_median',
    'detect_outliers_iqr',
]
