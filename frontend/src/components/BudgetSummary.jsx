import React, { useEffect, useState } from 'react';
import { budgetAPI } from '../services/api';
import useAutoDismiss from '../hooks/useAutoDismiss';

const CATEGORIES = ['Food', 'Transport', 'Bills', 'Shopping', 'Entertainment', 'Health'];

const BudgetSummary = ({ token }) => {
  const [summary, setSummary] = useState([]);
  const [form, setForm] = useState({ category: '', monthly_limit: '' });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  useAutoDismiss(success, setSuccess);
  useAutoDismiss(error, setError);

  const fetchSummary = async () => {
    try {
      const data = await budgetAPI.getSummary(token);
      setSummary(data.summary || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, [token]);

  const handleSetBudget = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccess('');
    setError('');
    try {
      const payload = {
        category: form.category,
        monthly_limit: Number(form.monthly_limit),
      };

      if (editingId) {
        await budgetAPI.update(token, editingId, payload);
        setSuccess(`Budget updated for ${form.category}.`);
      } else {
        await budgetAPI.set(token, payload);
        setSuccess(`Budget saved for ${form.category}.`);
      }

      setForm({ category: '', monthly_limit: '' });
      setEditingId(null);
      await fetchSummary();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (item) => {
    setEditingId(item.id);
    setSuccess('');
    setError('');
    setForm({ category: item.category, monthly_limit: item.budget_limit.toString() });
  };

  const handleDelete = async (budgetId) => {
    setDeletingId(budgetId);
    setSuccess('');
    setError('');
    try {
      await budgetAPI.delete(token, budgetId);
      if (editingId === budgetId) {
        setEditingId(null);
        setForm({ category: '', monthly_limit: '' });
      }
      setSuccess('Budget deleted.');
      await fetchSummary();
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingId(null);
    }
  };

  const statusColor = (status) =>
    status === 'over_budget' ? '#bf8991' : status === 'warning' ? '#cca97f' : '#9dbfa3';

  return (
    <div style={styles.container}>
      <div style={styles.formCard} className="glass-card">
        <h3 style={styles.title} className="editorial-title">Set monthly budget</h3>
        <p style={styles.subtitle}>Define a monthly limit for each category.</p>

        {success && <div className="auto-dismiss-alert" style={styles.successBox}>{success}</div>}
        {error && <div className="auto-dismiss-alert" style={styles.errorBox}>{error}</div>}

        <form onSubmit={handleSetBudget} style={styles.form}>
          <div style={styles.formRow}>
            <div style={styles.fieldGroup}>
              <label style={styles.label}>Category</label>
              <select
                className="input-field"
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                required
              >
                <option value="" disabled>Select Category</option>
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
            <div style={styles.fieldGroup}>
              <label style={styles.label}>Monthly limit ({'\u20B9'})</label>
              <input
                className="input-field"
                type="number"
                placeholder="e.g. 3000"
                min="1"
                value={form.monthly_limit}
                onChange={(e) => setForm({ ...form, monthly_limit: e.target.value })}
                required
              />
            </div>
          </div>
          <div style={styles.actionRow}>
            <button type="submit" className="btn-gold" style={{ width: '100%', padding: '12px' }} disabled={saving}>
              {saving ? 'Saving...' : editingId ? 'Update budget' : 'Save budget'}
            </button>
            {editingId && (
              <button
                type="button"
                className="soft-action"
                style={styles.cancelBtn}
                onClick={() => {
                  setEditingId(null);
                  setForm({ category: '', monthly_limit: '' });
                  setError('');
                }}
              >
                Cancel edit
              </button>
            )}
          </div>
        </form>
      </div>

      <div>
        <h3 style={styles.title} className="editorial-title">Monthly budget overview</h3>
        <p style={{ ...styles.subtitle, marginBottom: 16 }}>Track usage and remaining amount in each category.</p>

        {loading ? (
          <div style={styles.loadingText}>Loading budget data...</div>
        ) : summary.length === 0 ? (
          <div style={styles.emptyState}>
            <p style={styles.emptyText} className="editorial-title">No budgets available</p>
            <p style={styles.emptySubtext}>Set your first budget above.</p>
          </div>
        ) : (
          <div style={styles.cardsGrid}>
            {summary.map((item) => (
              <div key={item.id} className="stat-card" style={{ borderLeft: `4px solid ${statusColor(item.status)}` }}>
                <div style={styles.cardHeader}>
                  <div>
                    <p style={styles.cardCategory}>{item.category}</p>
                    <span style={{ ...styles.statusPill, borderColor: statusColor(item.status), color: statusColor(item.status) }}>
                      {item.status.replace('_', ' ')}
                    </span>
                  </div>
                  <span style={{ ...styles.pctText, color: statusColor(item.status) }}>
                    {item.usage_percentage}%
                  </span>
                </div>
                <div style={styles.cardActions}>
                  <button type="button" className="soft-action" style={styles.editBtn} onClick={() => handleEdit(item)}>
                    Edit
                  </button>
                  <button
                    type="button"
                    className="soft-action"
                    style={styles.deleteBtn}
                    onClick={() => handleDelete(item.id)}
                    disabled={deletingId === item.id}
                  >
                    {deletingId === item.id ? 'Deleting...' : 'Delete'}
                  </button>
                </div>

                <div style={styles.progressTrack}>
                  <div
                    style={{
                      ...styles.progressBar,
                      width: `${Math.min(item.usage_percentage, 100)}%`,
                      background: statusColor(item.status),
                    }}
                  />
                </div>

                <div style={styles.cardFooter}>
                  <div style={styles.amtGroup}>
                    <span style={styles.amtLabel}>Spent</span>
                    <span style={styles.amtValue}>{'\u20B9'}{item.spent.toLocaleString('en-IN')}</span>
                  </div>
                  <div style={styles.amtGroup}>
                    <span style={styles.amtLabel}>Limit</span>
                    <span style={styles.amtValue}>{'\u20B9'}{item.budget_limit.toLocaleString('en-IN')}</span>
                  </div>
                  <div style={styles.amtGroup}>
                    <span style={styles.amtLabel}>Remaining</span>
                    <span style={{ ...styles.amtValue, color: item.remaining < 0 ? '#cb9ba3' : '#9dbfa3' }}>
                      {'\u20B9'}{Math.abs(item.remaining).toLocaleString('en-IN')}
                      {item.remaining < 0 ? ' over' : ''}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const styles = {
  container: { display: 'flex', flexDirection: 'column', gap: 20 },
  formCard: { padding: 22 },
  title: { color: 'var(--text)', fontSize: '2rem', marginBottom: 4 },
  subtitle: { color: 'var(--muted)', fontSize: '0.84rem' },
  successBox: {
    marginTop: 10,
    marginBottom: 12,
    background: 'rgba(93, 128, 112, 0.24)',
    border: '1px solid #618a82',
    color: '#b3d4c9',
    borderRadius: 10,
    padding: '10px 12px',
  },
  errorBox: {
    marginTop: 10,
    marginBottom: 12,
    background: 'rgba(117, 73, 80, 0.24)',
    border: '1px solid #865a63',
    color: '#e5bbc1',
    borderRadius: 10,
    padding: '10px 12px',
  },
  form: { marginTop: 10, display: 'flex', flexDirection: 'column', gap: 12 },
  actionRow: { display: 'flex', gap: 8, flexWrap: 'wrap' },
  cancelBtn: {
    border: '1px solid #5d768e',
    background: 'rgba(38, 53, 70, 0.86)',
    color: '#dce4ea',
    borderRadius: 12,
    padding: '12px 16px',
    cursor: 'pointer',
    fontWeight: 700,
  },
  formRow: { display: 'flex', gap: 12, flexWrap: 'wrap' },
  fieldGroup: { flex: 1, minWidth: 220, display: 'flex', flexDirection: 'column', gap: 6 },
  label: { color: '#c7d1d9', fontSize: '0.74rem', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.1em' },
  cardsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 },
  cardHeader: { display: 'flex', justifyContent: 'space-between', marginBottom: 12 },
  cardActions: { display: 'flex', gap: 8, marginBottom: 12 },
  editBtn: {
    border: '1px solid #5c748b',
    background: 'rgba(41, 57, 74, 0.86)',
    color: '#dde5ec',
    borderRadius: 10,
    padding: '5px 10px',
    cursor: 'pointer',
    fontSize: '0.72rem',
    fontWeight: 700,
  },
  deleteBtn: {
    border: '1px solid #8b656d',
    background: 'rgba(116, 74, 81, 0.27)',
    color: '#e5b9c0',
    borderRadius: 10,
    padding: '5px 10px',
    cursor: 'pointer',
    fontSize: '0.72rem',
    fontWeight: 700,
  },
  cardCategory: { color: 'var(--text)', fontWeight: 700, marginBottom: 6 },
  statusPill: { border: '1px solid', borderRadius: 999, fontSize: '0.68rem', padding: '3px 8px', textTransform: 'capitalize', fontWeight: 700 },
  pctText: { fontWeight: 700, fontSize: '1.55rem' },
  progressTrack: { height: 8, borderRadius: 999, background: '#252b34', overflow: 'hidden', marginBottom: 12 },
  progressBar: { height: '100%', borderRadius: 999 },
  cardFooter: { display: 'flex', justifyContent: 'space-between', gap: 8 },
  amtGroup: { display: 'flex', flexDirection: 'column', gap: 2 },
  amtLabel: { color: 'var(--muted)', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.08em' },
  amtValue: { color: 'var(--text)', fontWeight: 700, fontSize: '0.9rem' },
  loadingText: { textAlign: 'center', padding: 34, color: 'var(--muted)' },
  emptyState: { textAlign: 'center', padding: 42, background: 'rgba(33, 47, 62, 0.78)', border: '1px solid var(--border)', borderRadius: 16 },
  emptyText: { color: 'var(--text)', fontSize: '2rem' },
  emptySubtext: { color: 'var(--muted)', marginTop: 6 },
};

export default BudgetSummary;
