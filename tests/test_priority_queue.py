import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app.dsa.priority_queue import MaxHeap, ExpensePriorityQueue


class TestMaxHeap:
    def setup_method(self):
        self.heap = MaxHeap()

    def test_push_and_peek(self):
        self.heap.push(500, {'description': 'Test'})
        assert self.heap.peek()['amount'] == 500

    def test_max_at_top(self):
        self.heap.push(300, {'description': 'Low'})
        self.heap.push(1000, {'description': 'High'})
        self.heap.push(500, {'description': 'Mid'})
        assert self.heap.peek()['amount'] == 1000

    def test_top_n(self):
        for amt in [100, 500, 200, 800, 350]:
            self.heap.push(amt, {'description': f'Expense {amt}'})
        top3 = self.heap.get_top_n(3)
        assert top3[0]['amount'] == 800
        assert top3[1]['amount'] == 500
        assert top3[2]['amount'] == 350

    def test_empty_heap(self):
        assert self.heap.peek() is None
        assert self.heap.pop() is None
        assert self.heap.is_empty()

    def test_size(self):
        self.heap.push(100, {})
        self.heap.push(200, {})
        assert self.heap.size() == 2
