// Mock data used throughout the app until real backend APIs are wired up
// See documentation/backend-requirements.md for API contracts

export const summaryData = {
  cashBalance: 12450,
  upiBalance: 48200,
  totalSpending: 32180,
  totalIncome: 85000,
  month: 'March 2026',
  spendingChange: -8.4,   // % vs last month
  incomeChange: 5.2,
};

export const transactions = [
  {
    id: 'tx-001',
    description: 'Monthly Salary — TechCorp',
    category: 'Income',
    categoryIcon: '💼',
    amount: 85000,
    type: 'credit',
    timestamp: '2026-03-01T09:00:00',
  },
  {
    id: 'tx-002',
    description: 'Groceries at Reliance Fresh',
    category: 'Food & Grocery',
    categoryIcon: '🛒',
    amount: 3240,
    type: 'debit',
    timestamp: '2026-03-24T16:30:00',
  },
  {
    id: 'tx-003',
    description: 'Starbucks Coffee',
    category: 'Dining',
    categoryIcon: '☕',
    amount: 580,
    type: 'debit',
    timestamp: '2026-03-22T11:20:00',
  },
  {
    id: 'tx-004',
    description: 'Electricity Bill — BESCOM',
    category: 'Utilities',
    categoryIcon: '⚡',
    amount: 2450,
    type: 'debit',
    timestamp: '2026-03-15T10:15:00',
  },
  {
    id: 'tx-005',
    description: 'Dinner at Olive Garden',
    category: 'Dining',
    categoryIcon: '🍽️',
    amount: 1870,
    type: 'debit',
    timestamp: '2026-03-12T20:45:00',
  },
  {
    id: 'tx-006',
    description: 'Netflix Subscription',
    category: 'Entertainment',
    categoryIcon: '🎬',
    amount: 649,
    type: 'debit',
    timestamp: '2026-03-05T00:00:00',
  },
  {
    id: 'tx-007',
    description: 'Amazon.in Shopping',
    category: 'Shopping',
    categoryIcon: '📦',
    amount: 4899,
    type: 'debit',
    timestamp: '2026-03-03T11:30:00',
  },
  {
    id: 'tx-008',
    description: 'Freelance Payment — Design',
    category: 'Income',
    categoryIcon: '🎨',
    amount: 12000,
    type: 'credit',
    timestamp: '2026-03-18T14:00:00',
  },
  {
    id: 'tx-009',
    description: 'Ola Cab Rides',
    category: 'Transport',
    categoryIcon: '🚖',
    amount: 920,
    type: 'debit',
    timestamp: '2026-03-20T08:00:00',
  },
  {
    id: 'tx-010',
    description: 'Gym Membership — Cult Fit',
    category: 'Health',
    categoryIcon: '💪',
    amount: 1999,
    type: 'debit',
    timestamp: '2026-03-10T07:00:00',
  },
];

export const spendingTrend = [
  { month: 'Oct', spending: 28400, income: 80000 },
  { month: 'Nov', spending: 31200, income: 82000 },
  { month: 'Dec', spending: 38900, income: 80000 },
  { month: 'Jan', spending: 27100, income: 85000 },
  { month: 'Feb', spending: 35070, income: 85000 },
  { month: 'Mar', spending: 32180, income: 85000 },
];

export const spendingByCategory = [
  { name: 'Food & Grocery', value: 8240, color: '#b1ffce' },
  { name: 'Utilities', value: 4820, color: '#d674ff' },
  { name: 'Entertainment', value: 3490, color: '#ff9249' },
  { name: 'Shopping', value: 6400, color: '#00ffa3' },
  { name: 'Transport', value: 2900, color: '#bb00fc' },
  { name: 'Health', value: 3100, color: '#ff7b04' },
  { name: 'Dining',  value: 3230, color: '#5eeeff' },
];

export const reportRows = [
  { date: '2026-03-01', description: 'Monthly Salary — TechCorp', category: 'Income', amount: 85000, type: 'credit', balance: 125450 },
  { date: '2026-03-03', description: 'Amazon.in Shopping', category: 'Shopping', amount: 4899, type: 'debit', balance: 120551 },
  { date: '2026-03-05', description: 'Netflix Subscription', category: 'Entertainment', amount: 649, type: 'debit', balance: 119902 },
  { date: '2026-03-10', description: 'Gym Membership', category: 'Health', amount: 1999, type: 'debit', balance: 117903 },
  { date: '2026-03-12', description: 'Dinner at Olive Garden', category: 'Dining', amount: 1870, type: 'debit', balance: 116033 },
  { date: '2026-03-15', description: 'Electricity Bill', category: 'Utilities', amount: 2450, type: 'debit', balance: 113583 },
  { date: '2026-03-18', description: 'Freelance Payment', category: 'Income', amount: 12000, type: 'credit', balance: 125583 },
  { date: '2026-03-20', description: 'Ola Cab Rides', category: 'Transport', amount: 920, type: 'debit', balance: 124663 },
  { date: '2026-03-22', description: 'Starbucks Coffee', category: 'Dining', amount: 580, type: 'debit', balance: 124083 },
  { date: '2026-03-24', description: 'Groceries at Reliance Fresh', category: 'Food & Grocery', amount: 3240, type: 'debit', balance: 120843 },
];

export const formatINR = (n) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n);

export const formatDate = (iso) => {
  const d = new Date(iso);
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) +
    ' • ' + d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true });
};
