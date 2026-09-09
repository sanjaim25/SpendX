import React, { useState } from 'react';
import { expenseAPI } from '../services/api';
import useAutoDismiss from '../hooks/useAutoDismiss';

const AddExpense = ({ token, onExpenseAdded }) => {
  const [form, setForm] = useState({ description: '', amount: '', date: '' });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  useAutoDismiss(success, setSuccess, 3000);
  useAutoDismiss(error, setError);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      const res = await expenseAPI.add(token, {
        ...form,
        date: form.date || new Date().toISOString().split('T')[0],
      });
      setSuccess(`Expense added under "${res.expense.category}".`);
      setForm({ description: '', amount: '', date: '' });
      onExpenseAdded();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container} className="glass-card">
      {success && (
        <div style={styles.successToast} role="status" aria-live="polite">
          <span style={styles.successIcon} aria-hidden="true">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
              <path d="m20 6-11 11-5-5" />
            </svg>
          </span>
          <span>{success}</span>
        </div>
      )}
      <h3 style={styles.title} className="editorial-title">Add expense</h3>
      <p style={styles.subtitle}>We auto-categorize each expense using your ML model.</p>

      {error && <div className="auto-dismiss-alert" style={styles.errorBox}>{error}</div>}

      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.fieldGroup}>
          <label style={styles.label}>Description</label>
          <input
            className="input-field"
            type="text"
            placeholder="Example: Grocery shopping, cab ride..."
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            required
          />
        </div>

        <div style={styles.row}>
          <div style={styles.fieldGroup}>
            <label style={styles.label}>Amount ({'\u20B9'})</label>
            <input
              className="input-field"
              type="number"
              placeholder="0.00"
              min="0.01"
              step="0.01"
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
              required
            />
          </div>
          <div style={styles.fieldGroup}>
            <label style={styles.label}>Date</label>
            <input
              className="input-field"
              type="date"
              value={form.date}
              onChange={(e) => setForm({ ...form, date: e.target.value })}
            />
          </div>
        </div>

        <div style={styles.quickAmounts}>
          {[100, 250, 500, 1000].map((amt) => (
            <button
              key={amt}
              type="button"
              className="soft-action"
              style={styles.quickBtn}
              onClick={() => setForm({ ...form, amount: amt.toString() })}
            >
              {'\u20B9'}{amt}
            </button>
          ))}
        </div>

        <button
          type="submit"
          className="btn-primary"
          style={{ width: '100%', padding: '13px', marginTop: '4px' }}
          disabled={loading}
        >
          {loading ? 'Saving...' : 'Add expense'}
        </button>
      </form>
    </div>
  );
};

const styles = {
  container: { padding: 22, position: 'relative' },
  title: { color: 'var(--text)', fontSize: '2rem', marginBottom: 4 },
  subtitle: { color: 'var(--muted)', fontSize: '0.85rem', marginBottom: 16 },
  successToast: {
    position: 'absolute',
    top: 12,
    right: 12,
    maxWidth: 'min(360px, calc(100% - 24px))',
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    padding: '10px 12px',
    border: '1px solid rgba(122, 178, 154, 0.56)',
    background: 'linear-gradient(160deg, rgba(82, 128, 110, 0.26), rgba(52, 85, 72, 0.2))',
    color: '#b9dfcf',
    borderRadius: 12,
    fontSize: '0.86rem',
    boxShadow: '0 12px 28px rgba(7, 14, 12, 0.34)',
    backdropFilter: 'blur(10px)',
    animation: 'summarySwitchIn 0.24s ease-out',
    pointerEvents: 'none',
    zIndex: 2,
  },
  successIcon: {
    width: 20,
    height: 20,
    borderRadius: '50%',
    border: '1px solid rgba(130, 194, 166, 0.6)',
    background: 'rgba(114, 174, 147, 0.22)',
    color: '#c9ebdd',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  errorBox: {
    padding: '10px 12px',
    border: '1px solid #865c64',
    background: 'rgba(118, 74, 81, 0.25)',
    color: '#e5bbc1',
    borderRadius: 12,
    marginBottom: 12,
    fontSize: '0.9rem',
  },
  form: { display: 'flex', flexDirection: 'column', gap: 14 },
  fieldGroup: { flex: 1, display: 'flex', flexDirection: 'column', gap: 6 },
  label: { color: '#c7d1d9', fontSize: '0.74rem', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.1em' },
  row: { display: 'flex', gap: 10, flexWrap: 'wrap' },
  quickAmounts: { display: 'flex', gap: 8, flexWrap: 'wrap' },
  quickBtn: {
    border: '1px solid #5a7288',
    background: 'rgba(38, 53, 69, 0.85)',
    color: '#dde5ec',
    borderRadius: 999,
    padding: '7px 12px',
    fontWeight: 700,
    cursor: 'pointer',
  },
};

export default AddExpense;
