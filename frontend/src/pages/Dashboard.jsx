import React, { useEffect, useState } from 'react';
import AddExpense from '../components/AddExpense';
import ExpenseList from '../components/ExpenseList';
import ForecastChart from '../components/ForecastChart';
import BudgetSummary from '../components/BudgetSummary';
import { dashboardAPI } from '../services/api';

const SidebarIcon = ({ id }) => {
  const common = { width: 17, height: 17, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round', strokeLinejoin: 'round' };

  if (id === 'overview') {
    return (
      <svg {...common}>
        <path d="M3 13h8V3H3zM13 21h8v-6h-8zM13 10h8V3h-8zM3 21h8v-6H3z" />
      </svg>
    );
  }
  if (id === 'expenses') {
    return (
      <svg {...common}>
        <path d="M5 4h14v16H5z" />
        <path d="M8 9h8M8 13h8M8 17h5" />
      </svg>
    );
  }
  if (id === 'forecast') {
    return (
      <svg {...common}>
        <path d="M4 19h16" />
        <path d="m6 15 4-4 3 3 5-6" />
      </svg>
    );
  }
  return (
    <svg {...common}>
      <path d="M4 7h16M7 4v16M4 17h16" />
    </svg>
  );
};

const Dashboard = ({ token, user, onLogout }) => {
  const COLLAPSED_WIDTH = 92;

  const [activeTab, setActiveTab] = useState('overview');
  const [dashData, setDashData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 900);
  const [showNav, setShowNav] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [period, setPeriod] = useState('monthly');
  const sidebarExpandedWidth = 268;
  const profileName = user?.name || 'User';
  const profileEmail = user?.email || '';

  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth < 900);
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  useEffect(() => {
    const fetchDashboard = async () => {
      setLoading(true);
      try {
        const data = await dashboardAPI.get(token, period);
        setDashData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, [token, refreshKey, period]);

  const onExpenseAdded = () => setRefreshKey((k) => k + 1);
  const sidebarCollapsed = !isMobile && isCollapsed;
  const sidebarWidth = isMobile ? 0 : sidebarCollapsed ? COLLAPSED_WIDTH : sidebarExpandedWidth;

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'expenses', label: 'Expenses' },
    { id: 'forecast', label: 'Forecast' },
    { id: 'budget', label: 'Budget' },
  ];

  return (
    <div style={styles.container} className="gradient-bg">
      <aside
        className={`sidebar-shell ${sidebarCollapsed ? 'is-collapsed' : ''}`}
        style={{
          ...styles.sidebar,
          width: sidebarWidth,
          ...(isMobile ? styles.sidebarMobile : {}),
          ...(isMobile && showNav ? styles.sidebarVisible : {}),
        }}
      >
        <div style={styles.brand} className="sidebar-brand">
          <div style={styles.brandLeft}>
            <div style={styles.brandIcon}>
              <svg viewBox="0 0 80 80" width="26" height="26" fill="none">
                <path d="M16 58h48" stroke="currentColor" strokeWidth="4.5" strokeLinecap="round" opacity="0.35" />
                <path d="m20 49 14-14 10 9 16-18" stroke="currentColor" strokeWidth="5.5" strokeLinecap="round" strokeLinejoin="round" />
                <path d="m54 26h12v12" stroke="currentColor" strokeWidth="4.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            {!sidebarCollapsed && (
              <div>
                <h2 style={styles.brandName} className="editorial-title">Finora</h2>
                <p style={styles.brandSub}>Smart Finance. Simplified.</p>
              </div>
            )}
          </div>
        </div>

        <div style={styles.userCard} className="sidebar-user-card">
          <div style={styles.avatar} className="avatar-badge">
            <svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="8" r="3.4" />
              <path d="M5.8 18.2c1.6-2.6 4-3.9 6.2-3.9s4.6 1.3 6.2 3.9" />
            </svg>
            <span style={styles.avatarAccent} />
          </div>
          {!sidebarCollapsed && (
            <div>
              <p style={styles.userName}>{profileName}</p>
              <p style={styles.userEmail}>{profileEmail}</p>
            </div>
          )}
        </div>

        <nav style={styles.nav}>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`sidebar-nav-item ${activeTab === tab.id ? 'is-active' : ''}`}
              style={{ ...styles.navItem, ...(activeTab === tab.id ? styles.navItemActive : {}) }}
              aria-label={tab.label}
              title={sidebarCollapsed ? tab.label : ''}
              onClick={() => {
                setActiveTab(tab.id);
                if (isMobile) setShowNav(false);
              }}
            >
              <span style={styles.navIcon}><SidebarIcon id={tab.id} /></span>
              {!sidebarCollapsed && <span>{tab.label}</span>}
            </button>
          ))}
        </nav>

        <button className="btn-ghost" style={{ width: '100%', ...styles.signoutBtn }} onClick={onLogout} aria-label="Sign out">
          {sidebarCollapsed ? (
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <path d="m16 17 5-5-5-5" />
              <path d="M21 12H9" />
            </svg>
          ) : 'Sign out'}
        </button>

        {!isMobile && (
          <button
            type="button"
            className={`sidebar-edge-toggle ${sidebarCollapsed ? 'is-collapsed' : ''}`}
            style={styles.edgeToggle}
            onClick={() => setIsCollapsed((v) => !v)}
            aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="m15 18-6-6 6-6" />
            </svg>
          </button>
        )}

      </aside>

      <main
        style={{
          ...styles.main,
          marginLeft: isMobile ? 0 : sidebarWidth,
        }}
      >
        <header style={styles.header}>
          <div>
            <h1 style={styles.pageTitle} className="editorial-title">
              {tabs.find((t) => t.id === activeTab)?.label}
            </h1>
            <p style={styles.pageSubtitle}>
              {new Date().toLocaleDateString('en-IN', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>

          <div style={styles.headerRight}>
            {dashData && (
              <div style={styles.headerStat}>
                <span style={styles.headerStatLabel}>
                  {period === 'weekly' ? 'Weekly total' : period === 'yearly' ? 'Yearly total' : 'Monthly total'}
                </span>
                <span style={styles.headerStatValue}>
                  {'\u20B9'}{dashData.total_expenses?.toLocaleString('en-IN', { minimumFractionDigits: 2 }) || '0.00'}
                </span>
              </div>
            )}
            {activeTab === 'overview' && (
              <div style={styles.periodControl} className="period-toggle" role="tablist" aria-label="Time filter">
                <div
                  className="period-indicator"
                  style={{
                    transform:
                      period === 'weekly'
                        ? 'translateX(0%)'
                        : period === 'monthly'
                          ? 'translateX(100%)'
                          : 'translateX(200%)',
                  }}
                />
                {['weekly', 'monthly', 'yearly'].map((opt) => (
                  <button
                    key={opt}
                    type="button"
                    role="tab"
                    aria-selected={period === opt}
                    className={`period-option ${period === opt ? 'is-active' : ''}`}
                    style={styles.periodOption}
                    onClick={() => setPeriod(opt)}
                  >
                    {opt.charAt(0).toUpperCase() + opt.slice(1)}
                  </button>
                ))}
              </div>
            )}
            {isMobile && (
              <button className="btn-primary" style={{ padding: '10px 14px' }} onClick={() => setShowNav((s) => !s)}>
                {showNav ? 'Close menu' : 'Menu'}
              </button>
            )}
          </div>
        </header>

        <div style={styles.content} className="fade-in">
          {activeTab === 'overview' && (
            <OverviewTab dashData={dashData} loading={loading} token={token} onExpenseAdded={onExpenseAdded} period={period} />
          )}
          {activeTab === 'expenses' && (
            <ExpenseList
              token={token}
              onExpenseAdded={onExpenseAdded}
              refreshKey={refreshKey}
              onAddExpenseRequest={() => setActiveTab('overview')}
            />
          )}
          {activeTab === 'forecast' && <ForecastChart token={token} />}
          {activeTab === 'budget' && <BudgetSummary token={token} />}
        </div>
      </main>
    </div>
  );
};

