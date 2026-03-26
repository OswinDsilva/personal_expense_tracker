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

export default function Sidebar({ activeView, onNavigate }) {
  return (
    <aside
      style={{
        width: '220px',
        minWidth: '220px',
        background: 'var(--surface-low)',
        borderRight: '1px solid rgba(72,72,73,0.3)',
        display: 'flex',
        flexDirection: 'column',
        padding: '1.5rem 1rem',
        height: '100vh',
        position: 'sticky',
        top: 0,
      }}
    >
      {/* Brand */}
      <div style={{ marginBottom: '2.5rem', paddingLeft: '0.5rem' }}>
        <div
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1.5rem',
            fontWeight: 700,
            background: 'linear-gradient(135deg, var(--primary), var(--primary-container))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          Kharcha
        </div>
        <div className="text-label text-muted" style={{ marginTop: '0.125rem' }}>
          Finance Command Center
        </div>
      </div>

      {/* Main navigation */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', flex: 1 }}>
        {navItems.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            id={`nav-${id}`}
            className={`nav-item${activeView === id ? ' active' : ''}`}
            onClick={() => onNavigate(id)}
          >
            <Icon size={16} strokeWidth={1.8} />
            {label}
          </button>
        ))}
      </nav>

      {/* Bottom actions */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
        {bottomItems.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            id={`nav-${id}`}
            className="nav-item"
            onClick={() => {}}
          >
            <Icon size={16} strokeWidth={1.8} />
            {label}
          </button>
        ))}
      </nav>
    </aside>
  );
}
