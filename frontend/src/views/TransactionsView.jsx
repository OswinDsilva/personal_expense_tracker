import { useState } from 'react';
import { Search, Filter, ArrowDownLeft, ArrowUpRight } from 'lucide-react';
import TransactionList from '../components/TransactionList';
import { transactions, formatINR } from '../data/mockData';

const ALL_CATEGORIES = ['All', ...new Set(transactions.map(tx => tx.category))];

export default function TransactionsView() {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');
  const [typeFilter, setTypeFilter] = useState('all');

  const filtered = transactions.filter(tx => {
    const matchSearch = tx.description.toLowerCase().includes(search.toLowerCase());
    const matchCat = category === 'All' || tx.category === category;
    const matchType = typeFilter === 'all' || tx.type === typeFilter;
    return matchSearch && matchCat && matchType;
  });

  const totalIn  = filtered.filter(t => t.type === 'credit').reduce((s, t) => s + t.amount, 0);
  const totalOut = filtered.filter(t => t.type === 'debit').reduce((s, t) => s + t.amount, 0);

  return (
    <div className="animate-fade-up" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Header */}
      <div>
        <div className="text-label text-muted">All Activity</div>
        <h1
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '2rem',
            fontWeight: 700,
            letterSpacing: '-0.5px',
            margin: '0.25rem 0 0',
          }}
        >
          Transactions
        </h1>
      </div>

      {/* Summary pills */}
      <div style={{ display: 'flex', gap: '0.75rem' }}>
        <div
          style={{
            background: 'rgba(177,255,206,0.08)',
            border: '1px solid rgba(177,255,206,0.2)',
            borderRadius: '0.5rem',
            padding: '0.625rem 1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <ArrowDownLeft size={14} color="var(--primary)" />
          <span className="text-label" style={{ color: 'var(--primary)' }}>In: {formatINR(totalIn)}</span>
        </div>
        <div
          style={{
            background: 'rgba(255,113,108,0.08)',
            border: '1px solid rgba(255,113,108,0.2)',
            borderRadius: '0.5rem',
            padding: '0.625rem 1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <ArrowUpRight size={14} color="var(--error)" />
          <span className="text-label" style={{ color: 'var(--error)' }}>Out: {formatINR(totalOut)}</span>
        </div>
        <div
          style={{
            background: 'var(--surface-low)',
            border: '1px solid rgba(72,72,73,0.3)',
            borderRadius: '0.5rem',
            padding: '0.625rem 1rem',
          }}
        >
          <span className="text-label text-muted">{filtered.length} transactions</span>
        </div>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
        {/* Search */}
        <div style={{ position: 'relative', flex: '1 1 240px', minWidth: '200px' }}>
          <Search
            size={14}
            style={{
              position: 'absolute',
              left: '0.875rem',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--on-surface-muted)',
              pointerEvents: 'none',
            }}
          />
          <input
            id="search-transactions"
            type="text"
            placeholder="Search transactions…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              width: '100%',
              background: 'var(--surface-low)',
              border: '1px solid rgba(72,72,73,0.3)',
              borderRadius: '0.5rem',
              padding: '0.625rem 0.875rem 0.625rem 2.375rem',
              color: 'var(--on-surface)',
              fontFamily: 'var(--font-body)',
              fontSize: '0.875rem',
              outline: 'none',
              transition: 'border-color 0.2s ease',
            }}
            onFocus={e => e.target.style.borderColor = 'rgba(177,255,206,0.4)'}
            onBlur={e => e.target.style.borderColor = 'rgba(72,72,73,0.3)'}
          />
        </div>

        {/* Type filter */}
        {['all', 'credit', 'debit'].map(t => (
          <button
            key={t}
            id={`filter-type-${t}`}
            className={typeFilter === t ? 'btn-primary' : 'btn-ghost'}
            onClick={() => setTypeFilter(t)}
            style={{ textTransform: 'capitalize' }}
          >
            {t === 'all' ? 'All' : t === 'credit' ? 'Income' : 'Expenses'}
          </button>
        ))}

        {/* Category select */}
        <select
          id="filter-category"
          value={category}
          onChange={e => setCategory(e.target.value)}
          style={{
            background: 'var(--surface-low)',
            border: '1px solid rgba(72,72,73,0.3)',
            borderRadius: '0.5rem',
            padding: '0.625rem 0.875rem',
            color: 'var(--on-surface-muted)',
            fontFamily: 'var(--font-label)',
            fontSize: '0.6875rem',
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            outline: 'none',
            cursor: 'pointer',
          }}
        >
          {ALL_CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      {/* List */}
      <div className="metric-card" style={{ padding: '0.5rem' }}>
        {filtered.length > 0
          ? <TransactionList transactions={filtered} />
          : (
            <div
              style={{
                padding: '3rem',
                textAlign: 'center',
                color: 'var(--on-surface-muted)',
                fontFamily: 'var(--font-label)',
                fontSize: '0.6875rem',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
              }}
            >
              No transactions match your filters.
            </div>
          )
        }
      </div>
    </div>
  );
}
