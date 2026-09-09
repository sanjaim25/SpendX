import React, { useEffect, useMemo, useState } from 'react';
import { forecastAPI } from '../services/api';

const CHART_WIDTH = 760;
const CHART_HEIGHT = 280;
const CHART_PAD_X = 26;
const CHART_PAD_Y = 18;

const toNum = (value) => {
  const number = Number(value);
  return Number.isFinite(number) ? number : 0;
};

const buildSeries = (forecast) => {
  const months = Math.max(3, toNum(forecast?.months_analyzed || 0));
  const slope = toNum(forecast?.trend_slope || 0);
  const predicted = Math.max(0, toNum(forecast?.predicted_total || 0));
  const points = [];

  for (let i = months - 1; i >= 0; i -= 1) {
    const value = Math.max(0, predicted - slope * (i + 1));
    points.push({ label: `M-${i + 1}`, value, isPredicted: false });
  }
  points.push({ label: 'Next', value: predicted, isPredicted: true });
  return points;
};

const smoothPath = (plotPoints) => {
  if (plotPoints.length <= 1) return '';
  let path = `M ${plotPoints[0].x} ${plotPoints[0].y}`;
  for (let i = 0; i < plotPoints.length - 1; i += 1) {
    const current = plotPoints[i];
    const next = plotPoints[i + 1];
    const controlX = (current.x + next.x) / 2;
    path += ` C ${controlX} ${current.y}, ${controlX} ${next.y}, ${next.x} ${next.y}`;
  }
  return path;
};

