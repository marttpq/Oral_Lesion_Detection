import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, ArrowRight } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

export default function Home() {
  const { t } = useLanguage();

  return (
    <main className="w-full max-w-[95%] 2xl:max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 animate-in fade-in duration-300">

      {/* Clean Clinical Hero Section */}
      <section className="w-full flex flex-col lg:flex-row items-center gap-12 lg:gap-16 py-10 sm:py-16">

        {/* Text Content */}
        <div className="lg:w-1/2 flex flex-col items-start gap-6 sm:gap-8">
          <span className="text-xs font-bold text-blue-600 tracking-wider uppercase block mb-2 flex items-center gap-2">
            <Activity className="w-4 h-4 text-blue-600" />
            {t('home.tag')}
          </span>

          <h1 className="font-serif text-4xl sm:text-5xl lg:text-7xl font-bold text-slate-900 tracking-tight leading-[1.15]">
            {t('home.title1')} <br className="hidden md:block" />
            <span className="text-blue-700">{t('home.title2')}</span>
          </h1>

          <p className="text-slate-500 text-base sm:text-lg lg:text-xl leading-relaxed max-w-xl font-normal">
            {t('home.desc')}
          </p>

          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto mt-2">
            <Link
              to="/assessment"
              className="w-full sm:w-auto px-8 py-3.5 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white text-sm lg:text-base font-semibold rounded-xl text-center shadow-md shadow-blue-600/20 transition-all flex items-center justify-center"
            >
              {t('home.startScreening')}
            </Link>
          </div>
        </div>

        {/* Professional Hero Image placeholder */}
        <div className="lg:w-1/2 w-full">
          <div className="w-full aspect-[4/3] rounded-2xl overflow-hidden bg-slate-100 relative shadow-sm border border-slate-200/90 h-80 sm:h-[450px] lg:h-auto">
            <div className="absolute top-5 left-5 z-10 px-4 py-2 bg-white/95 backdrop-blur-md border border-slate-200/90 shadow-sm rounded-xl flex flex-col">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-0.5">{t('home.accuracy')}</span>
              <span className="text-xl font-bold text-slate-900">95.5%</span>
            </div>
            <img
              src="https://images.unsplash.com/photo-1606811841689-23dfddce3e95?auto=format&fit=crop&w=1200&q=80"
              alt="Clinical Medical Setup"
              className="w-full h-full object-cover"
            />
          </div>
        </div>
      </section>

      {/* Types of Lesions Teaser Section (Landing Page Spread) */}
      <section className="w-full border-t border-slate-200/90 pt-16 sm:pt-24 mt-10">
        <div className="flex flex-col xl:flex-row items-center gap-12 sm:gap-16">

          <div className="xl:w-1/3 flex flex-col items-start text-left">
            <h2 className="font-serif text-3xl sm:text-4xl font-bold text-slate-900 mb-5 tracking-tight leading-[1.15]">
              {t('home.commonTitle')}
            </h2>
            <p className="text-slate-500 text-sm sm:text-base leading-relaxed mb-6 font-normal">
              {t('home.commonDesc')}
            </p>
            <Link to="/information" className="inline-flex items-center gap-2 text-blue-600 text-sm font-semibold hover:text-blue-700 transition-colors">
              {t('home.exploreAll')}
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="xl:w-2/3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6 w-full">
            {/* Card 1 */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200/90 overflow-hidden hover:shadow-md transition group cursor-pointer">
              <div className="w-full h-48 bg-slate-100 border-b border-slate-100 relative overflow-hidden">
                <img src="/Ulcer.jpg" alt="Ulcers" className="w-full h-full object-cover blur-md group-hover:blur-0 group-hover:scale-105 transition-all duration-500 opacity-90 group-hover:opacity-100" />
              </div>
              <div className="p-5 sm:p-6">
                <h3 className="font-bold text-slate-900 mb-1">{t('home.ulcer')}</h3>
                <p className="text-sm text-slate-500">{t('home.ulcerDesc')}</p>
              </div>
            </div>

            {/* Card 2 */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200/90 overflow-hidden hover:shadow-md transition group cursor-pointer">
              <div className="w-full h-48 bg-slate-100 border-b border-slate-100 relative overflow-hidden">
                <img src="/Oral_candidiasis.png" alt="Candidiasis" className="w-full h-full object-cover blur-md group-hover:blur-0 group-hover:scale-105 transition-all duration-500 opacity-90 group-hover:opacity-100" />
              </div>
              <div className="p-5 sm:p-6">
                <h3 className="font-bold text-slate-900 mb-1">{t('home.candidiasis')}</h3>
                <p className="text-sm text-slate-500">{t('home.candidiasisDesc')}</p>
              </div>
            </div>

            {/* Card 3 */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200/90 overflow-hidden hover:shadow-md transition group cursor-pointer">
              <div className="w-full h-48 bg-slate-100 border-b border-slate-100 relative overflow-hidden">
                <img src="/Leukoplakia.jpg" alt="Leukoplakia" className="w-full h-full object-cover blur-md group-hover:blur-0 group-hover:scale-105 transition-all duration-500 opacity-90 group-hover:opacity-100" />
              </div>
              <div className="p-5 sm:p-6">
                <h3 className="font-bold text-slate-900 mb-1">{t('home.leuko')}</h3>
                <p className="text-sm text-slate-500">{t('home.leukoDesc')}</p>
              </div>
            </div>
          </div>

        </div>
      </section>
    </main>
  );
}
