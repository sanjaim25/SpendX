const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
let authExpiredHandler = null;

export const setAuthExpiredHandler = (handler) => {
  authExpiredHandler = handler;
};

const getHeaders = (token) => ({
  'Content-Type': 'application/json',
  ...(token && { Authorization: `Bearer ${token}` }),
});

const handleResponse = async (res) => {
  let data = {};
  try {
    data = await res.json();
  } catch (_) {
    if (!res.ok) throw new Error(`Request failed (${res.status})`);
    return {};
  }

  if (!res.ok) {
    const message = data.error || data.msg || data.message || `Request failed (${res.status})`;
    const authError =
      res.status === 401 &&
      typeof message === 'string' &&
      (
        message.toLowerCase().includes('token has expired') ||
        message.toLowerCase().includes('missing authorization header') ||
        message.toLowerCase().includes('signature verification failed') ||
        message.toLowerCase().includes('invalid token')
      );

    if (authError && typeof authExpiredHandler === 'function') {
      authExpiredHandler();
    }

    throw new Error(authError ? 'Session expired. Please sign in again.' : message);
  }
  return data;
};

export const authAPI = {
  register: (data) =>
    fetch(`${BASE_URL}/register`, { method: 'POST', headers: getHeaders(), body: JSON.stringify(data) }).then(handleResponse),

  login: (data) =>
    fetch(`${BASE_URL}/login`, { method: 'POST', headers: getHeaders(), body: JSON.stringify(data) }).then(handleResponse),
};

export const expenseAPI = {
  getAll: (token) =>
    fetch(`${BASE_URL}/expenses`, { headers: getHeaders(token) }).then(handleResponse),

  add: (token, data) =>
    fetch(`${BASE_URL}/expenses`, { method: 'POST', headers: getHeaders(token), body: JSON.stringify(data) }).then(handleResponse),

  delete: (token, id) =>
    fetch(`${BASE_URL}/expenses/${id}`, { method: 'DELETE', headers: getHeaders(token) }).then(handleResponse),
};

export const forecastAPI = {
  get: (token) =>
    fetch(`${BASE_URL}/forecast`, { headers: getHeaders(token) }).then(handleResponse),
};

export const budgetAPI = {
  set: (token, data) =>
    fetch(`${BASE_URL}/budget`, { method: 'POST', headers: getHeaders(token), body: JSON.stringify(data) }).then(handleResponse),

  update: (token, id, data) =>
    fetch(`${BASE_URL}/budget/${id}`, { method: 'PUT', headers: getHeaders(token), body: JSON.stringify(data) }).then(handleResponse),

  delete: (token, id) =>
    fetch(`${BASE_URL}/budget/${id}`, { method: 'DELETE', headers: getHeaders(token) }).then(handleResponse),

  getSummary: (token) =>
    fetch(`${BASE_URL}/budget/summary`, { headers: getHeaders(token) }).then(handleResponse),
};

export const dashboardAPI = {
  get: (token, period = 'monthly') =>
    fetch(`${BASE_URL}/dashboard?period=${encodeURIComponent(period)}`, { headers: getHeaders(token) }).then(handleResponse),
};
