import { LayoutDashboard, ReceiptText, BarChart2, TrendingUp, HelpCircle, LogOut } from 'lucide-react';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'transactions', label: 'Transactions', icon: ReceiptText },
  { id: 'reports', label: 'Reports', icon: BarChart2 },
  { id: 'analytics', label: 'Analytics', icon: TrendingUp },
];

const bottomItems = [
  { id: 'support', label: 'Support', icon: HelpCircle },
  { id: 'logout', label: 'Logout', icon: LogOut },
];

export default function Sidebar({
  activeView,
  onNavigate,
  onOpenAddModal,
  onOpenStartingBalanceModal,
  onOpenCategoryModal,
  onLogout,
  currentUser,
}) {
  return (
    <aside className="app-sidebar">
      {/* Brand */}
      <div className="sidebar-brand-block">
        <div className="sidebar-brand">Obsidian</div>
        <div className="text-label text-muted" style={{ marginTop: '0.125rem' }}>
          {currentUser?.username ? `@${currentUser.username}` : 'Premium Finance'}
        </div>
      </div>

      {/* Main navigation */}
      <nav className="sidebar-main-nav">
        {navItems.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            id={`nav-${id}`}
            className={`nav-item${activeView === id ? ' active' : ''}`}
            onClick={() => onNavigate(id)}
            type="button"
          >
            <Icon size={16} strokeWidth={1.8} />
            {label}
          </button>
        ))}
      </nav>

      <div className="sidebar-action-wrap">
        <button
          type="button"
          className="btn-ghost sidebar-add-btn"
          onClick={onOpenCategoryModal}
        >
          Add Category
        </button>
        <button
          type="button"
          className="btn-ghost sidebar-add-btn"
          onClick={onOpenStartingBalanceModal}
        >
          Add Starting Balance
        </button>
        <button
          type="button"
          className="btn-primary sidebar-add-btn"
          onClick={onOpenAddModal}
        >
          Add Transaction
        </button>
      </div>

      {/* Bottom actions */}
      <nav className="sidebar-bottom-nav">
        {bottomItems.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            id={`nav-${id}`}
            className="nav-item"
            type="button"
            onClick={() => {
              if (id === 'logout') {
                onLogout?.();
              }
            }}
          >
            <Icon size={16} strokeWidth={1.8} />
            {label}
          </button>
        ))}
      </nav>
    </aside>
  );
}
