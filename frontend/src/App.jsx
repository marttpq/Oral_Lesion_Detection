import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import Home from './components/Home';
import Information from './components/Information';
import Login from './components/Login';

export default function App() {
  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col font-sans">
      <Navbar />
      <div className="flex-1 w-full">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/information" element={<Information />} />
          <Route path="/assessment" element={<Dashboard />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </div>
      <footer className="py-6 text-center text-xs text-slate-400 border-t border-slate-200/60 mt-12 bg-white w-full">
        <div className="w-full max-w-[95%] 2xl:max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
          OralScan AI · ระบบประเมินความเสี่ยงรอยโรคในช่องปาก &copy; 2026
        </div>
      </footer>
    </div>
  );
}
