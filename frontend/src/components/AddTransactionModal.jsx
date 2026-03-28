import { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import { createTransaction, getCategories } from '../lib/api';

const PAYMENT_METHODS = [
  { label: 'Cash', value: 'CASH' },
  { label: 'UPI', value: 'UPI' },
];

const TRANSACTION_TYPES = [
  { label: 'Expense', value: 'EXPENSE' },
  { label: 'Income', value: 'INCOME' },
];

export default function AddTransactionModal({
  isOpen,
  onClose,
  categoriesRefreshTick,
  onSuccess,
}) {
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    amount: '',
    description: '',
    paymentMethod: 'CASH',
    transactionType: 'EXPENSE',
    category: '',
  });
  const [categories, setCategories] = useState([]);

  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!isOpen) return;

    const loadCategories = async () => {
      try {
        const response = await getCategories();
        setCategories(response);
      } catch (error) {
        console.error('Error loading categories:', error);
      }
    };

    loadCategories();
  }, [isOpen, categoriesRefreshTick]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    const payload = {
      transaction_date: formData.date,
      amount: parseFloat(formData.amount),
      description: formData.description.trim(),
      payment_method: formData.paymentMethod,
      transaction_type: formData.transactionType,
      category_id:
        formData.transactionType === 'EXPENSE' && formData.category
          ? parseInt(formData.category, 10)
          : null,
    };

    try {
      await createTransaction(payload);

      // Reset form and close modal
      setFormData({
        date: new Date().toISOString().split('T')[0],
        amount: '',
        description: '',
        paymentMethod: 'CASH',
        transactionType: 'EXPENSE',
        category: '',
      });
      onSuccess?.();
      onClose();
    } catch (error) {
      console.error('Error creating transaction:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay" onClick={onClose} aria-hidden="true" />
      <div className="modal-shell" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div className="modal-content">
          {/* Header */}
          <div className="modal-header">
            <h2 id="modal-title" className="modal-title">Add Transaction</h2>
            <button
              type="button"
              className="modal-close-btn"
              onClick={onClose}
              aria-label="Close modal"
            >
              <X size={20} />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="modal-form">
            {/* Date */}
            <div className="form-group">
              <label htmlFor="date" className="form-label">Transaction Date</label>
              <input
                type="date"
                id="date"
                name="date"
                value={formData.date}
                onChange={handleChange}
                required
                className="form-input"
              />
            </div>

            {/* Amount */}
            <div className="form-group">
              <label htmlFor="amount" className="form-label">Amount (₹)</label>
              <input
                type="number"
                id="amount"
                name="amount"
                placeholder="0.00"
                value={formData.amount}
                onChange={handleChange}
                step="0.01"
                min="0"
                required
                className="form-input"
              />
            </div>

            {/* Description */}
            <div className="form-group">
              <label htmlFor="description" className="form-label">Description</label>
              <input
                type="text"
                id="description"
                name="description"
                placeholder="What was this transaction for?"
                value={formData.description}
                onChange={handleChange}
                required
                className="form-input"
              />
            </div>

            {/* Payment Method */}
            <div className="form-group">
              <label htmlFor="paymentMethod" className="form-label">Payment Method</label>
              <select
                id="paymentMethod"
                name="paymentMethod"
                value={formData.paymentMethod}
                onChange={handleChange}
                required
                className="form-select"
              >
                {PAYMENT_METHODS.map((method) => (
                  <option key={method.value} value={method.value}>
                    {method.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Transaction Type */}
            <div className="form-group">
              <label htmlFor="transactionType" className="form-label">Transaction Type</label>
              <select
                id="transactionType"
                name="transactionType"
                value={formData.transactionType}
                onChange={handleChange}
                required
                className="form-select"
              >
                {TRANSACTION_TYPES.map(({ label, value }) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            {/* Category */}
            <div className="form-group">
              <label htmlFor="category" className="form-label">Category</label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                required={formData.transactionType === 'EXPENSE'}
                disabled={formData.transactionType !== 'EXPENSE'}
                className="form-select"
              >
                <option value="">
                  {formData.transactionType === 'EXPENSE' ? 'Select category' : 'Not required for income'}
                </option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Form Actions */}
            <div className="modal-actions">
              <button
                type="button"
                onClick={onClose}
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
                {isSubmitting ? 'Adding...' : 'Add Transaction'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