const OverviewTab = ({ dashData, loading, token, onExpenseAdded, period }) => {
  const spentSub = period === 'weekly' ? 'This week' : period === 'yearly' ? 'This year' : 'This month';
  const txSub = period === 'weekly' ? 'Weekly count' : period === 'yearly' ? 'Yearly count' : 'Recorded';
  const forecastSub = dashData?.forecast_label || (period === 'weekly' ? 'Next week' : period === 'yearly' ? 'Projected year' : 'Next month');

  const stats = [
    {
      icon: '\u20B9',
      label: 'Total spent',
      value: `\u20B9${dashData?.total_expenses?.toLocaleString('en-IN') || '0'}`,
      sub: spentSub,
      color: '#d4cab8',
    },
    {
      icon: '#',
      label: 'Transactions',
      value: dashData?.expense_count || '0',
      sub: txSub,
      color: '#b9c7da',
    },
    {
      icon: 'F',
      label: period === 'yearly' ? 'Projection' : 'Forecast',
      value: `\u20B9${dashData?.forecast_value?.toLocaleString('en-IN') || 'N/A'}`,
      sub: forecastSub,
      color: '#98ba9f',
    },
    {
      icon: 'T',
      label: 'Trend',
      value: dashData?.trend_label || 'N/A',
      sub: 'Vs previous period',
      color: '#c5b6d8',
    },
  ];

  if (loading && !dashData) {
    return (
      <div style={styles.loadingWrap}>
        <div style={styles.loader} />
        <p style={styles.loadingText}>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div key={period} style={styles.statsGrid} className="summary-switch">
        {stats.map((stat, i) => (
          <div key={i} className="stat-card fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ color: stat.color, fontWeight: 800 }}>{stat.icon}</span>
              <span style={{ ...styles.trendBadge, color: stat.color, border: `1px solid ${stat.color}` }}>{stat.sub}</span>
            </div>
            <p style={styles.statLabel}>{stat.label}</p>
            <p style={styles.statValue} className="editorial-title">{stat.value}</p>
          </div>
        ))}
      </div>

      <div style={styles.twoCol}>
        <AddExpense token={token} onExpenseAdded={onExpenseAdded} />
        <div style={styles.miniCard} className="glass-card">
          <h3 style={styles.sectionTitle} className="editorial-title">Budget status</h3>
          {dashData?.budget_summary?.length > 0 ? (
            dashData.budget_summary.map((b, i) => (
              <div key={i} style={styles.budgetRow}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ color: 'var(--text)', fontWeight: 600 }}>{b.category}</span>
                  <span style={{ color: 'var(--muted)', fontWeight: 700 }}>{b.usage_percentage}%</span>
                </div>
                <div style={styles.progressTrack}>
                  <div
                    style={{
                      ...styles.progressBar,
                      width: `${Math.min(b.usage_percentage, 100)}%`,
                      background:
                        b.status === 'over_budget'
                          ? 'linear-gradient(90deg, #b77d84, #d39ba2)'
                          : b.status === 'warning'
                            ? 'linear-gradient(90deg, #b9956d, #d0b083)'
                            : 'linear-gradient(90deg, #7f9f86, #a3c1a8)',
                    }}
                  />
                </div>
              </div>
            ))
          ) : (
            <p style={{ color: 'var(--muted)' }}>No budgets set yet. Add a budget to start tracking.</p>
          )}
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: { display: 'flex', minHeight: '100vh' },
  sidebar: {
    width: 260,
    minHeight: '100vh',
    position: 'fixed',
    left: 0,
    top: 0,
    bottom: 0,
    zIndex: 20,
    background: 'transparent',
    borderRight: 'none',
    padding: 22,
    display: 'flex',
    flexDirection: 'column',
    gap: 20,
    transition: 'transform 0.25s ease',
  },
  sidebarMobile: { transform: 'translateX(-100%)' },
  sidebarVisible: { transform: 'translateX(0)' },
  brand: { display: 'flex', alignItems: 'center', gap: 12 },
  brandLeft: { display: 'flex', alignItems: 'center', gap: 12 },
  brandIcon: {
    width: 42,
    height: 42,
    borderRadius: '50%',
    background: 'linear-gradient(138deg, #cfc1ad, #94aab9)',
    color: '#1a2834',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 700,
  },
  signoutBtn: { display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 40 },
  edgeToggle: {
    position: 'absolute',
    top: '50%',
    right: -12,
    width: 24,
    height: 46,
    borderRadius: 999,
    border: '1px solid rgba(144, 164, 183, 0.38)',
    background: 'linear-gradient(180deg, rgba(56, 74, 92, 0.94), rgba(43, 59, 75, 0.94))',
    color: '#dce6ee',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    boxShadow: '0 10px 22px rgba(9, 13, 20, 0.34)',
    transform: 'translateY(-50%)',
    zIndex: 30,
  },
  brandName: { fontSize: '1.75rem', color: 'var(--text)', lineHeight: 1 },
  brandSub: { color: 'var(--muted)', fontSize: '0.73rem', letterSpacing: '0.02em', textTransform: 'none' },
  userCard: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    background: 'rgba(40, 56, 73, 0.55)',
    border: '1px solid rgba(112, 133, 154, 0.26)',
    borderRadius: 16,
    padding: 12,
  },
  avatar: {
    width: 42,
    height: 42,
    borderRadius: '50%',
    background: 'linear-gradient(145deg, rgba(216, 230, 241, 0.22), rgba(146, 173, 193, 0.2))',
    color: '#d6e4ef',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 700,
    position: 'relative',
    boxShadow: '0 8px 18px rgba(9, 13, 20, 0.24)',
  },
  avatarAccent: {
    position: 'absolute',
    right: 1,
    bottom: 1,
    width: 8,
    height: 8,
    borderRadius: '50%',
    background: 'linear-gradient(145deg, #8ec1b7, #6b9b94)',
    border: '1px solid rgba(12, 26, 37, 0.78)',
  },
  userName: { color: 'var(--text)', fontWeight: 700 },
  userEmail: { color: 'var(--muted)', fontSize: '0.78rem' },
  nav: { display: 'flex', flexDirection: 'column', gap: 8, flex: 1 },
  navItem: {
    border: '1px solid rgba(117, 138, 160, 0.2)',
    background: 'rgba(34, 48, 63, 0.38)',
    padding: '11px 13px',
    borderRadius: 14,
    textAlign: 'left',
    color: '#cfd6de',
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    cursor: 'pointer',
    fontWeight: 600,
  },
  navItemActive: { color: '#f2f6f9', borderColor: '#7792ab' },
  navIcon: {
    width: 20,
    height: 20,
    borderRadius: 0,
    background: 'transparent',
    border: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '0.78rem',
    fontWeight: 700,
  },
  main: { flex: 1, padding: 30 },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: 14,
    marginBottom: 24,
    flexWrap: 'wrap',
  },
  pageTitle: { color: 'var(--text)', fontSize: '3.4rem', lineHeight: 0.92 },
  pageSubtitle: { color: 'var(--muted)', marginTop: 8, fontSize: '0.82rem', letterSpacing: '0.12em', textTransform: 'uppercase' },
  headerRight: { display: 'flex', alignItems: 'center', gap: 10 },
  headerStat: {
    background: 'linear-gradient(145deg, rgba(39, 53, 70, 0.8), rgba(30, 42, 57, 0.8))',
    border: '1px solid var(--border)',
    borderRadius: 14,
    padding: '12px 16px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
    boxShadow: '0 8px 22px rgba(0,0,0,0.28)',
  },
  headerStatLabel: { color: 'var(--muted)', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.1em' },
  headerStatValue: { color: 'var(--text)', fontWeight: 700, fontSize: '1.2rem' },
  periodControl: {
    position: 'relative',
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    width: 284,
    borderRadius: 999,
    border: '1px solid rgba(120, 141, 162, 0.42)',
    background: 'rgba(35, 49, 64, 0.6)',
    padding: 4,
    overflow: 'hidden',
  },
  periodOption: {
    position: 'relative',
    zIndex: 2,
    border: 'none',
    background: 'transparent',
    color: '#c7d1d9',
    fontWeight: 700,
    letterSpacing: '0.03em',
    borderRadius: 999,
    padding: '7px 10px',
    cursor: 'pointer',
  },
  content: { maxWidth: 1200 },
  statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 },
  statLabel: { color: 'var(--muted)', fontSize: '0.72rem', textTransform: 'uppercase', marginBottom: 8, letterSpacing: '0.1em' },
  statValue: { color: 'var(--text)', fontSize: '2.2rem', lineHeight: 0.95 },
  twoCol: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 },
  miniCard: { padding: 22 },
  sectionTitle: { color: 'var(--text)', marginBottom: 16, fontSize: '2rem' },
  budgetRow: { marginBottom: 14 },
  progressTrack: { height: 8, borderRadius: 6, background: 'rgba(52, 69, 86, 0.7)', overflow: 'hidden' },
  progressBar: { height: '100%', borderRadius: 6 },
  trendBadge: {
    borderRadius: 999,
    padding: '3px 10px',
    fontSize: '0.66rem',
    fontWeight: 700,
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
  },
  loadingWrap: { height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 10 },
  loader: {
    width: 38,
    height: 38,
    border: '4px solid rgba(85, 107, 127, 0.7)',
    borderTop: '4px solid #d7cab7',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  loadingText: { color: 'var(--muted)' },
};

export default Dashboard;
