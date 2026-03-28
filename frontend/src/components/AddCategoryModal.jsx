import { useState } from 'react';
import { X } from 'lucide-react';
import { createCategory } from '../lib/api';

export default function AddCategoryModal({ isOpen, onClose, onSuccess }) {
  const [name, setName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleClose = () => {
    if (isSubmitting) return;
    onClose();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    const payload = { name: name.trim() };

    try {
      await createCategory(payload);
      setName('');
      onSuccess?.();
      onClose();
    } catch (error) {
      console.error('Error creating category:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay" onClick={handleClose} aria-hidden="true" />
      <div className="modal-shell" role="dialog" aria-modal="true" aria-labelledby="add-category-modal-title">
        <div className="modal-content">
          <div className="modal-header">
            <h2 id="add-category-modal-title" className="modal-title">Add Category</h2>
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
              <label htmlFor="category-name" className="form-label">Category Name</label>
              <input
                type="text"
                id="category-name"
                name="name"
                placeholder="e.g. Healthcare"
                value={name}
                onChange={(e) => setName(e.target.value)}
                minLength={3}
                maxLength={50}
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
                disabled={isSubmitting || name.trim().length < 3}
              >
                {isSubmitting ? 'Adding...' : 'Add Category'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
