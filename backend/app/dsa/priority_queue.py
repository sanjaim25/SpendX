import heapq


class MaxHeap:
    """
    Max Priority Queue for tracking top expenses.
    Uses Python's heapq (min-heap) with negated values to simulate max-heap.
    """

    def __init__(self):
        self._heap = []
        self._counter = 0  # Tiebreaker for equal amounts

    def push(self, amount: float, expense_data: dict):
        """Insert expense into the heap. O(log n)"""
        # Negate amount for max-heap behavior
        heapq.heappush(self._heap, (-amount, self._counter, expense_data))
        self._counter += 1

    def pop(self) -> dict:
        """Remove and return highest expense. O(log n)"""
        if not self._heap:
            return None
        neg_amount, _, expense_data = heapq.heappop(self._heap)
        expense_data['amount'] = -neg_amount
        return expense_data

    def peek(self) -> dict:
        """View highest expense without removing. O(1)"""
        if not self._heap:
            return None
        neg_amount, _, expense_data = self._heap[0]
        return {**expense_data, 'amount': -neg_amount}

    def get_top_n(self, n: int) -> list:
        """Return top N expenses by amount. O(n log n)"""
        top = []
        temp_heap = list(self._heap)

        for _ in range(min(n, len(temp_heap))):
            if not temp_heap:
                break
            neg_amount, counter, expense_data = heapq.heappop(temp_heap)
            top.append({**expense_data, 'amount': -neg_amount})

        return top

    def size(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def clear(self):
        self._heap = []
        self._counter = 0


class ExpensePriorityQueue:
    """
    High-level priority queue manager for SmartSpend expenses.
    """

    def __init__(self):
        self.heap = MaxHeap()

    def load_expenses(self, expenses: list):
        """Load a list of expense objects into the heap."""
        self.heap.clear()
        for expense in expenses:
            self.heap.push(expense.amount, expense.to_dict())

    def get_top_expenses(self, n: int = 5) -> list:
        """Return top N expenses."""
        return self.heap.get_top_n(n)

    def get_highest_expense(self) -> dict:
        """Return the single highest expense."""
        return self.heap.peek()

    def add_expense(self, expense) -> None:
        """Add a new expense to the queue."""
        self.heap.push(expense.amount, expense.to_dict())

    def get_expenses_above_threshold(self, threshold: float) -> list:
        """Return all expenses above a given amount."""
        all_top = self.heap.get_top_n(self.heap.size())
        return [e for e in all_top if e['amount'] >= threshold]

    def get_category_totals(self) -> dict:
        """Get total spending per category from heap data."""
        all_expenses = self.heap.get_top_n(self.heap.size())
        totals = {}
        for expense in all_expenses:
            cat = expense.get('category', 'Uncategorized')
            totals[cat] = totals.get(cat, 0) + expense['amount']
        return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))


if __name__ == '__main__':
    # Test the priority queue
    pq = MaxHeap()
    test_expenses = [
        (350, {'description': 'Swiggy order', 'category': 'Food'}),
        (1200, {'description': 'Uber to airport', 'category': 'Transport'}),
        (500, {'description': 'Netflix', 'category': 'Entertainment'}),
        (2500, {'description': 'Amazon shopping', 'category': 'Shopping'}),
        (800, {'description': 'Electricity bill', 'category': 'Bills'}),
    ]

    for amount, data in test_expenses:
        pq.push(amount, data)

    print("🏆 Top 3 Expenses:")
    for expense in pq.get_top_n(3):
        print(f"  ₹{expense['amount']} - {expense['description']} ({expense['category']})")
