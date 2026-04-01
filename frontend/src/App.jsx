import { useEffect, useRef, useState } from 'react';
import { LayoutDashboard, ReceiptText, BarChart2, TrendingUp, Plus } from 'lucide-react';
import './index.css';
import Sidebar from './components/Sidebar';
import AddTransactionModal from './components/AddTransactionModal';
import AddStartingBalanceModal from './components/AddStartingBalanceModal';
import AddCategoryModal from './components/AddCategoryModal';
import DashboardView from './views/DashboardView';
import TransactionsView from './views/TransactionsView';
import ReportsView from './views/ReportsView';
import AnalyticsView from './views/AnalyticsView';
import LoginView from './views/LoginView';
import LoadingSpinner from './components/LoadingSpinner';

const VIEWS = {
  dashboard: DashboardView,
  transactions: TransactionsView,
  reports: ReportsView,
  analytics: AnalyticsView,
};

const MOBILE_NAV_ITEMS = [
  { id: 'dashboard', label: 'Home', icon: LayoutDashboard },
  { id: 'transactions', label: 'Activity', icon: ReceiptText },
  { id: 'reports', label: 'Reports', icon: BarChart2 },
  { id: 'analytics', label: 'Insights', icon: TrendingUp },
];

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => Boolean(localStorage.getItem('access_token')));
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const stored = localStorage.getItem('current_user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });
  const [activeView, setActiveView] = useState('dashboard');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isStartingBalanceModalOpen, setIsStartingBalanceModalOpen] = useState(false);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);
  const [isMobileAddMenuOpen, setIsMobileAddMenuOpen] = useState(false);
  const [transactionsRefreshTick, setTransactionsRefreshTick] = useState(0);
  const [categoriesRefreshTick, setCategoriesRefreshTick] = useState(0);
  const mobileActionsRef = useRef(null);
  const ActiveView = VIEWS[activeView] ?? DashboardView;

  const handleLoginSuccess = (user) => {
    setCurrentUser(user ?? null);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('current_user');
    localStorage.removeItem('token');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('jwt');
    setCurrentUser(null);
    setIsAuthenticated(false);
    setActiveView('dashboard');
    setIsAddModalOpen(false);
    setIsStartingBalanceModalOpen(false);
    setIsCategoryModalOpen(false);
    setIsMobileAddMenuOpen(false);
  };

  const openTransactionModal = () => {
    setIsAddModalOpen(true);
    setIsStartingBalanceModalOpen(false);
    setIsCategoryModalOpen(false);
    setIsMobileAddMenuOpen(false);
  };

  const openStartingBalanceModal = () => {
    setIsStartingBalanceModalOpen(true);
    setIsAddModalOpen(false);
    setIsCategoryModalOpen(false);
    setIsMobileAddMenuOpen(false);
  };

  const openCategoryModal = () => {
    setIsCategoryModalOpen(true);
    setIsAddModalOpen(false);
    setIsStartingBalanceModalOpen(false);
    setIsMobileAddMenuOpen(false);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (mobileActionsRef.current && !mobileActionsRef.current.contains(event.target)) {
        setIsMobileAddMenuOpen(false);
      }
    };

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setIsMobileAddMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, []);

  useEffect(() => {
    setIsMobileAddMenuOpen(false);
  }, [activeView]);

  if (!isAuthenticated) {
    return <LoginView onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div id="app-layout" className="app-shell">
      <div className="app-aura app-aura-right" aria-hidden="true" />
      <div className="app-aura app-aura-left" aria-hidden="true" />

      <Sidebar
        activeView={activeView}
        onNavigate={setActiveView}
        onOpenAddModal={openTransactionModal}
        onOpenStartingBalanceModal={openStartingBalanceModal}
        onOpenCategoryModal={openCategoryModal}
        onLogout={handleLogout}
        currentUser={currentUser}
      />

      <header className={`mobile-top-bar${activeView === 'dashboard' ? ' active' : ''}`} aria-label="Dashboard header">
        <div className="mobile-user-tag" aria-label="Current user">
          {currentUser?.username ? `@${currentUser.username}` : '@user'}
        </div>

        <div className="mobile-add-actions" ref={mobileActionsRef}>
          <button
            type="button"
            className="mobile-plus-btn"
            onClick={() => setIsMobileAddMenuOpen((open) => !open)}
            aria-label="Open add menu"
            aria-expanded={isMobileAddMenuOpen}
            aria-haspopup="menu"
          >
            <Plus size={20} strokeWidth={2.3} />
          </button>

          {isMobileAddMenuOpen ? (
            <div className="mobile-add-menu" role="menu" aria-label="Add actions">
              <button type="button" role="menuitem" className="mobile-add-menu-item" onClick={openTransactionModal}>
                Add Transaction
              </button>
              <button type="button" role="menuitem" className="mobile-add-menu-item" onClick={openStartingBalanceModal}>
                Add Starting Balance
              </button>
              <button type="button" role="menuitem" className="mobile-add-menu-item" onClick={openCategoryModal}>
                Add Category
              </button>
            </div>
          ) : null}
        </div>
      </header>

      <main
        id="main-content"
        className={`main-content-shell${activeView === 'dashboard' ? ' with-mobile-header' : ''}`}
      >
        <ActiveView
          key={activeView}
          onNavigate={setActiveView}
          transactionsRefreshTick={transactionsRefreshTick}
          categoriesRefreshTick={categoriesRefreshTick}
        />
      </main>

      <AddTransactionModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        categoriesRefreshTick={categoriesRefreshTick}
        onSuccess={() => setTransactionsRefreshTick((tick) => tick + 1)}
      />
      <AddStartingBalanceModal
        isOpen={isStartingBalanceModalOpen}
        onClose={() => setIsStartingBalanceModalOpen(false)}
      />
      <AddCategoryModal
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        onSuccess={() => setCategoriesRefreshTick((tick) => tick + 1)}
      />

      <nav className="mobile-bottom-nav" aria-label="Primary navigation">
        {MOBILE_NAV_ITEMS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            className={`mobile-nav-item${activeView === id ? ' active' : ''}`}
            onClick={() => setActiveView(id)}
          >
            <Icon size={17} strokeWidth={2} />
            <span>{label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}
