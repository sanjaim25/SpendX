import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import { setAuthExpiredHandler } from './services/api';
import './index.css';

function App() {
  const [token, setToken] = useState(localStorage.getItem('smartspend_token'));
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('smartspend_user') || 'null'));

  const handleLogin = (newToken, userData) => {
    localStorage.setItem('smartspend_token', newToken);
    localStorage.setItem('smartspend_user', JSON.stringify(userData));
    setToken(newToken);
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('smartspend_token');
    localStorage.removeItem('smartspend_user');
    setToken(null);
    setUser(null);
  };

  useEffect(() => {
    setAuthExpiredHandler(() => {
      localStorage.removeItem('smartspend_token');
      localStorage.removeItem('smartspend_user');
      setToken(null);
      setUser(null);
    });

    return () => setAuthExpiredHandler(null);
  }, []);

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={token ? <Navigate to="/dashboard" /> : <Login onLogin={handleLogin} />}
        />
        <Route
          path="/dashboard"
          element={token ? <Dashboard token={token} user={user} onLogout={handleLogout} /> : <Navigate to="/login" />}
        />
        <Route path="*" element={<Navigate to={token ? "/dashboard" : "/login"} />} />
      </Routes>
    </Router>
  );
}

export default App;
