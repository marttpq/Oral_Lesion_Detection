import React from 'react';
import { Activity, Mail, Lock } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';

export default function Login() {
    const { t } = useLanguage();

    const handleMockSubmit = (e) => {
        e.preventDefault();
        // Functionless login as requested
    };

    return (
        <main className="flex-1 w-full flex items-center justify-center p-4 sm:p-8 animate-in fade-in duration-300">
            <div className="w-full max-w-md bg-white rounded-3xl border border-slate-200/90 shadow-xl shadow-slate-200/50 p-8 sm:p-10">

                {/* Brand Header */}
                <div className="flex flex-col items-center justify-center mb-8">
                    <div className="w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-sm shadow-blue-500/20 mb-4">
                        <Activity className="w-6 h-6 stroke-[2.5]" />
                    </div>
                    <h1 className="font-serif text-2xl font-bold text-slate-900 tracking-tight">
                        {t('login.title')}
                    </h1>
                    <p className="text-sm text-slate-500 mt-1.5">
                        {t('login.subtitle')}
                    </p>
                </div>

                {/* Functionless Mock Form */}
                <form onSubmit={handleMockSubmit} className="space-y-5">
                    <div className="space-y-1.5">
                        <label className="text-sm font-semibold text-slate-700 block">
                            {t('login.email')}
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                                <Mail className="w-4 h-4" />
                            </div>
                            <input
                                type="email"
                                placeholder="doctor@clinic.com"
                                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 focus:bg-white focus:outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all"
                            />
                        </div>
                    </div>

                    <div className="space-y-1.5">
                        <div className="flex items-center justify-between">
                            <label className="text-sm font-semibold text-slate-700 block">
                                {t('login.password')}
                            </label>
                            <a href="#" className="text-xs font-semibold text-blue-600 hover:text-blue-700 transition">
                                {t('login.forgotPassword')}
                            </a>
                        </div>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                                <Lock className="w-4 h-4" />
                            </div>
                            <input
                                type="password"
                                placeholder="••••••••"
                                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 focus:bg-white focus:outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="w-full py-3 mt-2 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white text-sm font-semibold rounded-xl shadow-md shadow-blue-600/20 transition-all flex items-center justify-center gap-2"
                    >
                        {t('login.signIn')}
                    </button>
                </form>

                <div className="mt-8 text-center text-sm text-slate-500">
                    {t('login.noAccount')}{' '}
                    <a href="#" className="font-semibold text-blue-600 hover:text-blue-700 transition">
                        {t('login.signUp')}
                    </a>
                </div>
            </div>
        </main>
    );
}
