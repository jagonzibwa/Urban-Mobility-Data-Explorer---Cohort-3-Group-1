import heapq
from typing import Generic, List, Tuple, TypeVar

T = TypeVar('T')


class MinHeapPriorityQueue(Generic[T]):
    """A simple min-heap based priority queue with (priority, item) tuples."""

    def __init__(self) -> None:
        self._heap: List[Tuple[float, T]] = []

    def push(self, priority: float, item: T) -> None:
        heapq.heappush(self._heap, (priority, item))

    def pop(self) -> Tuple[float, T]:
        return heapq.heappop(self._heap)

    def __len__(self) -> int:
        return len(self._heap)

    def peek(self) -> Tuple[float, T]:
        return self._heap[0]


