import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, Cell, PieChart, Pie
} from 'recharts';
import { spendingTrend, spendingByCategory, formatINR } from '../data/mockData';

/* ─── Custom Tooltip ─── */
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="custom-tooltip">
      <div className="text-label text-muted" style={{ marginBottom: '0.5rem' }}>{label}</div>
      {payload.map((p) => (
        <div
          key={p.dataKey}
          style={{ color: p.color, fontFamily: 'var(--font-label)', fontSize: '0.6875rem', marginTop: '0.125rem' }}
        >
          {p.name}: {formatINR(p.value)}
        </div>
      ))}
    </div>
  );
}

/* ─── Spending vs Income Area Chart ─── */
export function SpendingTrendChart({ data = spendingTrend }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="gradIncome" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#b1ffce" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#b1ffce" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="gradSpend" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#d674ff" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#d674ff" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(72,72,73,0.3)" vertical={false} />
        <XAxis
          dataKey="month"
          tick={{ fontFamily: 'var(--font-label)', fontSize: 10, fill: '#adaaab', textTransform: 'uppercase', letterSpacing: '0.06em' }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fontFamily: 'var(--font-label)', fontSize: 9.5, fill: '#adaaab' }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`}
        />
        <Tooltip content={<CustomTooltip />} />
        <Area type="monotone" dataKey="income" name="Income" stroke="#b1ffce" strokeWidth={2} fill="url(#gradIncome)" dot={false} />
        <Area type="monotone" dataKey="spending" name="Spending" stroke="#d674ff" strokeWidth={2} fill="url(#gradSpend)" dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

/* ─── Category Breakdown Bar Chart ─── */
export function CategoryBarChart() {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={spendingByCategory} margin={{ top: 5, right: 0, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(72,72,73,0.3)" vertical={false} />
        <XAxis
          dataKey="name"
          tick={{ fontFamily: 'var(--font-label)', fontSize: 9, fill: '#adaaab', textTransform: 'uppercase' }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fontFamily: 'var(--font-label)', fontSize: 9.5, fill: '#adaaab' }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) => `₹${(v / 1000).toFixed(1)}k`}
        />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="value" name="Spending" radius={[4, 4, 0, 0]}>
          {spendingByCategory.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} fillOpacity={0.85} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

/* ─── Category Donut Chart ─── */
export function CategoryDonutChart() {
  return (
    <ResponsiveContainer width="100%" height={160}>
      <PieChart>
        <Pie
          data={spendingByCategory}
          cx="50%"
          cy="50%"
          innerRadius={50}
          outerRadius={75}
          paddingAngle={3}
          dataKey="value"
        >
          {spendingByCategory.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} fillOpacity={0.9} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
      </PieChart>
    </ResponsiveContainer>
  );
}
