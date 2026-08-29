import React, { useRef, useState } from 'react';
import { Image as ImageIcon, ArrowUp, Check, X, FileImage } from 'lucide-react';

export default function UploadSection({ file, setFile, previewUrl, setPreviewUrl }) {
  const [isDragging, setIsDragging] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [imageMeta, setImageMeta] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (selectedFile) => {
    if (!selectedFile) return;

    // Validate type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(selectedFile.type)) {
      setErrorMessage('โปรดอัปโหลดไฟล์รูปภาพที่ถูกต้อง (JPG, PNG หรือ WEBP)');
      return;
    }

    // Validate size (max 20MB)
    const maxSize = 20 * 1024 * 1024;
    if (selectedFile.size > maxSize) {
      setErrorMessage('ขนาดไฟล์เกินขีดจำกัด 20MB');
      return;
    }

    setErrorMessage('');
    setFile(selectedFile);

    const objectUrl = URL.createObjectURL(selectedFile);
    setPreviewUrl(objectUrl);

    // Read image dimensions
    const img = new Image();
    img.onload = () => {
      setImageMeta({
        width: img.naturalWidth,
        height: img.naturalHeight,
        sizeKb: (selectedFile.size / 1024).toFixed(1),
        name: selectedFile.name,
        isValidDimensions: img.naturalWidth >= 800 && img.naturalHeight >= 600,
      });
    };
    img.src = objectUrl;
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleRemoveFile = (e) => {
    e.stopPropagation();
    setFile(null);
    setPreviewUrl(null);
    setImageMeta(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <section className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 sm:p-7 transition-all">
      {/* Section Header */}
      <div className="flex items-center gap-3 mb-5">
        <span className="text-xs font-semibold text-slate-400 tracking-wider">01</span>
        <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
          <ImageIcon className="w-4 h-4" />
        </div>
        <div>
          <h2 className="text-sm font-semibold text-slate-900 leading-tight">อัปโหลดภาพถ่าย</h2>
          <p className="text-xs text-slate-400 mt-0.5">ภาพถ่ายรอยโรคภายในช่องปาก</p>
        </div>
      </div>

      {/* Upload Zone */}
      {!previewUrl ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-xl p-8 sm:p-10 text-center transition-all cursor-pointer ${
            isDragging
              ? 'border-blue-500 bg-blueprint-grid-active ring-4 ring-blue-500/10'
              : 'border-blue-200/90 hover:border-blue-400 bg-blueprint-grid'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={(e) => handleFileChange(e.target.files?.[0])}
          />

          {/* Upload Icon inside circular badge */}
          <div className="mx-auto w-10 h-10 rounded-xl bg-blue-50 border border-blue-100/80 shadow-xs flex items-center justify-center text-blue-600 mb-3.5 group-hover:scale-105 transition-transform">
            <ArrowUp className="w-5 h-5 stroke-[2.5]" />
          </div>

          {/* Text Instructions */}
          <div className="text-sm text-slate-700 font-medium">
            ลากและวางภาพที่นี่ หรือ{' '}
            <span className="text-blue-600 underline font-semibold hover:text-blue-700">
              คลิกเพื่อเลือกไฟล์
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">JPG, PNG, WEBP · สูงสุด 20 MB</p>

          {/* Requirement Badges */}
          <div className="mt-5 flex flex-wrap items-center justify-center gap-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-white border border-slate-200/90 text-slate-600 text-xs font-normal shadow-2xs">
              <Check className="w-3.5 h-3.5 text-blue-600 stroke-[2.5]" />
              <span>ภาพถ่ายในช่องปากมีแสงสว่างเพียงพอ</span>
            </div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-white border border-slate-200/90 text-slate-600 text-xs font-normal shadow-2xs">
              <Check className="w-3.5 h-3.5 text-blue-600 stroke-[2.5]" />
              <span>เห็นรอยโรคชัดเจนในกรอบภาพ</span>
            </div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-white border border-slate-200/90 text-slate-600 text-xs font-normal shadow-2xs">
              <Check className="w-3.5 h-3.5 text-blue-600 stroke-[2.5]" />
              <span>ขนาดขั้นต่ำ 800 × 600 px</span>
            </div>
          </div>
        </div>
      ) : (
        /* Image Preview State */
        <div className="relative border border-slate-200 rounded-xl p-4 bg-slate-50/50 flex flex-col sm:flex-row items-center gap-4">
          <div className="relative w-36 h-36 sm:w-44 sm:h-44 rounded-lg overflow-hidden border border-slate-200 bg-white shadow-xs shrink-0 flex items-center justify-center">
            <img
              src={previewUrl}
              alt="ภาพตัวอย่างรอยโรคที่อัปโหลด"
              className="w-full h-full object-contain"
            />
          </div>

          <div className="flex-1 min-w-0 w-full flex flex-col justify-between py-1">
            <div>
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <FileImage className="w-4 h-4 text-blue-600" />
                  <span className="font-semibold text-slate-800 text-sm truncate max-w-xs sm:max-w-md md:max-w-xl">
                    {imageMeta?.name || file?.name}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={handleRemoveFile}
                  className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                  title="ลบรูปภาพ"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="mt-2 space-y-1 text-xs text-slate-500">
                <p>ขนาด: <span className="font-medium text-slate-700">{imageMeta?.sizeKb} KB</span></p>
                {imageMeta?.width && (
                  <p>
                    มิติภาพ:{' '}
                    <span className="font-medium text-slate-700">
                      {imageMeta.width} × {imageMeta.height} px
                    </span>
                  </p>
                )}
              </div>

              {/* Resolution Tag */}
              <div className="mt-3 flex items-center gap-2">
                <span
                  className={`inline-flex items-center gap-1 text-[11px] font-medium px-2.5 py-0.5 rounded-full ${
                    imageMeta?.isValidDimensions
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : 'bg-amber-50 text-amber-700 border border-amber-200'
                  }`}
                >
                  <Check className="w-3 h-3" />
                  {imageMeta?.isValidDimensions ? 'ความละเอียดภาพเหมาะสม' : 'ความละเอียดมาตรฐาน'}
                </span>
                <span className="text-[11px] text-slate-400">พร้อมสำหรับการประมวลผลด้วย AI</span>
              </div>
            </div>

            <div className="mt-4 flex items-center gap-3">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="text-xs text-blue-600 hover:text-blue-700 font-medium underline"
              >
                เปลี่ยนภาพถ่าย
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={(e) => handleFileChange(e.target.files?.[0])}
              />
            </div>
          </div>
        </div>
      )}

      {errorMessage && (
        <p className="text-xs font-medium text-rose-600 mt-2.5">{errorMessage}</p>
      )}
    </section>
  );
}
