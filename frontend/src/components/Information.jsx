import React from 'react';
import { BookOpen } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';

export default function Information() {
    const { lang, t, translations } = useLanguage();

    // Grabbing the pure array from translations logic
    const diseases = translations[lang]?.info?.diseases || translations['EN'].info.diseases;

    return (
        <main className="w-full max-w-[95%] 2xl:max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 animate-in fade-in duration-300">
            {/* Title & Introduction Section */}
            <div className="mb-8 sm:mb-10 text-left flex items-start gap-3">
                <div className="mt-1 w-6 h-6 rounded-md bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                    <BookOpen className="w-4 h-4" />
                </div>
                <div>
                    <span className="text-xs font-bold text-blue-600 tracking-wider uppercase block mb-2">
                        {t('info.title')}
                    </span>
                    <h1 className="font-serif text-3xl sm:text-4xl lg:text-[42px] font-bold text-slate-900 tracking-tight leading-[1.15] mb-3">
                        {t('nav.info')}
                    </h1>
                    <p className="text-slate-500 text-sm sm:text-base leading-relaxed max-w-4xl font-normal">
                        {t('info.desc')}
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-7 w-full">
                {diseases.map((disease) => (
                    <Link to={`/information/${disease.id}`} key={disease.id} className="bg-white rounded-2xl overflow-hidden border border-slate-200/90 shadow-sm hover:shadow-md transition-shadow flex flex-col group cursor-pointer">
                        <div className="w-full h-48 sm:h-52 bg-slate-100 relative overflow-hidden border-b border-slate-100">
                            <img src={disease.imgUrl} alt={disease.title} className="w-full h-full object-cover blur-md group-hover:blur-0 group-hover:scale-105 transition-all duration-500 opacity-90 group-hover:opacity-100" />
                        </div>
                        <div className="p-5 sm:p-6 flex flex-col flex-1">
                            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                                {t('info.biomarker')}
                            </span>
                            <h3 className="text-lg font-bold text-slate-900 mb-2">{disease.title}</h3>
                            <p className="text-slate-500 text-[13px] sm:text-sm leading-relaxed flex-1">
                                {disease.description}
                            </p>
                        </div>
                    </Link>
                ))}
            </div>
        </main>
    );
}
