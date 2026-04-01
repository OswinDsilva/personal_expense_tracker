import { useEffect, useMemo, useState } from 'react';
import { BarChart2, ArrowRight } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import TransactionList from '../components/TransactionList';
import { SpendingTrendChart } from '../components/Charts';
import { getMonthlyData, getTransactions, getYearlyData } from '../lib/api';

const CATEGORY_ICON_MAP = {
  Income: '💼',
  Shopping: '🛍️',
  Entertainment: '🎬',
  Health: '💊',
  Dining: '🍽️',
  Utilities: '⚡',
  Transport: '🚕',
  'Food & Grocery': '🛒',
};

const MONTH_NAMES = [
  'Jan',
  'Feb',
  'Mar',
  'Apr',
  'May',
  'Jun',
  'Jul',
  'Aug',
  'Sep',
  'Oct',
  'Nov',
  'Dec',
];

const FULL_MONTH_NAMES = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
];

export default function DashboardView({ onNavigate, transactionsRefreshTick }) {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;

  const [monthlyData, setMonthlyData] = useState(null);
  const [yearlyData, setYearlyData] = useState(null);
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isTrendLoading, setIsTrendLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');
  const [trendErrorMessage, setTrendErrorMessage] = useState('');

  useEffect(() => {
    const loadDashboard = async () => {
      setIsLoading(true);
      setIsTrendLoading(true);
      setErrorMessage('');
      setTrendErrorMessage('');

      const yearlyPromise = getYearlyData(year)
        .then((data) => ({ data, error: null }))
        .catch((error) => ({ data: null, error }));

      try {
        const [monthly, recent] = await Promise.all([
          getMonthlyData(year, month),
          getTransactions({ limit: 5 }),
        ]);

        setMonthlyData(monthly);
        setRecentTransactions(recent.data || []);
      } catch (error) {
        setErrorMessage(error.message || 'Failed to load dashboard data');
      } finally {
        setIsLoading(false);
      }

      const yearlyResult = await yearlyPromise;
      if (yearlyResult.error) {
        setYearlyData(null);
        setTrendErrorMessage(yearlyResult.error.message || 'Failed to load trend data');
      } else {
        setYearlyData(yearlyResult.data);
      }
      setIsTrendLoading(false);
    };

    loadDashboard();
  }, [month, transactionsRefreshTick, year]);

  const summaryData = useMemo(() => {
    if (!monthlyData) {
      return {
        cashBalance: 0,
        upiBalance: 0,
        totalSpending: 0,
        totalIncome: 0,
        month: `${FULL_MONTH_NAMES[month - 1]} ${year}`,
        spendingChange: 0,
        incomeChange: 0,
      };
    }

    const totalSpending = Number(monthlyData.totals.cash_spending) + Number(monthlyData.totals.upi_spending);
    const totalIncome = Number(monthlyData.totals.cash_income) + Number(monthlyData.totals.upi_income);

    return {
      cashBalance: Number(monthlyData.ending_balance.cash),
      upiBalance: Number(monthlyData.ending_balance.upi),
      totalSpending,
      totalIncome,
      month: `${FULL_MONTH_NAMES[month - 1]} ${year}`,
    };
  }, [month, monthlyData, year]);

  const trendData = useMemo(() => {
    if (!yearlyData?.monthly_breakdown) return [];

    return yearlyData.monthly_breakdown
      .map((entry) => ({
        monthNumber: Number(entry.month),
        month: MONTH_NAMES[Number(entry.month) - 1] ?? `M${entry.month}`,
        spending: Number(entry.total_spending.cash) + Number(entry.total_spending.upi),
        income: Number(entry.total_income.cash) + Number(entry.total_income.upi),
      }))
      .sort((a, b) => a.monthNumber - b.monthNumber);
  }, [yearlyData]);

  const transactionsForList = useMemo(
    () =>
      recentTransactions.map((tx) => {
        const isCredit = tx.transaction_type === 'INCOME' || (tx.transaction_type === 'TRANSFER' && tx.is_debit === false);
        const categoryName = tx.category?.name || (isCredit ? 'Income' : 'Uncategorized');

        return {
          id: tx.id,
          description: tx.description,
          category: categoryName,
          categoryIcon: CATEGORY_ICON_MAP[categoryName] || (isCredit ? '💰' : '🧾'),
          amount: Number(tx.amount),
          type: isCredit ? 'credit' : 'debit',
          timestamp: tx.created_at,
        };
      }),
    [recentTransactions]
  );

  return (
    <div className="view-shell animate-fade-up">
      {/* Page Header */}
      <div className="view-header">
        <div>
          <div className="text-label text-muted">Overview</div>
          <h1 className="view-title" style={{ margin: '0.25rem 0 0', color: 'var(--on-surface)' }}>
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

      {errorMessage ? (
        <div className="metric-card" style={{ padding: '0.9rem 1rem', color: 'var(--error)' }}>
          {errorMessage}
        </div>
      ) : null}

      {/* Metric Cards */}
      <div className="metrics-grid">
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
          colorAccent="tertiary"
          delay={120}
        />
        <MetricCard
          label="Total Income"
          value={summaryData.totalIncome}
          colorAccent="primary"
          delay={180}
        />
      </div>

      {/* Charts + Transactions row */}
      <div className="dashboard-split-grid">
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
          {isTrendLoading ? (
            <div className="text-label text-muted" style={{ padding: '2rem 0.25rem' }}>Loading trend...</div>
          ) : trendErrorMessage ? (
            <div className="text-label" style={{ padding: '2rem 0.25rem', color: 'var(--error)' }}>
              {trendErrorMessage}
            </div>
          ) : trendData.length === 0 ? (
            <div className="text-label text-muted" style={{ padding: '2rem 0.25rem' }}>No trend data available</div>
          ) : (
            <SpendingTrendChart data={trendData} />
          )}
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
          {isLoading ? (
            <div className="text-label text-muted" style={{ padding: '1rem 0.25rem' }}>Loading transactions...</div>
          ) : (
            <TransactionList transactions={transactionsForList} limit={5} />
          )}
        </div>
      </div>
    </div>
  );
}
