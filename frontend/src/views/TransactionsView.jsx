import { useEffect, useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight, CreditCard, Send, CalendarDays, CalendarClock } from 'lucide-react';
import { getCategories, getTransactions } from '../lib/api';

const ITEMS_PER_PAGE = 10;
const METHOD_OPTIONS = ['all', 'CASH', 'UPI'];

const formatINR = (value) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value || 0));

const formatDate = (value) =>
  new Date(value).toLocaleDateString('en-IN', {
    month: 'short',
    day: '2-digit',
    year: 'numeric',
  });

const mapTypeFilter = (typeFilter) => {
  if (typeFilter === 'income') return 'INCOME';
  if (typeFilter === 'expense') return 'EXPENSE';
  if (typeFilter === 'transfer') return 'TRANSFER';
  return undefined;
};

const amountSign = (tx) => {
  if (tx.transaction_type === 'INCOME') return '+';
  if (tx.transaction_type === 'TRANSFER') return tx.is_debit ? '−' : '+';
  return '−';
};

const amountColor = (tx) => {
  if (tx.transaction_type === 'INCOME') return 'var(--primary)';
  if (tx.transaction_type === 'TRANSFER' && !tx.is_debit) return 'var(--primary)';
  return 'var(--on-surface)';
};

export default function TransactionsView({ onNavigate, transactionsRefreshTick, categoriesRefreshTick }) {
  const [records, setRecords] = useState([]);
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const [typeFilter, setTypeFilter] = useState('all');
  const [methodFilter, setMethodFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');

  const [cursor, setCursor] = useState(null);
  const [cursorStack, setCursorStack] = useState([]);
  const [pagination, setPagination] = useState({ has_more: false, next_cursor: null });

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const data = await getCategories();
        setCategories(data);
      } catch (error) {
        console.error('Error loading categories:', error);
      }
    };

    loadCategories();
  }, [categoriesRefreshTick]);

  useEffect(() => {
    const loadTransactions = async () => {
      setIsLoading(true);
      setErrorMessage('');

      try {
        const data = await getTransactions({
          limit: ITEMS_PER_PAGE,
          cursor,
          start_date: fromDate || undefined,
          end_date: toDate || undefined,
          category_id: categoryFilter === 'all' ? undefined : categoryFilter,
          transaction_type: mapTypeFilter(typeFilter),
          payment_method: methodFilter === 'all' ? undefined : methodFilter,
        });

        setRecords(data.data || []);
        setPagination(data.pagination || { has_more: false, next_cursor: null });
      } catch (error) {
        setErrorMessage(error.message || 'Failed to load transactions');
        setRecords([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadTransactions();
  }, [cursor, fromDate, toDate, categoryFilter, typeFilter, methodFilter, transactionsRefreshTick]);

  const categoryOptions = useMemo(() => ['all', ...categories], [categories]);

  const resetCursorForFilter = () => {
    setCursor(null);
    setCursorStack([]);
  };

  const handlePrevPage = () => {
    if (cursorStack.length === 0) return;
    const previousCursor = cursorStack[cursorStack.length - 1];
    setCursorStack((prev) => prev.slice(0, -1));
    setCursor(previousCursor);
  };

  const handleNextPage = () => {
    if (!pagination.has_more || !pagination.next_cursor) return;
    setCursorStack((prev) => [...prev, cursor]);
    setCursor(pagination.next_cursor);
  };

  return (
    <div className="view-shell">
      <header className="transactions-v2-header">
        <div>
          <h1 className="view-title">Transactions</h1>
          <p className="text-label text-muted">Complete transaction ledger and history.</p>
        </div>
        <button className="btn-transactions-export" onClick={() => onNavigate?.('reports')}>
          View Reports
        </button>
      </header>

      <section className="transactions-v2-filters">
        <div className="transactions-filters-grid">
          <div className="date-range-group">
            <div className="filter-group">
              <label className="filter-label">From</label>
              <div className="filter-control-shell">
                <CalendarDays size={16} />
                <input
                  type="date"
                  value={fromDate}
                  onChange={(e) => {
                    setFromDate(e.target.value);
                    resetCursorForFilter();
                  }}
                  className="filter-date-input"
                />
              </div>
            </div>
            <div className="filter-group">
              <label className="filter-label">To</label>
              <div className="filter-control-shell">
                <CalendarClock size={16} />
                <input
                  type="date"
                  value={toDate}
                  onChange={(e) => {
                    setToDate(e.target.value);
                    resetCursorForFilter();
                  }}
                  className="filter-date-input"
                />
              </div>
            </div>
          </div>

          <div className="filter-group">
            <label className="filter-label">Type</label>
            <select
              value={typeFilter}
              onChange={(e) => {
                setTypeFilter(e.target.value);
                resetCursorForFilter();
              }}
              className="filter-select"
            >
              <option value="all">All Types</option>
              <option value="expense">Expense</option>
              <option value="income">Income</option>
              <option value="transfer">Transfer</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Method</label>
            <select
              value={methodFilter}
              onChange={(e) => {
                setMethodFilter(e.target.value);
                resetCursorForFilter();
              }}
              className="filter-select"
            >
              <option value="all">All Methods</option>
              {METHOD_OPTIONS.filter((value) => value !== 'all').map((method) => (
                <option key={method} value={method}>
                  {method}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Category</label>
            <select
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value);
                resetCursorForFilter();
              }}
              className="filter-select"
            >
              {categoryOptions.map((category) => (
                <option key={typeof category === 'string' ? category : category.id} value={typeof category === 'string' ? category : category.id}>
                  {typeof category === 'string' ? 'All Categories' : category.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </section>

      <section className="transactions-v2-ledger">
        {errorMessage ? (
          <div className="ledger-empty">{errorMessage}</div>
        ) : isLoading ? (
          <div className="ledger-empty">Loading transactions...</div>
        ) : records.length > 0 ? (
          <>
            <div className="ledger-table-wrapper">
              <table className="ledger-table">
                <thead>
                  <tr className="ledger-head-labels">
                    <th className="ledger-row-number"></th>
                    <th className="ledger-col ledger-col-date">Date</th>
                    <th className="ledger-col ledger-col-description">Description</th>
                    <th className="ledger-col ledger-col-category">Category</th>
                    <th className="ledger-col ledger-col-method text-center">Method</th>
                    <th className="ledger-col ledger-col-amount text-right">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map((tx, index) => (
                    <tr key={tx.id} className={`ledger-row ${index % 2 === 1 ? 'alternate' : ''}`}>
                      <td className="ledger-row-number">{index + 1}</td>
                      <td className="ledger-col ledger-col-date text-muted">
                        {formatDate(tx.transaction_date).toUpperCase()}
                      </td>
                      <td className="ledger-col ledger-col-description">
                        <div className="transaction-main">{tx.description}</div>
                        <div className="transaction-sub text-muted">{tx.category?.name || 'Uncategorized'}</div>
                      </td>
                      <td className="ledger-col ledger-col-category">
                        <span className="category-badge">{tx.category?.name || 'Uncategorized'}</span>
                      </td>
                      <td className="ledger-col ledger-col-method text-center">
                        <span className="method-icon text-muted">
                          {tx.payment_method === 'UPI' ? <Send size={18} /> : <CreditCard size={18} />}
                        </span>
                      </td>
                      <td
                        className="ledger-col ledger-col-amount text-right"
                        style={{
                          color: amountColor(tx),
                          fontWeight: 600,
                        }}
                      >
                        {amountSign(tx)}{formatINR(tx.amount)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="ledger-footer">
              <div className="ledger-footer-info">
                Showing {records.length} entries
              </div>
              <div className="ledger-pagination">
                <button
                  className="pagination-button"
                  onClick={handlePrevPage}
                  disabled={cursorStack.length === 0}
                >
                  <ChevronLeft size={18} />
                </button>
                <button
                  className="pagination-button"
                  onClick={handleNextPage}
                  disabled={!pagination.has_more || !pagination.next_cursor}
                >
                  <ChevronRight size={18} />
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="ledger-empty">No transactions match your filters.</div>
        )}
      </section>
    </div>
  );
}
