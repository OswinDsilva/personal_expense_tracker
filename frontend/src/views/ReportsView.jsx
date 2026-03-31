import { useEffect, useState } from 'react';
import {
  ChevronDown,
  Lock,
  Download,
} from 'lucide-react';
import { getPreviewMonthly, getPreviewYearly, downloadMonthlyExport, downloadYearlyExport, downloadFullYearExport } from '../lib/api';

const PERIODS = ['Monthly', 'Yearly'];
const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const CURRENT_YEAR = 2026;
const YEARS_AVAILABLE = [2026, 2025, 2024];
const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

const isNoDataPreviewError = (message) => {
  if (!message) return false;
  const normalized = String(message).toLowerCase();
  return (
    normalized.includes('starting balance')
    || normalized.includes('starting balances not found')
    || normalized.includes('no starting balance')
  );
};

const isNetworkFetchError = (message) => {
  if (!message) return false;
  const normalized = String(message).toLowerCase();
  return (
    normalized.includes('networkerror when attempting to fetch resource')
    || normalized.includes('failed to fetch')
    || normalized.includes('load failed')
  );
};

const isApiUnavailable = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return !response.ok;
  } catch {
    return true;
  }
};

const formatDetailedCurrency = (value) => {
  if (value === null || value === undefined) return '';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

export default function ReportsView() {
  const [period, setPeriod] = useState('Monthly');
  const [selectedYear, setSelectedYear] = useState(CURRENT_YEAR);
  const [selectedMonth, setSelectedMonth] = useState(3); // March
  const [previewData, setPreviewData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [isExporting, setIsExporting] = useState(false);
  const gridRows = Array.isArray(previewData?.grid) ? previewData.grid : [];
  const numericColumns = Array.isArray(previewData?.cell_types?.numeric_columns)
    ? previewData.cell_types.numeric_columns
    : [];

  // Generate list of available months (only past months for current year)
  const getAvailableMonths = () => {
    const months = [];
    const maxMonth = selectedYear === CURRENT_YEAR ? new Date().getMonth() + 1 : 12;
    for (let i = 1; i <= maxMonth; i++) {
      months.push({ value: i, label: MONTH_NAMES[i - 1] });
    }
    return months;
  };

  // Fetch preview data when period, year, or month changes
  useEffect(() => {
    const loadPreview = async () => {
      setIsLoading(true);
      setErrorMessage('');
      try {
        const data = period === 'Monthly'
          ? await getPreviewMonthly(selectedYear, selectedMonth)
          : await getPreviewYearly(selectedYear);
        // Accept both direct and wrapped response formats.
        const normalized = data?.grid ? data : (data?.data?.grid ? data.data : null);
        setPreviewData(normalized);
      } catch (error) {
        const message = error?.message || 'Failed to load report';

        // Missing starting balance means there is no period data to preview yet.
        if (isNoDataPreviewError(message)) {
          setErrorMessage('');
          setPreviewData(null);
          return;
        }

        // Only show network fetch errors when the API is truly unreachable.
        if (isNetworkFetchError(message)) {
          const unavailable = await isApiUnavailable();
          if (!unavailable) {
            setErrorMessage('');
            setPreviewData(null);
            return;
          }
        }

        setErrorMessage(message);
        setPreviewData(null);
      } finally {
        setIsLoading(false);
      }
    };

    loadPreview();
  }, [period, selectedYear, selectedMonth]);

  const handleExport = async () => {
    setIsExporting(true);
    try {
      if (period === 'Monthly') {
        await downloadMonthlyExport(selectedYear, selectedMonth);
      } else {
        await downloadYearlyExport(selectedYear);
      }
    } catch (error) {
      setErrorMessage(error.message || 'Failed to export report');
    } finally {
      setIsExporting(false);
    }
  };

  const handleFullYearExport = async () => {
    setIsExporting(true);
    try {
      await downloadFullYearExport(selectedYear);
    } catch (error) {
      setErrorMessage(error.message || 'Failed to export full year report');
    } finally {
      setIsExporting(false);
    }
  };

  // Helper function to check if a cell is part of a merged group
  const isMergedCell = (rowIdx, colIdx) => {
    if (!Array.isArray(previewData?.merges)) return null;
    return previewData.merges.find(
      (merge) => rowIdx > merge.r1 && rowIdx <= merge.r2 && colIdx >= merge.c1 && colIdx <= merge.c2
    );
  };

  // Helper function to check if a cell is the header of a merged group
  const isMergeStart = (rowIdx, colIdx) => {
    if (!Array.isArray(previewData?.merges)) return false;
    return previewData.merges.find(
      (merge) => rowIdx === merge.r1 && colIdx === merge.c1
    );
  };

  const getMergeColspan = (rowIdx, colIdx) => {
    const merge = previewData?.merges?.find(
      (m) => rowIdx === m.r1 && colIdx === m.c1
    );
    return merge ? merge.c2 - merge.c1 + 1 : 1;
  };

  const formatCellValue = (value, rowIdx, colIdx) => {
    void rowIdx;
    if (value === null || value === undefined) return '';
    // Check if this column is numeric
    if (numericColumns.includes(colIdx) && typeof value === 'number') {
      return formatDetailedCurrency(value);
    }
    return String(value);
  };

  const availableMonths = getAvailableMonths();

  return (
    <div className="view-shell reports-v2-shell animate-fade-up">
      <header className="reports-v2-header">
        <div>
          <h1 className="reports-v2-title">Reports</h1>
          <p className="reports-v2-subtitle">Surgical analysis of your capital allocation.</p>
        </div>

        <div className="reports-v2-period-switch" role="tablist" aria-label="Report period">
          {PERIODS.map((item) => (
            <button
              key={item}
              type="button"
              className={`reports-v2-switch-btn${period === item ? ' active' : ''}`}
              onClick={() => setPeriod(item)}
            >
              {item}
            </button>
          ))}
        </div>

        <button
          type="button"
          className="reports-v2-export-btn"
          onClick={handleFullYearExport}
          disabled={isExporting}
          title={`Export full year ${selectedYear} report`}
        >
          <Download size={16} />
          Export Full Year
        </button>
      </header>

      <section className="reports-v2-filters" aria-label="Report filters">
        {period === 'Monthly' && (
          <label className="reports-v2-filter-group">
            <span className="reports-v2-filter-label">Period Month</span>
            <div className="reports-v2-select-wrap">
              <select
                value={selectedMonth}
                onChange={(event) => setSelectedMonth(parseInt(event.target.value, 10))}
                className="reports-v2-select"
              >
                {availableMonths.map((item) => (
                  <option key={item.value} value={item.value}>{item.label}</option>
                ))}
              </select>
              <ChevronDown size={16} className="reports-v2-select-icon" />
            </div>
          </label>
        )}

        <label className="reports-v2-filter-group">
          <span className="reports-v2-filter-label">Fiscal Year</span>
          <div className="reports-v2-select-wrap">
            <select
              value={selectedYear}
              onChange={(event) => setSelectedYear(parseInt(event.target.value, 10))}
              className="reports-v2-select"
            >
              {YEARS_AVAILABLE.map((year) => (
                <option key={year} value={year}>FY {year}-{year + 1}</option>
              ))}
            </select>
            <ChevronDown size={16} className="reports-v2-select-icon" />
          </div>
        </label>

        <div className="reports-v2-filter-group reports-v2-filter-disabled" aria-disabled="true">
          <span className="reports-v2-filter-label">Sub-Category</span>
          <div className="reports-v2-disabled-input">
            <Lock size={13} />
            <span>All Categories</span>
          </div>
        </div>
      </section>

      <section className="reports-v2-ledger-shell" aria-label="Statement ledger">
        <div className="reports-v2-ledger-head">
          <div className="reports-v2-ledger-title-wrap">
            <span className="reports-v2-ledger-stripe" aria-hidden="true" />
            <h2 className="reports-v2-ledger-title">Statement Ledger</h2>
          </div>

          <button
            type="button"
            className="reports-v2-export-btn"
            onClick={handleExport}
            disabled={isLoading || isExporting || !previewData}
          >
            <Download size={16} />
            {isExporting ? 'Exporting...' : 'Export Report'}
          </button>
        </div>

        {errorMessage && (
          <div className="error-message" style={{ padding: '12px', marginBottom: '12px', color: '#dc2626' }}>
            {errorMessage}
          </div>
        )}

        {isLoading ? (
          <div style={{ padding: '48px', textAlign: 'center', color: '#666' }}>
            Loading report preview...
          </div>
        ) : gridRows.length > 0 ? (
          <div className="reports-v2-grid-scroll">
            <table className="reports-v2-table">
              <thead>
                <tr className="reports-v2-grid-letters">
                  <th className="reports-v2-index-corner" />
                  {gridRows[0]?.map((_, idx) => (
                    <th key={idx}>{String.fromCharCode(65 + idx)}</th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {gridRows.map((row, rowIdx) => (
                  <tr key={rowIdx} className="reports-v2-row">
                    <td className="reports-v2-row-index">{rowIdx + 1}</td>
                    {(Array.isArray(row) ? row : []).map((cell, colIdx) => {
                      const merge = isMergedCell(rowIdx, colIdx);
                      const isStart = isMergeStart(rowIdx, colIdx);

                      // Skip if this is a merged cell (not the starting cell)
                      if (merge && !isStart) {
                        return null;
                      }

                      const colspan = getMergeColspan(rowIdx, colIdx);
                      const formattedValue = formatCellValue(cell, rowIdx, colIdx);
                      const isNumeric = numericColumns.includes(colIdx);

                      return (
                        <td
                          key={colIdx}
                          colSpan={colspan}
                          className={`${isNumeric ? 'amount-cell' : ''}`}
                          style={{
                            textAlign: isNumeric ? 'right' : 'left',
                          }}
                        >
                          {formattedValue}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ padding: '48px', textAlign: 'center', color: '#999' }}>
            No data available for this period
          </div>
        )}

        <footer className="reports-v2-footer">
          <p>Report for {period === 'Monthly' ? `${MONTH_NAMES[selectedMonth - 1]} ${selectedYear}` : selectedYear}</p>
        </footer>
      </section>
    </div>
  );
}
