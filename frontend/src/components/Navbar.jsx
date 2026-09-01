import React from 'react';
import { Activity } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';

export default function Navbar() {
  const location = useLocation();
  const isInfo = location.pathname.includes('information');
  const isHome = location.pathname === '/';
  const isLogin = location.pathname === '/login';

  const { lang, setLang, t } = useLanguage();

  return (
    <header className="w-full bg-white/95 backdrop-blur-sm border-b border-slate-100 sticky top-0 z-40">
      <div className="w-full max-w-[95%] 2xl:max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-2.5 cursor-pointer">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm shadow-blue-500/20">
            <Activity className="w-4 h-4 stroke-[2.5]" />
          </div>
          <div className="flex items-center tracking-tight">
            <span className="font-bold text-slate-900 text-lg">OralScan</span>
            <span className="font-bold text-blue-600 text-lg ml-1">AI</span>
          </div>
        </Link>

        {/* Navigation links & CTA */}
        <div className="flex items-center gap-3 sm:gap-5">
          <nav className="hidden md:flex items-center gap-1">
            <Link
              to="/"
              className={`px-3.5 py-1.5 text-sm font-medium rounded-lg transition ${isHome ? 'text-blue-600 bg-blue-50/80' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
            >
              {t('nav.home')}
            </Link>
            <Link
              to="/information"
              className={`px-3.5 py-1.5 text-sm font-medium rounded-lg transition ${isInfo ? 'text-blue-600 bg-blue-50/80' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
            >
              {t('nav.info')}
            </Link>
          </nav>

          <div className="h-4 w-[1px] bg-slate-200 hidden md:block"></div>

          {/* Language Pill */}
          <div className="flex items-center bg-slate-100/80 rounded-full p-1 border border-slate-200/60 shadow-inner">
            <button
              onClick={() => setLang('TH')}
              className={`px-3 py-1 text-xs font-semibold rounded-full md:min-w-[40px] transition-all ${lang === 'TH' ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'}`}
            >
              TH
            </button>
            <button
              onClick={() => setLang('EN')}
              className={`px-3 py-1 text-xs font-semibold rounded-full md:min-w-[40px] transition-all ${lang === 'EN' ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'}`}
            >
              EN
            </button>
          </div>

          <Link
            to="/assessment"
            className="ml-1 bg-[#1d4ed8] hover:bg-blue-700 active:bg-blue-800 text-white text-sm font-medium px-4 py-2 rounded-lg shadow-sm transition"
          >
            {t('nav.startAssessment')}
          </Link>
          <Link
            to="/login"
            className="ml-1 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-sm font-medium px-4 py-2 rounded-lg shadow-sm transition hidden sm:inline-flex"
          >
            {t('nav.login')}
          </Link>
        </div>
      </div>
    </header>
  );
}
