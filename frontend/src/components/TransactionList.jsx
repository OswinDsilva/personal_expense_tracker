import { formatINR, formatDate } from '../data/mockData';
import { ArrowDownLeft, ArrowUpRight } from 'lucide-react';

export default function TransactionList({ transactions, limit }) {
  const list = limit ? transactions.slice(0, limit) : transactions;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
      {list.map((tx, i) => (
        <div
          key={tx.id}
          id={`transaction-${tx.id}`}
          className="transaction-row animate-fade-up"
          style={{ animationDelay: `${i * 40}ms` }}
        >
          {/* Icon */}
          <div
            className="transaction-icon"
            style={{
              background: tx.type === 'credit'
                ? 'rgba(177, 255, 206, 0.1)'
                : 'rgba(38, 38, 39, 1)',
              border: `1px solid ${tx.type === 'credit' ? 'rgba(177,255,206,0.2)' : 'rgba(72,72,73,0.3)'}`,
              fontSize: '1rem',
            }}
          >
            {tx.categoryIcon}
          </div>

          {/* Info */}
          <div style={{ flex: 1, minWidth: 0 }}>
            <div
              className="text-body"
              style={{
                color: 'var(--on-surface)',
                fontWeight: 500,
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {tx.description}
            </div>
            <div className="text-label text-muted" style={{ marginTop: '0.125rem' }}>
              {tx.category} • {formatDate(tx.timestamp)}
            </div>
          </div>

          {/* Amount */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.125rem' }}>
            <div
              style={{
                fontFamily: 'var(--font-display)',
                fontWeight: 600,
                fontSize: '0.9375rem',
                color: tx.type === 'credit' ? 'var(--primary)' : 'var(--on-surface)',
              }}
            >
              {tx.type === 'credit' ? '+' : '−'} {formatINR(tx.amount)}
            </div>
            <div style={{
              color: tx.type === 'credit' ? 'var(--primary-dim)' : 'var(--on-surface-muted)',
              display: 'flex', alignItems: 'center', gap: '0.125rem',
            }}>
              {tx.type === 'credit'
                ? <ArrowDownLeft size={10} />
                : <ArrowUpRight size={10} />}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
