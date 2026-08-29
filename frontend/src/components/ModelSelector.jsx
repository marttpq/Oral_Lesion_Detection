import React from 'react';
import { Cpu, Clock } from 'lucide-react';

export default function ModelSelector({ selectedModel, setSelectedModel }) {
  const models = [
    {
      id: 'yolov7',
      tag: 'การตรวจจับ (Detection)',
      tagType: 'slate',
      title: 'YOLOv7',
      description:
        'โมเดลตรวจจับวัตถุสถาปัตยกรรม YOLOv7 ระบุตำแหน่งและตีกรอบ Bounding Box ของรอยโรคในภาพ',
      output: 'ผลลัพธ์: ตรวจจับรอยโรคและตีกรอบ Bounding Box',
      requiresHistory: false,
    },
    {
      id: 'yolov8',
      tag: 'การตรวจจับ (Detection)',
      tagType: 'blue',
      title: 'YOLOv8',
      description:
        'โมเดลตรวจจับวัตถุสถาปัตยกรรม YOLOv8 ระบุตำแหน่งและตีกรอบ Bounding Box ของรอยโรคในภาพ',
      output: 'ผลลัพธ์: ตรวจจับรอยโรคและตีกรอบ Bounding Box',
      requiresHistory: false,
    },
    {
      id: 'densenet-bert',
      tag: 'มัลติโมดอล (Multimodal)',
      tagType: 'purple',
      title: 'DenseNet + WangchanBERTa',
      description:
        'ผสานคุณลักษณะภาพจาก DenseNet เข้ากับข้อความประวัติทางคลินิกที่แปลงด้วย WangchanBERTa เพื่อวินิจฉัยจำแนกโรคแบบองค์รวม',
      output: 'ผลลัพธ์: การวินิจฉัยจำแนกโรค (Classification)',
      requiresHistory: true,
    },
  ];

  // Current active model's capability tag for the section header
  const activeModelObj = models.find((m) => m.id === selectedModel) || models[1];

  return (
    <section className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 sm:p-7 transition-all">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold text-slate-400 tracking-wider">02</span>
          <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-900 leading-tight">เลือกโมเดล AI</h2>
            <p className="text-xs text-slate-400 mt-0.5">เลือกสถาปัตยกรรมสำหรับการวิเคราะห์</p>
          </div>
        </div>

        {/* Right header pill badge */}
        <div className="self-start sm:self-auto">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-50/90 text-blue-600 border border-blue-100">
            {activeModelObj.tag}
          </span>
        </div>
      </div>

      {/* 3 Model Selection Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 sm:gap-4">
        {models.map((model) => {
          const isSelected = selectedModel === model.id;

          return (
            <div
              key={model.id}
              onClick={() => setSelectedModel(model.id)}
              className={`relative rounded-xl p-4 sm:p-4.5 flex flex-col justify-between cursor-pointer transition-all border ${isSelected
                ? 'border-2 border-blue-600 bg-blue-50/15 shadow-xs ring-1 ring-blue-500/15'
                : 'border-slate-200 hover:border-slate-300 bg-white hover:bg-slate-50/40'
                }`}
            >
              {/* Card Top: Tag + Radio Button */}
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span
                    className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] font-medium tracking-wide ${isSelected
                      ? 'bg-blue-100/80 text-blue-700'
                      : 'bg-slate-100 text-slate-600'
                      }`}
                  >
                    {model.tag}
                  </span>

                  {/* Radio Icon */}
                  <div
                    className={`w-4 h-4 rounded-full flex items-center justify-center transition-all ${isSelected
                      ? 'bg-blue-600 ring-2 ring-blue-600/20 text-white'
                      : 'border-2 border-slate-300 bg-white'
                      }`}
                  >
                    {isSelected && (
                      <div className="w-1.5 h-1.5 rounded-full bg-white" />
                    )}
                  </div>
                </div>

                {/* Model Title */}
                <h3 className="text-sm font-bold text-slate-900 mb-1.5">{model.title}</h3>

                {/* Model Description */}
                <p className="text-xs text-slate-500 leading-relaxed font-normal">
                  {model.description}
                </p>
              </div>

              {/* Card Bottom: Output & History Indicator */}
              <div className="mt-5 pt-3 border-t border-slate-100">
                <div className="text-[11px] text-slate-500">
                  <span className="font-medium text-slate-600">{model.output.split(':')[0]}:</span>
                  <span className="ml-1 text-slate-500">{model.output.split(':')[1]}</span>
                </div>

                {model.requiresHistory && (
                  <div className="mt-1.5 flex items-center gap-1 text-[11px] text-slate-500">
                    <Clock className="w-3 h-3 text-slate-400" />
                    <span>สามารถกรอกประวัติอาการผู้ป่วยเพื่อเพิ่มความแม่นยำในการประเมิน</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
