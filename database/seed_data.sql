-- Seed test user
INSERT OR IGNORE INTO users (name, email, password_hash)
VALUES ('Test User', 'test@smartspend.com', 'hashed_password_here');

-- Seed expenses
INSERT INTO expenses (user_id, category_id, description, amount, date, predicted_category) VALUES
(1, 1, 'Swiggy biryani order', 350.00, '2024-01-05', 'Food'),
(1, 1, 'Zomato pizza', 450.00, '2024-01-10', 'Food'),
(1, 2, 'Uber cab to office', 200.00, '2024-01-06', 'Transport'),
(1, 3, 'Electricity bill January', 1200.00, '2024-01-15', 'Bills'),
(1, 4, 'Amazon kurta purchase', 799.00, '2024-01-20', 'Shopping'),
(1, 5, 'Netflix subscription', 499.00, '2024-01-01', 'Entertainment'),
(1, 1, 'Grocery vegetables fruits', 600.00, '2024-02-03', 'Food'),
(1, 2, 'Ola ride to mall', 150.00, '2024-02-08', 'Transport'),
(1, 3, 'Internet bill', 800.00, '2024-02-15', 'Bills'),
(1, 4, 'Flipkart shoes', 1500.00, '2024-02-22', 'Shopping');

-- Seed budgets
INSERT OR IGNORE INTO budgets (user_id, category, monthly_limit, month, year) VALUES
(1, 'Food', 3000.00, 3, 2024),
(1, 'Transport', 1500.00, 3, 2024),
(1, 'Bills', 2000.00, 3, 2024),
(1, 'Shopping', 2000.00, 3, 2024),
(1, 'Entertainment', 1000.00, 3, 2024);