const ForecastChart = ({ token }) => {
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hoveredIndex, setHoveredIndex] = useState(null);

  useEffect(() => {
    const fetchForecast = async () => {
      try {
        const data = await forecastAPI.get(token);
        setForecast(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchForecast();
  }, [token]);

  const trendSeries = useMemo(
    () => (forecast && forecast.status !== 'no_data' ? buildSeries(forecast) : []),
    [forecast]
  );

  if (loading) return <div style={styles.loading}>Loading forecast...</div>;

  if (!forecast || forecast.status === 'no_data') {
    return (
      <div style={styles.noData} className="glass-card">
        <h3 style={styles.noDataTitle} className="editorial-title">Not enough data yet</h3>
        <p style={styles.noDataText}>Add at least 2 months of expenses to generate a forecast.</p>
      </div>
    );
  }

  const trendColor =
    forecast.trend === 'increasing' ? '#c4959b' : forecast.trend === 'decreasing' ? '#93b6a2' : '#8caec5';

  const maxValue = Math.max(...trendSeries.map((item) => item.value), 1);
  const minValue = Math.min(...trendSeries.map((item) => item.value), 0);
  const yRange = Math.max(1, maxValue - minValue);
  const chartInnerWidth = CHART_WIDTH - CHART_PAD_X * 2;
  const chartInnerHeight = CHART_HEIGHT - CHART_PAD_Y * 2;
  const xStep = trendSeries.length > 1 ? chartInnerWidth / (trendSeries.length - 1) : chartInnerWidth;

  const plotPoints = trendSeries.map((item, idx) => {
    const ratio = (item.value - minValue) / yRange;
    return {
      ...item,
      x: CHART_PAD_X + idx * xStep,
      y: CHART_PAD_Y + chartInnerHeight * (1 - ratio),
    };
  });

  const linePath = smoothPath(plotPoints);
  const areaPath = `${linePath} L ${plotPoints[plotPoints.length - 1].x} ${CHART_HEIGHT - CHART_PAD_Y} L ${plotPoints[0].x} ${CHART_HEIGHT - CHART_PAD_Y} Z`;
  const hoveredPoint = hoveredIndex === null ? null : plotPoints[hoveredIndex];
  const categoryForecasts = Object.entries(forecast.category_forecasts || {}).sort((a, b) => b[1] - a[1]);

  return (
    <div style={styles.container}>
      <div style={styles.heroCard} className="glass-card">
        <div style={styles.heroLeft}>
          <p style={styles.heroLabel}>Predicted next month</p>
          <h1 style={styles.heroAmount} className="editorial-title">
            {'\u20B9'}{toNum(forecast.predicted_total).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </h1>
          <p style={styles.heroFor}>{forecast.forecast_for || 'N/A'}</p>
          <div style={{ ...styles.trendPill, borderColor: trendColor, color: trendColor }}>
            {forecast.trend} trend
          </div>
          <p style={styles.message}>{forecast.message}</p>
        </div>

        <div style={styles.heroRight}>
          <div style={styles.statGrid}>
            {[
              { label: 'Months analyzed', value: forecast.months_analyzed },
              { label: 'Trend slope', value: `\u20B9${toNum(forecast.trend_slope).toFixed(2)}/month` },
              { label: 'R2 score', value: toNum(forecast.r_squared).toFixed(3) },
              { label: 'Forecast for', value: forecast.forecast_for },
            ].map((stat, index) => (
              <div key={index} className="mini-stat" style={styles.miniStat}>
                <p style={styles.miniStatLabel}>{stat.label}</p>
                <p style={styles.miniStatValue}>{stat.value}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={styles.chartCard} className="glass-card">
        <div style={styles.chartHead}>
          <div>
            <h3 style={styles.sectionTitle} className="editorial-title">Spending trend projection</h3>
            <p style={styles.sectionSubtitle}>Recent trend line with projected next-month estimate.</p>
          </div>
          <div style={styles.legendPill}>Muted analytical view</div>
        </div>

        <div style={styles.chartWrap}>
          <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} style={styles.svgChart}>
            <defs>
              <linearGradient id="forecastAreaGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="rgba(131, 176, 189, 0.45)" />
                <stop offset="100%" stopColor="rgba(131, 176, 189, 0.02)" />
              </linearGradient>
            </defs>

            {[0, 1, 2, 3, 4].map((step) => {
              const y = CHART_PAD_Y + (chartInnerHeight / 4) * step;
              return (
                <line
                  key={step}
                  x1={CHART_PAD_X}
                  y1={y}
                  x2={CHART_WIDTH - CHART_PAD_X}
                  y2={y}
                  stroke="rgba(143, 161, 178, 0.22)"
                  strokeWidth="1"
                  strokeDasharray="4 6"
                />
              );
            })}

            <path d={areaPath} fill="url(#forecastAreaGradient)" />
            <path d={linePath} fill="none" stroke="#8db5c3" strokeWidth="3" strokeLinecap="round" />

            {plotPoints.map((point, idx) => (
              <g key={idx}>
                <circle
                  cx={point.x}
                  cy={point.y}
                  r={hoveredIndex === idx ? 6.2 : point.isPredicted ? 4.8 : 4}
                  fill={point.isPredicted ? '#cfc1ad' : '#8db5c3'}
                  stroke="rgba(19, 30, 43, 0.95)"
                  strokeWidth="2"
                  style={{ cursor: 'pointer', transition: 'all 0.18s ease' }}
                  onMouseEnter={() => setHoveredIndex(idx)}
                  onMouseLeave={() => setHoveredIndex(null)}
                />
                <text
                  x={point.x}
                  y={CHART_HEIGHT - 4}
                  textAnchor="middle"
                  fontSize="10"
                  fill="rgba(183, 194, 205, 0.8)"
                >
                  {point.label}
                </text>
              </g>
            ))}
          </svg>

          {hoveredPoint && (
            <div
              style={{
                ...styles.tooltip,
                left: `${(hoveredPoint.x / CHART_WIDTH) * 100}%`,
                top: `${(hoveredPoint.y / CHART_HEIGHT) * 100}%`,
              }}
            >
              <span style={styles.tooltipLabel}>{hoveredPoint.label}</span>
              <strong style={styles.tooltipValue}>
                {'\u20B9'}{hoveredPoint.value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
              </strong>
            </div>
          )}
        </div>
      </div>

      <div style={styles.categoryCard} className="glass-card">
        <h3 style={styles.sectionTitle} className="editorial-title">Category forecast</h3>
        <p style={styles.sectionSubtitle}>Projected spending split for the next month.</p>
        <div style={styles.categoryGrid}>
          {categoryForecasts.map(([category, amount]) => (
            <div key={category} style={styles.categoryItem}>
              <span style={styles.categoryName}>{category}</span>
              <span style={styles.categoryAmount}>{'\u20B9'}{toNum(amount).toLocaleString('en-IN')}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: { display: 'flex', flexDirection: 'column', gap: 16 },
  heroCard: { padding: 24, display: 'flex', gap: 20, flexWrap: 'wrap' },
  heroLeft: { flex: 1, minWidth: 240 },
  heroLabel: { color: 'var(--muted)', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: 6, letterSpacing: '0.1em' },
  heroAmount: { color: 'var(--text)', fontSize: '3.25rem', lineHeight: 0.9 },
  heroFor: { color: 'var(--muted)', marginBottom: 12 },
  trendPill: { display: 'inline-block', border: '1px solid', borderRadius: 999, padding: '5px 10px', marginBottom: 12, fontWeight: 700, textTransform: 'capitalize' },
  message: { color: '#c7cdd3', lineHeight: 1.45 },
  heroRight: { flex: 1, minWidth: 240 },
  statGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 },
  miniStat: { border: '1px solid var(--border)', borderRadius: 12, background: 'rgba(35, 49, 64, 0.76)', padding: 10 },
  miniStatLabel: { color: 'var(--muted)', fontSize: '0.7rem', textTransform: 'uppercase', marginBottom: 4, letterSpacing: '0.08em' },
  miniStatValue: { color: 'var(--text)', fontWeight: 700 },
  chartCard: { padding: 22 },
  chartHead: { display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', marginBottom: 12 },
  sectionTitle: { color: 'var(--text)', fontSize: '2rem' },
  sectionSubtitle: { color: 'var(--muted)', fontSize: '0.84rem', marginTop: 6 },
  legendPill: {
    border: '1px solid rgba(131, 170, 184, 0.36)',
    color: '#abc7d1',
    borderRadius: 999,
    padding: '6px 12px',
    fontSize: '0.72rem',
    fontWeight: 700,
    alignSelf: 'flex-start',
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
  },
  chartWrap: { position: 'relative', overflow: 'hidden', borderRadius: 16, border: '1px solid rgba(120, 142, 161, 0.22)', background: 'rgba(28, 40, 53, 0.4)' },
  svgChart: { width: '100%', height: 'auto', display: 'block' },
  tooltip: {
    position: 'absolute',
    transform: 'translate(-50%, -115%)',
    background: 'rgba(22, 34, 47, 0.96)',
    border: '1px solid rgba(126, 157, 176, 0.42)',
    borderRadius: 10,
    padding: '7px 10px',
    pointerEvents: 'none',
    boxShadow: '0 10px 24px rgba(9, 14, 20, 0.34)',
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
    minWidth: 90,
  },
  tooltipLabel: { color: '#aebbc8', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em' },
  tooltipValue: { color: '#e4edf3', fontSize: '0.9rem' },
  categoryCard: { padding: 22 },
  categoryGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 10, marginTop: 12 },
  categoryItem: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: 8,
    border: '1px solid rgba(123, 145, 164, 0.28)',
    borderRadius: 12,
    background: 'rgba(34, 48, 64, 0.56)',
    padding: '10px 12px',
  },
  categoryName: { color: '#c8d4dd', fontWeight: 600 },
  categoryAmount: { color: '#dde7ef', fontWeight: 700 },
  loading: { textAlign: 'center', color: 'var(--muted)', padding: 60 },
  noData: { padding: 40, textAlign: 'center' },
  noDataTitle: { color: 'var(--text)', marginBottom: 8, fontSize: '2rem' },
  noDataText: { color: 'var(--muted)' },
};

export default ForecastChart;
