export default function AnalyticsView() {
  return (
    <div className="view-shell animate-fade-up">
      <div>
        <div className="text-label text-muted">Insights Workspace</div>
        <h1 className="view-title" style={{ margin: '0.25rem 0 0' }}>
          Analytics
        </h1>
      </div>

      <div className="metric-card" style={{ padding: '2rem', minHeight: '18rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="text-label text-muted" style={{ marginBottom: '0.75rem' }}>Status</div>
          <h2 className="text-headline" style={{ color: 'var(--on-surface)', marginBottom: '0.5rem' }}>
            Analytics Is Under Development
          </h2>
          <p className="text-body" style={{ color: 'var(--on-surface-muted)', maxWidth: '32rem' }}>
            This section is being upgraded. Detailed analytics and advanced insights will be available in an upcoming release.
          </p>
        </div>
      </div>
    </div>
  );
}
