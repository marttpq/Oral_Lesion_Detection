import React from 'react';
import { Activity } from 'lucide-react';

export default function Navbar() {
  return (
    <header className="w-full bg-white/95 backdrop-blur-sm border-b border-slate-100 sticky top-0 z-40">
      <div className="w-full max-w-[95%] 2xl:max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <div className="flex items-center gap-2.5 cursor-pointer">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm shadow-blue-500/20">
            <Activity className="w-4 h-4 stroke-[2.5]" />
          </div>
          <div className="flex items-center tracking-tight">
            <span className="font-bold text-slate-900 text-lg">OralScan</span>
            <span className="font-bold text-blue-600 text-lg ml-1">AI</span>
          </div>
        </div>

        {/* Navigation links & CTA */}
        <div className="flex items-center gap-2 sm:gap-4">
          <nav className="hidden md:flex items-center gap-1">
            <a
              href="#home"
              className="px-3.5 py-1.5 text-sm font-medium text-slate-600 hover:text-slate-900 rounded-lg hover:bg-slate-50 transition"
            >
              หน้าแรก
            </a>
            <a
              href="#diseases"
              className="px-3.5 py-1.5 text-sm font-medium text-slate-600 hover:text-slate-900 rounded-lg hover:bg-slate-50 transition"
            >
              โรคในช่องปาก
            </a>
            <a
              href="#assessment"
              className="px-4 py-1.5 text-sm font-medium text-blue-600 bg-blue-50/80 rounded-lg transition"
            >
              การประเมิน
            </a>
          </nav>

          <button
            type="button"
            className="ml-2 bg-[#1d4ed8] hover:bg-blue-700 active:bg-blue-800 text-white text-sm font-medium px-4 py-2 rounded-lg shadow-sm transition"
          >
            เริ่มการประเมิน
          </button>
        </div>
      </div>
    </header>
  );
}
