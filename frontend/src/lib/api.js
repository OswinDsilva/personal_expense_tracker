const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
export const AUTH_EXPIRED_EVENT = 'auth:expired';

export const resolveStoredToken = () => {
  const candidates = ['access_token', 'token', 'auth_token', 'jwt'];
  for (const key of candidates) {
    const value = localStorage.getItem(key);
    if (value) {
      return value;
    }
  }
  return null;
};

const parseError = async (response) => {
  try {
    const body = await response.json();
    if (typeof body?.detail === 'string') return body.detail;
    if (Array.isArray(body?.detail)) return body.detail.map((d) => d?.msg || JSON.stringify(d)).join(', ');
    return `Request failed with status ${response.status}`;
  } catch {
    return `Request failed with status ${response.status}`;
  }
};

export const apiRequest = async (path, options = {}) => {
  const token = resolveStoredToken();
  const headers = {
    ...(options.body ? { 'Content-Type': 'application/json' } : {}),
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok && response.status === 401 && path !== '/auth/login' && path !== '/auth/register') {
    window.dispatchEvent(new CustomEvent(AUTH_EXPIRED_EVENT));
  }

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response;
};

export const registerUser = async (payload) => {
  const response = await apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return response.json();
};

export const loginUser = async (payload) => {
  const response = await apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return response.json();
};

export const getCurrentUser = async () => {
  const response = await apiRequest('/auth/me');
  return response.json();
};

export const getCategories = async () => {
  const response = await apiRequest('/categories/');
  return response.json();
};

export const createCategory = async (payload) => {
  const response = await apiRequest('/categories/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return response.json();
};

export const createStartingBalance = async (payload) => {
  const response = await apiRequest('/starting-balances/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return response.json();
};

export const createTransaction = async (payload) => {
  const response = await apiRequest('/transactions/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return response.json();
};

export const getTransactions = async (params = {}) => {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.set(key, String(value));
    }
  });

  const query = searchParams.toString();
  const response = await apiRequest(`/transactions/${query ? `?${query}` : ''}`);
  return response.json();
};

export const getPreviewMonthly = async (year, month) => {
  const response = await apiRequest(`/reports/preview/monthly/${year}/${month}`);
  return response.json();
};

export const getPreviewYearly = async (year) => {
  const response = await apiRequest(`/reports/preview/yearly/${year}`);
  return response.json();
};

export const getMonthlyData = async (year, month) => {
  const response = await apiRequest(`/reports/data/${year}/${month}`);
  return response.json();
};

export const getYearlyData = async (year) => {
  const response = await apiRequest(`/reports/data/${year}`);
  return response.json();
};

export const downloadMonthlyExport = async (year, month) => {
  const response = await apiRequest(`/reports/exports/${year}/${month}`);
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Expenses_${year}_${month}.xlsx`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};

export const downloadYearlyExport = async (year) => {
  const response = await apiRequest(`/reports/exports/${year}`);
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Expenses_${year}_summary.xlsx`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};

export const downloadFullYearExport = async (year) => {
  const response = await apiRequest(`/reports/exports/${year}/full`);
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Expenses_${year}_full_summary.xlsx`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};
