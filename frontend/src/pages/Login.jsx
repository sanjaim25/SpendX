import React, { useState } from 'react';
import { authAPI } from '../services/api';
import useAutoDismiss from '../hooks/useAutoDismiss';

const Login = ({ onLogin }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  useAutoDismiss(error, setError);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      let data;
      if (isRegister) {
        await authAPI.register(form);
        data = await authAPI.login({ email: form.email, password: form.password });
      } else {
        data = await authAPI.login({ email: form.email, password: form.password });
      }
      onLogin(data.access_token, data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container} className="gradient-bg login-bg">
      <div style={styles.blobA} />
      <div style={styles.blobB} />

      <div style={styles.wrapper} className="fade-in">
        <div style={styles.logoArea}>
          <div style={styles.logoIcon} className="login-logo-mark" aria-hidden="true">
            <svg viewBox="0 0 80 80" width="42" height="42" fill="none">
              <path d="M16 23c7-8 26-9 33-1 6 6 2 14-10 16l-10 2c-12 2-16 11-10 18 7 8 25 8 35-1" stroke="currentColor" strokeWidth="5.5" strokeLinecap="round"/>
              <path d="M29 18h25M26 62h28" stroke="currentColor" strokeWidth="4.6" strokeLinecap="round" opacity="0.75"/>
            </svg>
          </div>
          <h1 style={styles.logoText} className="editorial-title">Finora</h1>
          <div className="ornament" style={{ margin: '10px 0' }}>Smart spend intelligence</div>
          <p style={styles.tagline}>Track better, spend wiser, stay in control.</p>
        </div>

        <div style={styles.card} className="glass-card login-card">
          <h2 style={styles.cardTitle} className="editorial-title">{isRegister ? 'Create account' : 'Welcome back'}</h2>
          <p style={styles.cardSubtitle}>
            {isRegister ? 'Set up your Finora profile' : 'Sign in to continue'}
          </p>

          {error && <div className="auto-dismiss-alert" style={styles.errorBox}>Warning: {error}</div>}

          <form onSubmit={handleSubmit} style={styles.form}>
            {isRegister && (
              <div style={styles.formGroup}>
                <label style={styles.label}>Full name</label>
                <input
                  className="input-field"
                  type="text"
                  placeholder="Your full name"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                />
              </div>
            )}
            <div style={styles.formGroup}>
              <label style={styles.label}>Email</label>
              <input
                className="input-field"
                type="email"
                placeholder="your@email.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>Password</label>
              <input
                className="input-field"
                type="password"
                placeholder="Enter password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
              />
            </div>

            <button
              type="submit"
              className="btn-primary"
              style={{ width: '100%', padding: '14px', marginTop: '8px' }}
              disabled={loading}
            >
              {loading ? 'Please wait...' : isRegister ? 'Create account' : 'Sign in'}
            </button>
          </form>

          <div className="ornament" style={{ margin: '20px 0' }}>or</div>

          <p style={styles.switchText}>
            {isRegister ? 'Already have an account? ' : "Don't have an account? "}
            <span style={styles.switchLink} onClick={() => setIsRegister(!isRegister)}>
              {isRegister ? 'Sign in' : 'Register'}
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '24px',
    position: 'relative',
    overflow: 'hidden',
  },
  blobA: {
    position: 'absolute',
    width: '460px',
    height: '460px',
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(186,177,160,0.14) 0%, rgba(186,177,160,0) 70%)',
    top: '-160px',
    left: '-140px',
    pointerEvents: 'none',
  },
  blobB: {
    position: 'absolute',
    width: '520px',
    height: '520px',
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(131,139,158,0.16) 0%, rgba(131,139,158,0) 70%)',
    bottom: '-200px',
    right: '-150px',
    pointerEvents: 'none',
  },
  wrapper: { width: '100%', maxWidth: '468px', position: 'relative', zIndex: 1 },
  logoArea: { textAlign: 'center', marginBottom: '24px' },
  logoIcon: {
    width: '72px',
    height: '72px',
    borderRadius: '50%',
    margin: '0 auto 14px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 700,
    color: '#253746',
    background: 'linear-gradient(138deg, #d9ccbb, #a4b8c7)',
    boxShadow: '0 14px 30px rgba(11, 16, 24, 0.28)',
  },
  logoText: { color: 'var(--text)', fontSize: '3.2rem', lineHeight: 1 },
  tagline: { color: 'var(--muted)', fontSize: '0.95rem' },
  card: { padding: '32px' },
  cardTitle: { color: 'var(--text)', fontSize: '2.15rem', marginBottom: '4px' },
  cardSubtitle: { color: 'var(--muted)', marginBottom: '22px' },
  errorBox: {
    marginBottom: '14px',
    padding: '10px 12px',
    borderRadius: '12px',
    background: 'rgba(118, 74, 81, 0.24)',
    color: '#e5bbc1',
    border: '1px solid #835861',
    fontSize: '0.9rem',
  },
  form: { display: 'flex', flexDirection: 'column', gap: '14px' },
  formGroup: { display: 'flex', flexDirection: 'column', gap: '6px' },
  label: { color: '#c8d2da', fontSize: '0.76rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em' },
  switchText: { textAlign: 'center', color: 'var(--muted)', fontSize: '0.92rem' },
  switchLink: { color: '#d9e2e9', cursor: 'pointer', fontWeight: 700, textDecoration: 'underline' },
};

export default Login;
