import React, { useEffect, useState } from 'react';
import { expenseAPI } from '../services/api';

const BADGE_CLASS = {
  Food: 'badge badge-food',
  Transport: 'badge badge-transport',
  Bills: 'badge badge-bills',
  Shopping: 'badge badge-shopping',
  Entertainment: 'badge badge-entertainment',
  Health: 'badge badge-health',
};

const CATEGORY_META = {
  All: { icon: '◌' },
  Food: { icon: '🍽' },
  Transport: { icon: '↗' },
  Bills: { icon: '▣' },
  Shopping: { icon: '◇' },
  Entertainment: { icon: '▶' },
  Health: { icon: '✚' },
};

const ExpenseList = ({ token, refreshKey, onAddExpenseRequest }) => {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('All');
  const [search, setSearch] = useState('');
  const [deleting, setDeleting] = useState(null);

  const categories = ['All', 'Food', 'Transport', 'Bills', 'Shopping', 'Entertainment', 'Health'];

  useEffect(() => {
    const fetchExpenses = async () => {
      setLoading(true);
      try {
        const data = await expenseAPI.getAll(token);
        setExpenses(data.expenses || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchExpenses();
  }, [token, refreshKey]);

  const handleDelete = async (id) => {
    setDeleting(id);
    try {
      await expenseAPI.delete(token, id);
      setExpenses((prev) => prev.filter((e) => e.id !== id));
    } catch (err) {
      console.error(err);
    } finally {
      setDeleting(null);
    }
  };

  const filtered = expenses.filter((e) => {
    const matchCat = filter === 'All' || e.category === filter;
    const matchSearch = e.description.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  const total = filtered.reduce((sum, e) => sum + e.amount, 0);
  const totalExpenses = expenses.reduce((sum, e) => sum + e.amount, 0);
  const today = new Date();
  const mondayOffset = (today.getDay() + 6) % 7;
  const weekStart = new Date(today);
  weekStart.setDate(today.getDate() - mondayOffset);
  weekStart.setHours(0, 0, 0, 0);
  const weeklyTotal = expenses.reduce((sum, expense) => {
    const expenseDate = new Date(expense.date);
    if (!Number.isNaN(expenseDate.getTime()) && expenseDate >= weekStart) return sum + expense.amount;
    return sum;
  }, 0);

  return (
    <div style={styles.pageWrap}>
      <div style={styles.summaryRow}>
        <div style={styles.summaryCard} className="glass-card expense-summary-card">
          <div style={styles.summaryIcon}>◴</div>
          <div>
            <p style={styles.summaryLabel}>Weekly total</p>
            <p style={styles.summaryValue}>{'\u20B9'}{weeklyTotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</p>
          </div>
        </div>
        <div style={styles.summaryCard} className="glass-card expense-summary-card">
          <div style={styles.summaryIcon}>◎</div>
          <div>
            <p style={styles.summaryLabel}>Total expenses</p>
            <p style={styles.summaryValue}>{'\u20B9'}{totalExpenses.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</p>
          </div>
        </div>
      </div>

      <div style={styles.container} className="glass-card">
      <div style={styles.header}>
        <div>
          <h3 style={styles.title} className="editorial-title">Expense history</h3>
          <p style={styles.subtitle}>Review and manage your transactions.</p>
        </div>
      </div>

      <div style={styles.controls}>
        <div style={styles.searchRow}>
          <input
            className="input-field"
            type="text"
            placeholder="Search expenses..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={styles.searchInput}
          />
          <div style={styles.totalBadge}>
            <span style={styles.totalLabel}>Filtered total</span>
            <span style={styles.totalValue}>{'\u20B9'}{total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
          </div>
        </div>
        <div style={styles.filterGroup}>
          {categories.map((cat) => (
            <button
              key={cat}
              className="filter-chip"
              style={{ ...styles.filterBtn, ...(filter === cat ? styles.filterBtnActive : {}) }}
              onClick={() => setFilter(cat)}
            >
              <span style={styles.chipIcon}>{CATEGORY_META[cat]?.icon || '◌'}</span>
              <span>{cat}</span>
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div style={styles.loadingText}>Loading expenses...</div>
      ) : filtered.length === 0 ? (
        <div style={styles.emptyState}>
          <p style={styles.emptyText} className="editorial-title">No expenses yet</p>
          <p style={styles.emptySubtext}>No expenses yet — start tracking your spending by adding your first expense.</p>
          <button
            type="button"
            className="btn-primary"
            style={styles.emptyCta}
            onClick={() => onAddExpenseRequest && onAddExpenseRequest()}
          >
            + Add Expense
          </button>
        </div>
      ) : (
        <div style={styles.tableWrapper}>
          <table style={styles.table}>
            <thead>
              <tr>
                {['Date', 'Description', 'Category', 'Amount', ''].map((h) => (
                  <th key={h} style={styles.th}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((expense) => (
                <tr key={expense.id} className="table-row-hover" style={styles.tr}>
                  <td style={styles.td}><span style={styles.dateText}>{expense.date}</span></td>
                  <td style={styles.td}><span style={styles.descText}>{expense.description}</span></td>
                  <td style={styles.td}>
                    <span className={BADGE_CLASS[expense.category] || 'badge'}>{expense.category}</span>
                  </td>
                  <td style={styles.td}>
                    <span style={styles.amountText}>{'\u20B9'}{expense.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                  </td>
                  <td style={styles.td}>
                    <button className="soft-action" onClick={() => handleDelete(expense.id)} style={styles.deleteBtn} disabled={deleting === expense.id}>
                      {deleting === expense.id ? '...' : 'Delete'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      </div>
    </div>
  );
};

const styles = {
  pageWrap: { display: 'flex', flexDirection: 'column', gap: 14 },
  summaryRow: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 },
  summaryCard: { padding: 14, display: 'flex', alignItems: 'center', gap: 10, borderRadius: 14 },
  summaryIcon: {
    width: 28,
    height: 28,
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'rgba(129, 163, 187, 0.2)',
    color: '#cddbe6',
    fontSize: '0.82rem',
    fontWeight: 800,
  },
  summaryLabel: { color: 'var(--muted)', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.08em' },
  summaryValue: { color: 'var(--text)', fontWeight: 700, fontSize: '1rem' },
  container: { padding: 22 },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14, gap: 10, flexWrap: 'wrap' },
  title: { color: 'var(--text)', fontSize: '2rem' },
  subtitle: { color: 'var(--muted)', fontSize: '0.84rem', marginTop: 4 },
  totalBadge: { border: '1px solid var(--border)', background: 'rgba(35, 49, 64, 0.75)', borderRadius: 12, padding: '10px 14px', textAlign: 'right', minWidth: 170 },
  totalLabel: { color: 'var(--muted)', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.1em' },
  totalValue: { color: 'var(--text)', fontSize: '1.2rem', fontWeight: 700 },
  controls: { display: 'flex', gap: 10, marginBottom: 16, flexDirection: 'column', alignItems: 'stretch' },
  searchRow: { display: 'grid', gridTemplateColumns: '1fr auto', gap: 10, alignItems: 'center' },
  searchInput: { width: '100%', minWidth: 280 },
  filterGroup: { display: 'flex', gap: 6, flexWrap: 'wrap' },
  filterBtn: {
    border: '1px solid #4f667d',
    borderRadius: 999,
    padding: '6px 10px',
    background: 'rgba(33, 47, 62, 0.8)',
    color: '#c8d0d8',
    cursor: 'pointer',
    fontWeight: 600,
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
  },
  chipIcon: { fontSize: '0.68rem', opacity: 0.8 },
  filterBtnActive: {
    background: 'rgba(68, 88, 109, 0.55)',
    color: '#f0f3f6',
    borderColor: '#6d87a0',
  },
  tableWrapper: { overflowX: 'auto' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { textAlign: 'left', fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--muted)', padding: '10px 12px', borderBottom: '1px solid var(--border-soft)', letterSpacing: '0.1em' },
  tr: { borderBottom: '1px solid rgba(63, 82, 102, 0.5)' },
  td: { padding: '12px' },
  dateText: { color: 'var(--muted)', fontSize: '0.82rem' },
  descText: { color: 'var(--text)', fontWeight: 600 },
  amountText: { color: 'var(--text)', fontWeight: 700 },
  deleteBtn: {
    border: '1px solid #87616a',
    background: 'rgba(112, 69, 76, 0.28)',
    color: '#e2bbc3',
    borderRadius: 8,
    padding: '5px 8px',
    cursor: 'pointer',
    fontSize: '0.72rem',
    fontWeight: 700,
  },
  loadingText: { textAlign: 'center', color: 'var(--muted)', padding: 36 },
  emptyState: { textAlign: 'center', padding: 50 },
  emptyText: { color: 'var(--text)', fontSize: '2.2rem' },
  emptySubtext: { color: 'var(--muted)', marginTop: 6 },
  emptyCta: { marginTop: 16, padding: '11px 16px', fontSize: '0.74rem' },
};

export default ExpenseList;
