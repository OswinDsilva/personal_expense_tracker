import { TrendingUp, TrendingDown } from 'lucide-react';

const formatMetricINR = (value) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value || 0));

export default function MetricCard({ label, value, change, colorAccent = 'primary', style = {}, delay = 0 }) {
  const isPositive = change >= 0;
  const colorMap = {
    primary: 'var(--primary)',
    secondary: 'var(--secondary)',
    tertiary: 'var(--tertiary)',
    error: 'var(--error)',
  };
  const accentColor = colorMap[colorAccent] || colorMap.primary;

  return (
    <div
      className="metric-card animate-fade-up"
      style={{ animationDelay: `${delay}ms`, ...style }}
    >
      {/* Decorative accent bar */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '2px',
          background: `linear-gradient(90deg, ${accentColor} 0%, transparent 100%)`,
          borderRadius: '1rem 1rem 0 0',
        }}
      />

      <div className="text-label text-muted" style={{ marginBottom: '0.75rem' }}>
        {label}
      </div>

      <div
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '1.875rem',
          fontWeight: 700,
          color: 'var(--on-surface)',
          letterSpacing: '-0.5px',
          lineHeight: 1.1,
        }}
      >
        {formatMetricINR(value)}
      </div>

      {change !== undefined && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.25rem',
            marginTop: '0.5rem',
            color: isPositive ? 'var(--primary)' : 'var(--error)',
            fontFamily: 'var(--font-label)',
            fontSize: '0.6875rem',
            fontWeight: 600,
            letterSpacing: '0.04em',
          }}
        >
          {isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
          {isPositive ? '+' : ''}{change}% vs last month
        </div>
      )}
    </div>
  );
}
