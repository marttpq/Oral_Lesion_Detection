import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';

export default function YoloSymptomsForm({ symptoms, setSymptoms }) {
  const { t } = useLanguage();

  // Notice that `id` values remain exactly the same to preserve Backend mapping!
  const col1Items = [
    { id: 'noSymptoms', label: t('symptoms.noSymptoms') },
    { id: 'drinkAlcohol', label: t('symptoms.drinkAlcohol') },
    { id: 'smoking', label: t('symptoms.smoking') },
    { id: 'chewBetelNut', label: t('symptoms.chewBet') },
  ];

  const col2Items = [
    { id: 'eatSpicyFood', label: t('symptoms.eatSpicy') },
    { id: 'wipeOff', label: t('symptoms.wipeOff') },
    { id: 'alwaysHurts', label: t('symptoms.alwaysHurts') },
  ];

  const handleToggle = (id) => {
    setSymptoms((prev) => {
      if (id === 'noSymptoms') {
        return prev.includes('noSymptoms') ? [] : ['noSymptoms'];
      }

      const filtered = prev.filter((item) => item !== 'noSymptoms');
      if (filtered.includes(id)) {
        return filtered.filter((item) => item !== id);
      } else {
        return [...filtered, id];
      }
    });
  };

  return (
    <div>
      <h3 className="text-base sm:text-lg font-bold text-slate-900 mb-4 tracking-tight">
        {t('symptoms.yoloHeader')}
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-y-3.5 gap-x-8">
        <div className="space-y-3.5">
          {col1Items.map((item) => (
            <label
              key={item.id}
              className="flex items-center gap-3 cursor-pointer select-none group"
            >
              <input
                type="checkbox"
                className="custom-checkbox"
                checked={symptoms.includes(item.id)}
                onChange={() => handleToggle(item.id)}
              />
              <span className="text-sm text-slate-700 font-normal group-hover:text-slate-900 transition-colors">
                {item.label}
              </span>
            </label>
          ))}
        </div>

        <div className="space-y-3.5">
          {col2Items.map((item) => (
            <label
              key={item.id}
              className="flex items-center gap-3 cursor-pointer select-none group"
            >
              <input
                type="checkbox"
                className="custom-checkbox"
                checked={symptoms.includes(item.id)}
                onChange={() => handleToggle(item.id)}
              />
              <span className="text-sm text-slate-700 font-normal group-hover:text-slate-900 transition-colors">
                {item.label}
              </span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}
