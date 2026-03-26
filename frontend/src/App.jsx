import { useState } from 'react';
import './index.css';
import Sidebar from './components/Sidebar';
import DashboardView from './views/DashboardView';
import TransactionsView from './views/TransactionsView';
import ReportsView from './views/ReportsView';
import AnalyticsView from './views/AnalyticsView';

const VIEWS = {
  dashboard: DashboardView,
  transactions: TransactionsView,
  reports: ReportsView,
  analytics: AnalyticsView,
};

export default function App() {
  const [activeView, setActiveView] = useState('dashboard');
  const ActiveView = VIEWS[activeView] ?? DashboardView;

  return (
    <div
      id="app-layout"
      style={{
        display: 'flex',
        width: '100%',
        minHeight: '100vh',
        background: 'var(--surface)',
      }}
    >
      <Sidebar activeView={activeView} onNavigate={setActiveView} />
      <main
        id="main-content"
        style={{
          flex: 1,
          minHeight: '100vh',
          overflowY: 'auto',
          background: 'var(--surface)',
        }}
      >
        <ActiveView key={activeView} onNavigate={setActiveView} />
      </main>
    </div>
  );
}
