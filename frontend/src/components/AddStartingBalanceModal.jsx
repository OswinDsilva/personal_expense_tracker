import { useMemo, useState } from 'react';
import { X } from 'lucide-react';
import { createStartingBalance } from '../lib/api';

const formatCurrentMonth = () => {
  const now = new Date();
  return {
    year: String(now.getFullYear()),
    month: String(now.getMonth() + 1).padStart(2, '0'),
  };
};

const toApiMonthDate = (yearValue, monthValue) => `${yearValue}-${monthValue}-01`;

const MONTH_OPTIONS = [
  { value: '01', label: 'January' },
  { value: '02', label: 'February' },
  { value: '03', label: 'March' },
  { value: '04', label: 'April' },
  { value: '05', label: 'May' },
  { value: '06', label: 'June' },
  { value: '07', label: 'July' },
  { value: '08', label: 'August' },
  { value: '09', label: 'September' },
  { value: '10', label: 'October' },
  { value: '11', label: 'November' },
  { value: '12', label: 'December' },
];

export default function AddStartingBalanceModal({ isOpen, onClose }) {
  const currentDateParts = useMemo(() => formatCurrentMonth(), []);
  const currentYear = currentDateParts.year;
  const currentMonth = currentDateParts.month;

  const [formData, setFormData] = useState({
    year: currentYear,
    month: currentMonth,
    cashBalance: '',
    upiBalance: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const visibleMonths = useMemo(() => {
    if (formData.year === currentYear) {
      return MONTH_OPTIONS.filter(({ value }) => value <= currentMonth);
    }
    return MONTH_OPTIONS;
  }, [currentMonth, currentYear, formData.year]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleClose = () => {
    if (isSubmitting) return;
    onClose();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    const payload = {
      month: toApiMonthDate(formData.year, formData.month),
      cash_balance: parseFloat(formData.cashBalance),
      upi_balance: parseFloat(formData.upiBalance),
    };

    try {
      await createStartingBalance(payload);

      setFormData({
        year: currentYear,
        month: currentMonth,
        cashBalance: '',
        upiBalance: '',
      });
      onClose();
    } catch (error) {
      console.error('Error creating starting balance:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay" onClick={handleClose} aria-hidden="true" />
      <div className="modal-shell" role="dialog" aria-modal="true" aria-labelledby="starting-balance-modal-title">
        <div className="modal-content">
          <div className="modal-header">
            <h2 id="starting-balance-modal-title" className="modal-title">Add Starting Balance</h2>
            <button
              type="button"
              className="modal-close-btn"
              onClick={handleClose}
              aria-label="Close modal"
            >
              <X size={20} />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="modal-form">
            <div className="form-group">
              <label htmlFor="starting-balance-year" className="form-label">Year</label>
              <input
                type="number"
                id="starting-balance-year"
                name="year"
                placeholder="YYYY"
                value={formData.year}
                min="2000"
                max={currentYear}
                onChange={(e) => {
                  const yearValue = e.target.value;
                  setFormData((prev) => {
                    const adjustedMonth =
                      yearValue === currentYear && prev.month > currentMonth
                        ? currentMonth
                        : prev.month;
                    return { ...prev, year: yearValue, month: adjustedMonth };
                  });
                }}
                required
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="starting-balance-month" className="form-label">Month</label>
              <select
                id="starting-balance-month"
                name="month"
                value={formData.month}
                onChange={handleChange}
                required
                className="form-select"
              >
                {visibleMonths.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="starting-balance-cash" className="form-label">Cash Balance (₹)</label>
              <input
                type="number"
                id="starting-balance-cash"
                name="cashBalance"
                placeholder="0.00"
                value={formData.cashBalance}
                onChange={handleChange}
                step="0.01"
                min="0"
                required
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="starting-balance-upi" className="form-label">UPI Balance (₹)</label>
              <input
                type="number"
                id="starting-balance-upi"
                name="upiBalance"
                placeholder="0.00"
                value={formData.upiBalance}
                onChange={handleChange}
                step="0.01"
                min="0"
                required
                className="form-input"
              />
            </div>

            <div className="modal-actions">
              <button
                type="button"
                onClick={handleClose}
                className="btn-modal-secondary"
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-modal-primary"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Adding...' : 'Add Starting Balance'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
