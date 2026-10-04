import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, ChevronLeft, ChevronRight } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { diseaseDetailsData } from '../data/diseaseDetails';

export default function DiseaseDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { lang } = useLanguage();
    const [isBlurred, setIsBlurred] = useState(true);

    // Normalize IDs to prevent 404s
    const normalizedId = id === 'ulcer' ? 'ulcers' : id;
    const diseaseData = diseaseDetailsData[normalizedId];

    // Scroll to top on mount
    useEffect(() => {
        window.scrollTo(0, 0);
    }, [id]);

    if (!diseaseData) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[50vh] text-center">
                <h2 className="text-2xl font-bold text-slate-800 mb-4">Content Not Found</h2>
                <button onClick={() => navigate('/information')} className="text-blue-600 font-medium hover:underline">
                    &larr; Return to Information
                </button>
            </div>
        );
    }

    const content = diseaseData[lang] || diseaseData['TH'];

    return (
        <main className="w-full max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 animate-in fade-in duration-300">
            {/* Header / Title */}
            <div className="mb-6 sm:mb-8 text-left flex flex-col gap-2">
                <button onClick={() => navigate('/information')} className="w-fit mb-3 flex items-center gap-1.5 text-slate-500 hover:text-blue-600 transition-colors text-sm font-medium">
                    <ArrowLeft className="w-4 h-4" />
                    {lang === 'EN' ? 'Back' : 'กลับ'}
                </button>
                <span className="text-xs font-bold text-blue-600 tracking-wider uppercase">
                    {lang === 'EN' ? 'Clinical Information' : 'ข้อมูลรอยโรคทางคลินิก'}
                </span>
                <h1 className="font-serif text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight leading-[1.15]">
                    {content.title}
                </h1>
            </div>

            {/* Image Section */}
            <div
                className="w-full relative rounded-2xl overflow-hidden max-h-[400px] bg-slate-900 border border-slate-200/80 shadow-sm mb-8 sm:mb-10 cursor-pointer group"
                onClick={() => setIsBlurred(!isBlurred)}
            >
                {isBlurred && (
                    <div className="absolute inset-0 flex items-center justify-center z-10 pointer-events-none">
                        <div className="bg-black/60 backdrop-blur-md px-6 py-2 border border-white/20 rounded-full text-white text-sm font-semibold tracking-wide">
                            {lang === 'EN' ? 'Click to reveal clinical image' : 'คลิกเพื่อดูภาพทางคลินิก'}
                        </div>
                    </div>
                )}
                <img
                    src={diseaseData.imgUrl}
                    alt={content.title}
                    className={`w-full max-h-[400px] md:h-[400px] object-contain object-center transition-all duration-700 ease-out ${isBlurred ? 'blur-2xl scale-110 opacity-50' : 'blur-0 scale-100 opacity-100'}`}
                />
            </div>

            {/* Structured Content Sections */}
            <div className="space-y-6 sm:space-y-8">
                {content.sections.map((section, idx) => (
                    <div key={idx} className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-sm">
                        <h2 className="text-lg font-bold text-slate-900 mb-4 pb-4 border-b border-slate-100">
                            {section.title}
                        </h2>
                        <ul className="space-y-3 list-disc list-outside ml-5">
                            {section.items.map((item, i) => (
                                <li key={i} className="text-slate-600 text-sm sm:text-base leading-relaxed pl-1">
                                    {item}
                                </li>
                            ))}
                        </ul>
                    </div>
                ))}
            </div>
        </main>
    );
}
