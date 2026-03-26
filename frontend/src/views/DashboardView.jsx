import { BarChart2, ArrowRight } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import TransactionList from '../components/TransactionList';
import { SpendingTrendChart } from '../components/Charts';
import { summaryData, transactions } from '../data/mockData';

export default function DashboardView({ onNavigate }) {
  return (
    <div
      className="animate-fade-up"
      style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '2rem' }}
    >
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div>
          <div className="text-label text-muted">Kharcha Overview</div>
          <h1
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '2rem',
              fontWeight: 700,
              letterSpacing: '-0.5px',
              margin: '0.25rem 0 0',
              color: 'var(--on-surface)',
            }}
          >
            {summaryData.month}
          </h1>
        </div>
        <button
          id="btn-view-reports"
          className="btn-ghost"
          onClick={() => onNavigate('reports')}
          style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}
        >
          <BarChart2 size={13} />
          View Reports
        </button>
      </div>

      {/* Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
        <MetricCard
          label="Cash Balance"
          value={summaryData.cashBalance}
          colorAccent="primary"
          delay={0}
        />
        <MetricCard
          label="UPI Balance"
          value={summaryData.upiBalance}
          colorAccent="secondary"
          delay={60}
        />
        <MetricCard
          label="Total Spending"
          value={summaryData.totalSpending}
          change={summaryData.spendingChange}
          colorAccent="tertiary"
          delay={120}
        />
        <MetricCard
          label="Total Income"
          value={summaryData.totalIncome}
          change={summaryData.incomeChange}
          colorAccent="primary"
          delay={180}
        />
      </div>

      {/* Charts + Transactions row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '1.5rem' }}>
        {/* Trend Chart */}
        <div className="metric-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div>
              <div className="text-label text-muted">6-Month Trend</div>
              <div className="text-headline" style={{ color: 'var(--on-surface)', marginTop: '0.125rem' }}>
                Income vs Spending
              </div>
            </div>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontFamily: 'var(--font-label)', fontSize: '0.6875rem', color: 'var(--primary)' }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--primary)', display: 'inline-block' }} />
                Income
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontFamily: 'var(--font-label)', fontSize: '0.6875rem', color: 'var(--secondary)' }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--secondary)', display: 'inline-block' }} />
                Spending
              </span>
            </div>
          </div>
          <SpendingTrendChart />
        </div>

        {/* Recent Transactions */}
        <div className="metric-card" style={{ padding: '1.25rem', overflow: 'hidden' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div className="text-headline" style={{ color: 'var(--on-surface)' }}>Recent</div>
            <button
              id="btn-view-all-transactions"
              className="btn-ghost"
              onClick={() => onNavigate('transactions')}
              style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', padding: '0.375rem 0.625rem' }}
            >
              View All <ArrowRight size={11} />
            </button>
          </div>
          <TransactionList transactions={transactions} limit={5} />
        </div>
      </div>
    </div>
  );
}
