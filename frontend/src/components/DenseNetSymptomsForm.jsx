import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';

export default function DenseNetSymptomsForm({
  symptoms = [],
  setSymptoms,
  lesionFeatures = [],
  setLesionFeatures,
  lesionLocations = [],
  setLesionLocations,
  clinicalNotes = '',
  setClinicalNotes,
}) {
  const { t } = useLanguage();

  const historyCol1 = [
    { id: 'noSymptoms', label: t('symptoms.noSymptoms') },
    { id: 'smoking', label: t('symptoms.smoking') },
    { id: 'eatSpicyFood', label: t('symptoms.eatSpicy') },
    { id: 'alwaysHurts', label: t('symptoms.alwaysHurts') },
  ];

  const historyCol2 = [
    { id: 'drinkAlcohol', label: t('symptoms.drinkAlcohol') },
    { id: 'chewBetelNut', label: t('symptoms.chewBet') },
    { id: 'wipeOff', label: t('symptoms.wipeOff') },
  ];

  const featureCol1 = [
    { id: 'whitePatch', label: t('symptoms.whitePatch') },
    { id: 'whitePlaque', label: t('symptoms.whitePlaque') },
    { id: 'whiteYellowLesion', label: t('symptoms.whiteYellow') },
  ];

  const featureCol2 = [
    { id: 'whiteReticular', label: t('symptoms.whiteRet') },
    { id: 'whiteRaisedLine', label: t('symptoms.whiteRaised') },
  ];

  const locationCol1 = [
    { id: 'tongue', label: t('symptoms.tongue') },
    { id: 'palate', label: t('symptoms.palate') },
    { id: 'lip', label: t('symptoms.lip') },
    { id: 'softTissue', label: t('symptoms.softTissue') },
  ];

  const locationCol2 = [
    { id: 'buccalMucosa', label: t('symptoms.buccal') },
    { id: 'gingiva', label: t('symptoms.gingiva') },
    { id: 'floorOfMouth', label: t('symptoms.floor') },
    { id: 'pharynx', label: t('symptoms.pharynx') },
  ];

  const handleToggleArray = (id, list, setList, isSymptom = false) => {
    if (isSymptom && id === 'noSymptoms') {
      setList((prev) => (prev.includes('noSymptoms') ? [] : ['noSymptoms']));
      return;
    }

    setList((prev) => {
      const filtered = isSymptom ? prev.filter((item) => item !== 'noSymptoms') : prev;
      if (filtered.includes(id)) {
        return filtered.filter((item) => item !== id);
      } else {
        return [...filtered, id];
      }
    });
  };

  return (
    <div className="space-y-6">
      {/* 1 */}
      <div>
        <h3 className="text-sm sm:text-base font-bold text-slate-900 leading-tight">
          {t('symptoms.denseHistHeader')}
        </h3>
        <p className="text-xs text-slate-500 mt-1 mb-3.5">
          {t('symptoms.denseHistHint')}
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-y-3.5 gap-x-8">
          <div className="space-y-3.5">
            {historyCol1.map((item) => (
              <label key={item.id} className="flex items-center gap-3 cursor-pointer select-none group">
                <input type="checkbox" className="custom-checkbox" checked={symptoms.includes(item.id)} onChange={() => handleToggleArray(item.id, symptoms, setSymptoms, true)} />
                <span className="text-sm text-slate-700 font-normal group-hover:text-slate-900 transition-colors">{item.label}</span>
              </label>
            ))}
          </div>
          <div className="space-y-3.5">
            {historyCol2.map((item) => (
              <label key={item.id} className="flex items-center gap-3 cursor-pointer select-none group">
                <input type="checkbox" className="custom-checkbox" checked={symptoms.includes(item.id)} onChange={() => handleToggleArray(item.id, symptoms, setSymptoms, true)} />
                <span className="text-sm text-slate-700 font-normal group-hover:text-slate-900 transition-colors">{item.label}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* 2 */}
      <div className="pt-2">
        <h3 className="text-sm sm:text-base font-bold text-slate-900 mb-3.5">
          {t('symptoms.denseFeatHeader')}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-y-3.5 gap-x-8">
          <div className="space-y-3.5">
            {featureCol1.map((item) => (
              <label key={item.id} className="flex items-center gap-3 cursor-pointer select-none group">
                <input type="checkbox" className="custom-checkbox" checked={lesionFeatures.includes(item.id)} onChange={() => handleToggleArray(item.id, lesionFeatures, setLesionFeatures)} />
                <span className="text-sm text-slate-700 font-normal group-hover:text-slate-900 transition-colors">{item.label}</span>
              </label>
            ))}
          </div>
          <div className="space-y-3.5">
            {featureCol2.map((item) => (
              <label key={item.id} className="flex items-center gap-3 cursor-pointer select-none group">
                <input type="checkbox" className="custom-checkbox" checked={lesionFeatures.includes(item.id)} onChange={() => handleToggleArray(item.id, lesionFeatures, setLesionFeatures)} />
                <span className="text-sm text-slate-700 font-normal group-hover:text-slate-900 transition-colors">{item.label}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* 3 */}
      <div className="pt-2">
        <h3 className="text-sm sm:text-base font-bold text-slate-900 mb-3.5">
          {t('symptoms.denseLocHeader')}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-y-3.5 gap-x-8">
          <div className="space-y-3.5">
            {locationCol1.map((item) => (
              <label key={item.id} className="flex items-center gap-3 cursor-pointer select-none group">
                <input type="checkbox" className="custom-checkbox" checked={lesionLocations.includes(item.id)} onChange={() => handleToggleArray(item.id, lesionLocations, setLesionLocations)} />
                <span className="text-sm text-slate-700 font-normal group-hover:text-slate-900 transition-colors">{item.label}</span>
              </label>
            ))}
          </div>
          <div className="space-y-3.5">
            {locationCol2.map((item) => (
              <label key={item.id} className="flex items-center gap-3 cursor-pointer select-none group">
                <input type="checkbox" className="custom-checkbox" checked={lesionLocations.includes(item.id)} onChange={() => handleToggleArray(item.id, lesionLocations, setLesionLocations)} />
                <span className="text-sm text-slate-700 font-normal group-hover:text-slate-900 transition-colors">{item.label}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* 4 */}
      <div className="pt-2">
        <label htmlFor="clinical-notes" className="block text-sm sm:text-base font-bold text-slate-900 mb-2">
          {t('symptoms.denseNoteHeader')}
        </label>
        <textarea
          id="clinical-notes"
          rows={4}
          value={clinicalNotes}
          onChange={(e) => setClinicalNotes(e.target.value)}
          placeholder={t('symptoms.denseNoteHint')}
          className="w-full rounded-xl border border-slate-200/90 p-3.5 text-sm text-slate-800 placeholder-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 focus:outline-none transition resize-y min-h-[110px]"
        />
      </div>
    </div>
  );
}
