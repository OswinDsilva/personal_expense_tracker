import { formatINR } from '../data/mockData';
import { reportRows } from '../data/mockData';
import { ArrowDownLeft, ArrowUpRight } from 'lucide-react';

export default function ReportsView() {
  const totalIncome  = reportRows.filter(r => r.type === 'credit').reduce((s, r) => s + r.amount, 0);
  const totalExpense = reportRows.filter(r => r.type === 'debit').reduce((s, r) => s + r.amount, 0);
  const netFlow = totalIncome - totalExpense;

  return (
    <div className="animate-fade-up" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Header */}
      <div>
        <div className="text-label text-muted">Financial Grid</div>
        <h1
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '2rem',
            fontWeight: 700,
            letterSpacing: '-0.5px',
            margin: '0.25rem 0 0',
          }}
        >
          Reports
        </h1>
      </div>

      {/* Summary Row */}
      <div style={{ display: 'flex', gap: '1rem' }}>
        {[
          { label: 'Total Income', value: totalIncome, color: 'primary', icon: <ArrowDownLeft size={14} /> },
          { label: 'Total Expense', value: totalExpense, color: 'error', icon: <ArrowUpRight size={14} /> },
          { label: 'Net Flow', value: netFlow, color: netFlow >= 0 ? 'primary' : 'error', icon: null },
        ].map(({ label, value, color, icon }) => (
          <div
            key={label}
            className="metric-card"
            style={{ flex: 1, padding: '1.25rem' }}
          >
            <div className="text-label text-muted" style={{ marginBottom: '0.5rem' }}>{label}</div>
            <div
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '1.5rem',
                fontWeight: 700,
                color: `var(--${color})`,
                display: 'flex',
                alignItems: 'center',
                gap: '0.375rem',
              }}
            >
              {icon}{formatINR(Math.abs(value))}
            </div>
          </div>
        ))}
      </div>

      {/* Data Grid */}
      <div className="metric-card" style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: 'var(--surface-hi)' }}>
              {['Date', 'Description', 'Category', 'Amount', 'Type', 'Balance'].map(h => (
                <th
                  key={h}
                  style={{
                    padding: '0.875rem 1rem',
                    textAlign: h === 'Amount' || h === 'Balance' ? 'right' : 'left',
                    fontFamily: 'var(--font-label)',
                    fontSize: '0.6875rem',
                    fontWeight: 600,
                    letterSpacing: '0.08em',
                    textTransform: 'uppercase',
                    color: 'var(--on-surface-muted)',
                  }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {reportRows.map((row, i) => (
              <tr
                key={i}
                id={`report-row-${i}`}
                style={{
                  background: i % 2 === 0 ? 'var(--surface)' : 'var(--surface-low)',
                  transition: 'background 0.15s ease',
                  cursor: 'default',
                }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--surface-hi)'}
                onMouseLeave={e => e.currentTarget.style.background = i % 2 === 0 ? 'var(--surface)' : 'var(--surface-low)'}
              >
                <td style={{ padding: '0.75rem 1rem', fontFamily: 'var(--font-label)', fontSize: '0.6875rem', color: 'var(--on-surface-muted)' }}>
                  {new Date(row.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}
                </td>
                <td style={{ padding: '0.75rem 1rem', fontFamily: 'var(--font-body)', fontSize: '0.875rem', color: 'var(--on-surface)' }}>
                  {row.description}
                </td>
                <td style={{ padding: '0.75rem 1rem' }}>
                  <span
                    style={{
                      background: 'var(--surface-hi)',
                      border: '1px solid rgba(72,72,73,0.3)',
                      borderRadius: '0.375rem',
                      padding: '0.1875rem 0.5rem',
                      fontFamily: 'var(--font-label)',
                      fontSize: '0.625rem',
                      letterSpacing: '0.04em',
                      textTransform: 'uppercase',
                      color: 'var(--on-surface-muted)',
                    }}
                  >
                    {row.category}
                  </span>
                </td>
                <td
                  style={{
                    padding: '0.75rem 1rem',
                    textAlign: 'right',
                    fontFamily: 'var(--font-display)',
                    fontSize: '0.9375rem',
                    fontWeight: 600,
                    color: row.type === 'credit' ? 'var(--primary)' : 'var(--on-surface)',
                  }}
                >
                  {row.type === 'credit' ? '+' : '−'} {formatINR(row.amount)}
                </td>
                <td style={{ padding: '0.75rem 1rem' }}>
                  <span
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.25rem',
                      background: row.type === 'credit' ? 'rgba(177,255,206,0.08)' : 'rgba(255,113,108,0.08)',
                      border: `1px solid ${row.type === 'credit' ? 'rgba(177,255,206,0.2)' : 'rgba(255,113,108,0.2)'}`,
                      borderRadius: '0.375rem',
                      padding: '0.1875rem 0.5rem',
                      fontFamily: 'var(--font-label)',
                      fontSize: '0.625rem',
                      letterSpacing: '0.04em',
                      textTransform: 'uppercase',
                      color: row.type === 'credit' ? 'var(--primary)' : 'var(--error)',
                    }}
                  >
                    {row.type === 'credit' ? <ArrowDownLeft size={9} /> : <ArrowUpRight size={9} />}
                    {row.type === 'credit' ? 'Income' : 'Debit'}
                  </span>
                </td>
                <td
                  style={{
                    padding: '0.75rem 1rem',
                    textAlign: 'right',
                    fontFamily: 'var(--font-label)',
                    fontSize: '0.6875rem',
                    color: 'var(--on-surface-muted)',
                  }}
                >
                  {formatINR(row.balance)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
