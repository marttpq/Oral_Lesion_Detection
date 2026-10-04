import React, { useState, useRef, useEffect } from 'react';
import { Activity, LogOut, ChevronDown, Menu, X } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';

export default function Navbar() {
  const location = useLocation();
  const isInfo = location.pathname.includes('information');
  const isHome = location.pathname === '/';
  const isLogin = location.pathname === '/login';

  const { lang, setLang, t } = useLanguage();
  const { user, logout } = useAuth();

  const [showDropdown, setShowDropdown] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

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

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-3 sm:gap-5">
          <nav className="flex items-center gap-1">
            <Link to="/" className={`px-3.5 py-1.5 text-sm font-medium rounded-lg transition ${isHome ? 'text-blue-600 bg-blue-50/80' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'}`}>
              {t('nav.home')}
            </Link>
            <Link to="/information" className={`px-3.5 py-1.5 text-sm font-medium rounded-lg transition ${isInfo ? 'text-blue-600 bg-blue-50/80' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'}`}>
              {t('nav.info')}
            </Link>
          </nav>

          <div className="h-4 w-[1px] bg-slate-200"></div>

          {/* Language Pill */}
          <div className="flex items-center bg-slate-100/80 rounded-full p-1 border border-slate-200/60 shadow-inner">
            <button onClick={() => setLang('TH')} className={`px-3 py-1 text-xs font-semibold rounded-full min-w-[40px] transition-all ${lang === 'TH' ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'}`}>TH</button>
            <button onClick={() => setLang('EN')} className={`px-3 py-1 text-xs font-semibold rounded-full min-w-[40px] transition-all ${lang === 'EN' ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'}`}>EN</button>
          </div>

          <Link to="/assessment" className="ml-1 bg-[#1d4ed8] hover:bg-blue-700 active:bg-blue-800 text-white text-sm font-medium px-4 py-2 rounded-lg shadow-sm transition">
            {t('nav.startAssessment')}
          </Link>

          {user ? (
            <div className="ml-1 relative" ref={dropdownRef}>
              <button
                onClick={() => setShowDropdown(!showDropdown)}
                className="flex items-center justify-center w-10 h-10 rounded-full border-2 border-white shadow-sm ring-1 ring-slate-200/90 overflow-hidden hover:ring-blue-400 transition cursor-pointer"
              >
                {user.picture ? (
                  <img src={user.picture} alt="Profile" className="w-full h-full object-cover" referrerPolicy="no-referrer" />
                ) : (
                  <div className="w-full h-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center text-sm">
                    {user.email.charAt(0).toUpperCase()}
                  </div>
                )}
              </button>

              {/* Desktop Profile Dropdown */}
              {showDropdown && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-slate-100 py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
                  <div className="px-4 py-2 border-b border-slate-100/80">
                    <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest mb-0.5">Signed in as</p>
                    <p className="text-sm font-semibold text-slate-800 truncate" title={user.email}>{user.email}</p>
                  </div>
                  <div className="p-1">
                    <button onClick={() => { setShowDropdown(false); logout(); }} className="w-full flex items-center gap-2.5 px-3 py-2 text-sm font-medium text-slate-600 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition">
                      <LogOut className="w-4 h-4" />
                      Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <Link to="/login" className="ml-1 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-sm font-medium px-4 py-2 rounded-lg shadow-sm transition inline-flex">
              {t('nav.login')}
            </Link>
          )}
        </div>

        {/* Mobile Hamburger Toggle */}
        <div className="md:hidden flex items-center">
          <button
            onClick={() => setShowMobileMenu(!showMobileMenu)}
            className="p-2 -mr-2 text-slate-600 hover:text-slate-900 hover:bg-slate-50 rounded-lg transition"
          >
            {showMobileMenu ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {showMobileMenu && (
        <div className="md:hidden absolute top-16 left-0 w-full bg-white border-b border-slate-100 shadow-xl z-50 animate-in slide-in-from-top-2 duration-200">
          <div className="flex flex-col px-4 py-4 space-y-4">
            {/* Nav Links */}
            <nav className="flex flex-col gap-2 border-b border-slate-100 pb-4">
              <Link to="/" onClick={() => setShowMobileMenu(false)} className={`px-4 py-3 text-base font-semibold rounded-xl ${isHome ? 'text-blue-700 bg-blue-50' : 'text-slate-600 hover:bg-slate-50'}`}>
                {t('nav.home')}
              </Link>
              <Link to="/information" onClick={() => setShowMobileMenu(false)} className={`px-4 py-3 text-base font-semibold rounded-xl ${isInfo ? 'text-blue-700 bg-blue-50' : 'text-slate-600 hover:bg-slate-50'}`}>
                {t('nav.info')}
              </Link>
              <Link to="/assessment" onClick={() => setShowMobileMenu(false)} className="px-4 py-3 text-base font-semibold rounded-xl text-white bg-blue-600 hover:bg-blue-700 mt-1 text-center">
                {t('nav.startAssessment')}
              </Link>
            </nav>

            {/* Bottom Actions */}
            <div className="flex flex-col gap-4 pt-1 pb-2">
              <div className="flex items-center justify-between px-2">
                <span className="text-sm font-bold text-slate-400 uppercase tracking-wider">Language</span>
                <div className="flex items-center bg-slate-100/80 rounded-full p-1 border border-slate-200/60 shadow-inner">
                  <button onClick={() => setLang('TH')} className={`px-4 py-1.5 text-xs font-bold rounded-full min-w-[50px] transition-all ${lang === 'TH' ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500'}`}>TH</button>
                  <button onClick={() => setLang('EN')} className={`px-4 py-1.5 text-xs font-bold rounded-full min-w-[50px] transition-all ${lang === 'EN' ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500'}`}>EN</button>
                </div>
              </div>

              {user ? (
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 flex items-center justify-between mt-2">
                  <div className="flex items-center gap-3 overflow-hidden">
                    {user.picture ? (
                      <img src={user.picture} alt="Profile" className="w-10 h-10 rounded-full object-cover border border-slate-200" referrerPolicy="no-referrer" />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center shrink-0">
                        {user.email.charAt(0).toUpperCase()}
                      </div>
                    )}
                    <div className="flex flex-col truncate">
                      <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Signed In</span>
                      <span className="text-sm font-bold text-slate-800 truncate leading-tight">{user.email}</span>
                    </div>
                  </div>
                  <button onClick={() => { setShowMobileMenu(false); logout(); }} className="p-2.5 text-rose-600 bg-rose-50 hover:bg-rose-100 rounded-lg shrink-0">
                    <LogOut className="w-5 h-5" />
                  </button>
                </div>
              ) : (
                <Link to="/login" onClick={() => setShowMobileMenu(false)} className="w-full mt-2 py-3.5 bg-slate-800 hover:bg-slate-900 text-white text-base font-medium rounded-xl text-center">
                  {t('nav.login')}
                </Link>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
