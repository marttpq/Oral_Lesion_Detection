import React from 'react';

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
  // Category 1: ประวัติ/อาการผู้ป่วย
  const historyCol1 = [
    { id: 'noSymptoms', label: 'ไม่มีอาการผิดปกติ' },
    { id: 'smoking', label: 'สูบบุหรี่' },
    { id: 'eatSpicyFood', label: 'รับประทานอาหารเผ็ดแล้วรู้สึกระคายเคือง' },
    { id: 'alwaysHurts', label: 'มีอาการเจ็บหรือระคายเคืองตลอดเวลา' },
  ];

  const historyCol2 = [
    { id: 'drinkAlcohol', label: 'ดื่มเครื่องดื่มแอลกอฮอล์' },
    { id: 'chewBetelNut', label: 'เคี้ยวหมาก' },
    { id: 'wipeOff', label: 'คราบขาวที่สามารถลอกออกได้' },
  ];

  // Category 2: ลักษณะรอยโรค
  const featureCol1 = [
    { id: 'whitePatch', label: 'ปื้นขาว' },
    { id: 'whitePlaque', label: 'ฝ้าขาวเช็ดออกได้' },
    { id: 'whiteYellowLesion', label: 'แผลสีขาวเหลือง' },
  ];

  const featureCol2 = [
    { id: 'whiteReticular', label: 'เส้นสีขาวคล้ายร่างแห' },
    { id: 'whiteRaisedLine', label: 'เส้นสีขาวนูน' },
  ];

  // Category 3: บริเวณรอยโรค
  const locationCol1 = [
    { id: 'tongue', label: 'ลิ้น' },
    { id: 'palate', label: 'เพดานปาก' },
    { id: 'lip', label: 'ริมฝีปาก' },
    { id: 'softTissue', label: 'เยื่อบุริมฝีปากด้านใน' },
  ];

  const locationCol2 = [
    { id: 'buccalMucosa', label: 'กระพุ้งแก้ม' },
    { id: 'gingiva', label: 'เหงือก' },
    { id: 'floorOfMouth', label: 'พื้นปาก' },
    { id: 'pharynx', label: 'คอหอย' },
  ];

  // Toggle helper for arrays
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
      {/* 1. ประวัติ/อาการผู้ป่วย */}
      <div>
        <h3 className="text-sm sm:text-base font-bold text-slate-900 leading-tight">
          ประวัติ/อาการผู้ป่วย
        </h3>
        <p className="text-xs text-slate-500 mt-1 mb-3.5">
          โปรดเลือกจากรายการ หรือพิมพ์เพิ่มเติม (หากไม่ได้เลือกหรือพิมพ์ ระบบจะบันทึกว่า
          "ไม่มีอาการผิดปกติ" โดยอัตโนมัติ)
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-y-3.5 gap-x-8">
          <div className="space-y-3.5">
            {historyCol1.map((item) => (
              <label
                key={item.id}
                className="flex items-center gap-3 cursor-pointer select-none group"
              >
                <input
                  type="checkbox"
                  className="custom-checkbox"
                  checked={symptoms.includes(item.id)}
                  onChange={() => handleToggleArray(item.id, symptoms, setSymptoms, true)}
                />
                <span className="text-sm text-slate-700 font-normal group-hover:text-slate-900 transition-colors">
                  {item.label}
                </span>
              </label>
            ))}
          </div>

          <div className="space-y-3.5">
            {historyCol2.map((item) => (
              <label
                key={item.id}
                className="flex items-center gap-3 cursor-pointer select-none group"
              >
                <input
                  type="checkbox"
                  className="custom-checkbox"
                  checked={symptoms.includes(item.id)}
                  onChange={() => handleToggleArray(item.id, symptoms, setSymptoms, true)}
                />
                <span className="text-sm text-slate-700 font-normal group-hover:text-slate-900 transition-colors">
                  {item.label}
                </span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* 2. ลักษณะรอยโรค */}
      <div className="pt-2">
        <h3 className="text-sm sm:text-base font-bold text-slate-900 mb-3.5">
          ลักษณะรอยโรค
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-y-3.5 gap-x-8">
          <div className="space-y-3.5">
            {featureCol1.map((item) => (
              <label
                key={item.id}
                className="flex items-center gap-3 cursor-pointer select-none group"
              >
                <input
                  type="checkbox"
                  className="custom-checkbox"
                  checked={lesionFeatures.includes(item.id)}
                  onChange={() => handleToggleArray(item.id, lesionFeatures, setLesionFeatures)}
                />
                <span className="text-sm text-slate-700 font-normal group-hover:text-slate-900 transition-colors">
                  {item.label}
                </span>
              </label>
            ))}
          </div>

          <div className="space-y-3.5">
            {featureCol2.map((item) => (
              <label
                key={item.id}
                className="flex items-center gap-3 cursor-pointer select-none group"
              >
                <input
                  type="checkbox"
                  className="custom-checkbox"
                  checked={lesionFeatures.includes(item.id)}
                  onChange={() => handleToggleArray(item.id, lesionFeatures, setLesionFeatures)}
                />
                <span className="text-sm text-slate-700 font-normal group-hover:text-slate-900 transition-colors">
                  {item.label}
                </span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* 3. บริเวณรอยโรค */}
      <div className="pt-2">
        <h3 className="text-sm sm:text-base font-bold text-slate-900 mb-3.5">
          บริเวณรอยโรค
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-y-3.5 gap-x-8">
          <div className="space-y-3.5">
            {locationCol1.map((item) => (
              <label
                key={item.id}
                className="flex items-center gap-3 cursor-pointer select-none group"
              >
                <input
                  type="checkbox"
                  className="custom-checkbox"
                  checked={lesionLocations.includes(item.id)}
                  onChange={() => handleToggleArray(item.id, lesionLocations, setLesionLocations)}
                />
                <span className="text-sm text-slate-700 font-normal group-hover:text-slate-900 transition-colors">
                  {item.label}
                </span>
              </label>
            ))}
          </div>

          <div className="space-y-3.5">
            {locationCol2.map((item) => (
              <label
                key={item.id}
                className="flex items-center gap-3 cursor-pointer select-none group"
              >
                <input
                  type="checkbox"
                  className="custom-checkbox"
                  checked={lesionLocations.includes(item.id)}
                  onChange={() => handleToggleArray(item.id, lesionLocations, setLesionLocations)}
                />
                <span className="text-sm text-slate-700 font-normal group-hover:text-slate-900 transition-colors">
                  {item.label}
                </span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* 4. รายละเอียดอาการเพิ่มเติม */}
      <div className="pt-2">
        <label
          htmlFor="clinical-notes"
          className="block text-sm sm:text-base font-bold text-slate-900 mb-2"
        >
          รายละเอียดอาการเพิ่มเติม:
        </label>
        <textarea
          id="clinical-notes"
          rows={4}
          value={clinicalNotes}
          onChange={(e) => setClinicalNotes(e.target.value)}
          placeholder="เช่น มีอาการปวดเป็นบางครั้ง, เป็นมานาน 2 สัปดาห์ ..."
          className="w-full rounded-xl border border-slate-200/90 p-3.5 text-sm text-slate-800 placeholder-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 focus:outline-none transition resize-y min-h-[110px]"
        />
      </div>
    </div>
  );
}
