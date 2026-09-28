import React from 'react';
import { Routes, Route, useLocation, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import Home from './components/Home';
import Information from './components/Information';
import Login from './components/Login';
import { useAuth } from './contexts/AuthContext';

function ProtectedRoute({ children }) {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/login" state={{ fromProtected: true }} replace />;
  }
  return children;
}

export default function App() {
  const location = useLocation();
  const isLoginPage = location.pathname === '/login';

  return (
    <div className={`min-h-screen bg-[#F8FAFC] flex flex-col font-sans ${isLoginPage ? 'overflow-hidden' : ''}`}>
      {!isLoginPage && <Navbar />}
      <div className={`w-full flex-col ${isLoginPage ? 'h-screen flex' : 'flex-1 flex'}`}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/information" element={<Information />} />
          <Route path="/assessment" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/login" element={<Login />} />
        </Routes>
      </div>
      {!isLoginPage && (
        <footer className="py-6 text-center text-xs text-slate-400 border-t border-slate-200/60 mt-12 bg-white w-full">
          <div className="w-full max-w-[95%] 2xl:max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
            OralScan AI · ระบบประเมินความเสี่ยงรอยโรคในช่องปาก &copy; 2026
          </div>
        </footer>
      )}
    </div>
  );
}
