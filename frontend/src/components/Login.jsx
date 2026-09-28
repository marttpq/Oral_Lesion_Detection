import React from 'react';
import { Activity, Mail, Lock, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';

export default function Login() {
    const { t, lang } = useLanguage();

    const handleMockSubmit = (e) => {
        e.preventDefault();
        // Functionless login as requested
    };

    return (
        <main className="w-full h-full flex basis-full animate-in fade-in duration-500 overflow-hidden">
            {/* Left Graphic Panel (Hidden on Mobile) */}
            <div className="hidden lg:flex lg:w-[45%] xl:w-1/2 relative bg-gradient-to-br from-blue-700 to-blue-900 overflow-hidden">
                <div className="absolute inset-0 bg-white/5 opacity-10 mix-blend-overlay" />

                {/* Top Left Logo */}
                <div className="absolute top-10 left-10 xl:top-12 xl:left-12 z-30 flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-white/10 backdrop-blur-md flex items-center justify-center text-white border border-white/20 shadow-sm">
                        <Activity className="w-5 h-5 stroke-[2.5]" />
                    </div>
                    <span className="font-serif text-white font-bold text-xl tracking-tight drop-shadow-sm">OralScan AI</span>
                </div>

                {/* Center Welcome Message */}
                <div className="z-30 flex flex-col justify-center px-10 xl:px-16 w-full h-full">
                    <div className="max-w-md">
                        <span className="inline-block text-blue-200 font-semibold tracking-wider text-[10px] uppercase mb-4 border border-blue-400/30 bg-blue-500/10 px-3 py-1.5 rounded-full">
                            Secure Clinical Portal
                        </span>
                        <h2 className="text-3xl xl:text-[34px] font-serif font-bold text-white leading-[1.25] mb-4">
                            {lang === 'TH'
                                ? "แพลตฟอร์มสนับสนุนการคัดกรองรอยโรคด้วยระบบ AI"
                                : "AI-Assisted Oral Screening & Diagnostic Support"}
                        </h2>
                        <p className="text-blue-100/70 leading-relaxed font-normal text-sm xl:text-base">
                            {lang === 'TH'
                                ? "เข้าสู่ระบบเพื่อใช้งานโมเดลการประเมิน แพลตฟอร์มนี้ออกแบบมาเพื่อสนับสนุนการวิเคราะห์ความเสี่ยงเบื้องต้นทางคลินิก โดยพิจารณาจากภาพถ่ายและประวัติทางการแพทย์"
                                : "Sign in to explore our evaluation models. This platform is designed to support preliminary medical assessments by analyzing visual and clinical patient data."}
                        </p>
                    </div>
                </div>
            </div>

            {/* Right Form Panel */}
            <div className="w-full lg:w-[55%] xl:w-1/2 bg-white flex flex-col relative overflow-y-auto">
                <div className="flex-1 flex flex-col justify-center items-center p-6 sm:p-12 xl:p-16">

                    {/* Floating Back Link */}
                    <div className="absolute top-6 left-6 sm:top-10 sm:left-10 w-full">
                        <Link to="/" className="inline-flex items-center gap-2 text-sm font-semibold text-slate-400 hover:text-slate-800 transition-colors">
                            <ArrowLeft className="w-4 h-4" />
                            {t('nav.home')}
                        </Link>
                    </div>

                    <div className="w-full max-w-[400px] mt-10 lg:mt-0">
                        {/* Mobile Header (Hidden on Desktop) */}
                        <div className="lg:hidden flex items-center gap-3 mb-10">
                            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
                                <Activity className="w-5 h-5 stroke-[2.5]" />
                            </div>
                            <span className="font-serif text-slate-900 font-bold text-2xl tracking-tight">OralScan AI</span>
                        </div>

                        {/* Title Section */}
                        <div className="mb-10 text-left">
                            <h1 className="font-serif text-3xl font-bold text-slate-900 tracking-tight mb-2">
                                {t('login.title')}
                            </h1>
                            <p className="text-sm text-slate-500 font-medium">
                                {t('login.subtitle')}
                            </p>
                        </div>

                        {/* Form */}
                        <form onSubmit={handleMockSubmit} className="space-y-6">
                            <div className="space-y-2">
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
                                        className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200/90 rounded-xl text-sm text-slate-800 focus:bg-white focus:outline-none focus:ring-4 focus:ring-blue-500/15 focus:border-blue-500 transition-all font-medium placeholder-slate-400"
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                    <label className="text-sm font-semibold text-slate-700 block">
                                        {t('login.password')}
                                    </label>
                                    <a href="#" className="text-[13px] font-bold text-blue-600 hover:text-blue-700 transition">
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
                                        className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200/90 rounded-xl text-sm text-slate-800 focus:bg-white focus:outline-none focus:ring-4 focus:ring-blue-500/15 focus:border-blue-500 transition-all font-medium placeholder-slate-400"
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                className="w-full py-3.5 mt-2 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white text-sm font-semibold rounded-xl shadow-[0_4px_14px_0_rgba(37,99,235,0.25)] transition-all flex items-center justify-center gap-2"
                            >
                                {t('login.signIn')}
                            </button>

                            <div className="flex items-center gap-4 my-6">
                                <div className="flex-1 h-px bg-slate-200/80"></div>
                                <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">{t('login.or')}</span>
                                <div className="flex-1 h-px bg-slate-200/80"></div>
                            </div>

                            <button
                                type="button"
                                onClick={handleMockSubmit}
                                className="w-full py-3.5 bg-white hover:bg-slate-50 active:bg-slate-100 border border-slate-200/90 text-slate-700 text-sm font-semibold rounded-xl shadow-xs transition-all flex items-center justify-center gap-3"
                            >
                                <svg className="w-[18px] h-[18px]" viewBox="0 0 24 24">
                                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                                </svg>
                                {t('login.google')}
                            </button>
                        </form>

                        <div className="mt-10 lg:mt-12 text-center text-[13px] font-medium text-slate-500">
                            {t('login.noAccount')}{' '}
                            <a href="#" className="font-bold text-blue-600 hover:text-blue-700 transition">
                                {t('login.signUp')}
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
