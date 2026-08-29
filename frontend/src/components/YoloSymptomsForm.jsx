import React from 'react';

export default function YoloSymptomsForm({ symptoms, setSymptoms }) {
  // 2-column data matching Reference Image 3
  const col1Items = [
    { id: 'noSymptoms', label: 'ไม่มีอาการผิดปกติ' },
    { id: 'drinkAlcohol', label: 'ดื่มเครื่องดื่มแอลกอฮอล์' },
    { id: 'smoking', label: 'สูบบุหรี่' },
    { id: 'chewBetelNut', label: 'เคี้ยวหมาก' },
  ];

  const col2Items = [
    { id: 'eatSpicyFood', label: 'รับประทานอาหารเผ็ดแล้วรู้สึกระคายเคือง' },
    { id: 'wipeOff', label: 'คราบขาวที่สามารถลอกออก' },
    { id: 'alwaysHurts', label: 'มีอาการเจ็บหรือระคายเคืองตลอดเวลา' },
  ];

  const handleToggle = (id) => {
    setSymptoms((prev) => {
      // If user toggles "ไม่มีอาการผิดปกติ"
      if (id === 'noSymptoms') {
        return prev.includes('noSymptoms') ? [] : ['noSymptoms'];
      }

      // If user toggles any other symptom, remove "noSymptoms"
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
      {/* Title from Reference Image 3 */}
      <h3 className="text-base sm:text-lg font-bold text-slate-900 mb-4 tracking-tight">
        อาการผู้ป่วย (เลือกอย่างน้อย 1 ข้อ)
      </h3>

      {/* 2-Column Checkboxes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-y-3.5 gap-x-8">
        {/* Column 1 */}
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

        {/* Column 2 */}
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
