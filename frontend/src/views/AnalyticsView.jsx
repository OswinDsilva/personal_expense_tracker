import { CategoryBarChart, CategoryDonutChart } from '../components/Charts';
import { spendingByCategory, formatINR } from '../data/mockData';

export default function AnalyticsView() {
  const total = spendingByCategory.reduce((s, c) => s + c.value, 0);

  return (
    <div className="animate-fade-up" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      <div>
        <div className="text-label text-muted">Spending Breakdown</div>
        <h1
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '2rem',
            fontWeight: 700,
            letterSpacing: '-0.5px',
            margin: '0.25rem 0 0',
          }}
        >
          Analytics
        </h1>
      </div>

      {/* Grid: Donut + Category Legend | Bar Chart */}
      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '1.5rem' }}>

        {/* Donut + legend */}
        <div className="metric-card" style={{ padding: '1.5rem' }}>
          <div className="text-label text-muted" style={{ marginBottom: '1rem' }}>Category Split</div>
          <CategoryDonutChart />
          <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {spendingByCategory.map(cat => (
              <div
                key={cat.name}
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div style={{
                    width: 8, height: 8, borderRadius: '50%',
                    background: cat.color, flexShrink: 0,
                    boxShadow: `0 0 6px ${cat.color}60`
                  }} />
                  <span className="text-label text-muted">{cat.name}</span>
                </div>
                <span
                  style={{
                    fontFamily: 'var(--font-label)',
                    fontSize: '0.6875rem',
                    fontWeight: 600,
                    color: 'var(--on-surface)',
                  }}
                >
                  {((cat.value / total) * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Bar chart */}
        <div className="metric-card" style={{ padding: '1.5rem' }}>
          <div style={{ marginBottom: '1rem' }}>
            <div className="text-label text-muted" style={{ marginBottom: '0.25rem' }}>Monthly Spend</div>
            <div className="text-headline" style={{ color: 'var(--on-surface)' }}>By Category</div>
          </div>
          <CategoryBarChart />

          {/* Category detail cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem', marginTop: '1.25rem' }}>
            {spendingByCategory.map(cat => (
              <div
                key={cat.name}
                style={{
                  background: 'var(--surface)',
                  border: '1px solid rgba(72,72,73,0.3)',
                  borderRadius: '0.625rem',
                  padding: '0.875rem',
                  transition: 'all 0.2s ease',
                  cursor: 'default',
                }}
                onMouseEnter={e => { e.currentTarget.style.background = 'var(--surface-hi)'; e.currentTarget.style.borderColor = `${cat.color}40`; }}
                onMouseLeave={e => { e.currentTarget.style.background = 'var(--surface)'; e.currentTarget.style.borderColor = 'rgba(72,72,73,0.3)'; }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.375rem' }}>
                  <div style={{ width: 6, height: 6, borderRadius: '50%', background: cat.color, flexShrink: 0 }} />
                  <span className="text-label text-muted">{cat.name}</span>
                </div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '1rem', fontWeight: 600, color: cat.color }}>
                  {formatINR(cat.value)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
