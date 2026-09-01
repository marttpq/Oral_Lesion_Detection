import React, { createContext, useContext, useState } from 'react';

const LanguageContext = createContext();

export const translations = {
    TH: {
        nav: {
            home: "หน้าแรก",
            info: "โรคในช่องปาก",
            startAssessment: "เริ่มการประเมิน",
            login: "เข้าสู่ระบบ"
        },
        home: {
            tag: "ระบบประเมินรอยโรคด้วย AI",
            title1: "วิเคราะห์และประเมินรอยโรค",
            title2: "ในช่องปากอย่างแม่นยำ",
            desc: "ยกระดับความมั่นใจในการวินิจฉัยด้วย Medical AI เราผสานภาพถ่ายภายในช่องปากกับประวัติผู้ป่วย เพื่อประเมินความเสี่ยงได้รวดเร็วและแม่นยำสูง",
            startScreening: "เริ่มการคัดกรอง",
            patientInfo: "ข้อมูลผู้ป่วย",
            accuracy: "ความแม่นยำ",
            timeText: "เวลาประมวลผล",
            commonTitle: "รอยโรคในช่องปากที่พบบ่อย",
            commonDesc: "AI ของเราได้รับการฝึกสอนให้จดจำรอยโรคในช่องปากหลายรูปแบบ การเข้าใจลักษณะของโรคเหล่านี้เป็นก้าวแรกสู่การวินิจฉัยที่ถูกต้อง",
            exploreAll: "ดูโรคทั้งหมด",
            ulcer: "แผลร้อนใน (Aphthous Ulcers)",
            ulcerDesc: "แผลตื้นและเจ็บ บริเวณเนื้อเยื่ออ่อน",
            candidiasis: "เชื้อราในช่องปาก (Candidiasis)",
            candidiasisDesc: "ฝ้าขาวจากเชื้อรา มักพบบนลิ้นหรือกระพุ้งแก้ม",
            leuko: "รอยโรคฝ้าขาว (Leukoplakia)",
            leukoDesc: "แผ่นฝ้าขาวหนา อาจมีความเสี่ยงก่อมะเร็ง"
        },
        info: {
            title: "ข้อมูลอ้างอิงรอยโรค",
            desc: "ระบบของเราตรวจสอบรอยโรคจากฐานข้อมูลที่ครอบคลุม นี่คือข้อมูลอ้างอิงทางคลินิกที่สำคัญซึ่ง AI ของเราสามารถตรวจพบลักษณะอาการเบื้องต้นได้",
            biomarker: "ลักษณะทางภาพถ่าย",
            diseases: [
                {
                    id: "ulcers", title: "แผลร้อนใน (Aphthous Ulcers)",
                    description: "รู้จักกันทั่วไปว่าแผลร้อนใน เป็นรอยโรคตื้นๆ ขนาดเล็กที่เกิดบนเนื้อเยื่ออ่อนในช่องปากหรือบริเวณเหงือก มีอาการเจ็บ ทำให้กินและพูดลำบาก"
                },
                {
                    id: "candidiasis", title: "เชื้อราในช่องปาก (Candidiasis)",
                    description: "การติดเชื้อรา (Candida) ที่เกิดบนเยื่อบุช่องปาก มักปรากฏเป็นฝ้าขาวหรือรอยโรคบริเวณลิ้นหรือกระพุ้งแก้มด้านใน"
                },
                {
                    id: "leukoplakia", title: "รอยโรคฝ้าขาว (Leukoplakia)",
                    description: "แผ่นฝ้าขาวสีขุ่นที่ก่อตัวบริเวณเหงือก กระพุ้งแก้มด้านใน พื้นปาก หรือบางครั้งบนลิ้น ข้อสังเกตคือขูดไม่ออก ถือเป็นภาวะความเสี่ยงก่อนเป็นมะเร็ง"
                },
                {
                    id: "lichen-planus", title: "ไลเคน พลานัส (Oral Lichen Planus)",
                    description: "ภาวะอักเสบเรื้อรังที่ส่งผลกระทบต่อเยื่อบุในช่องปาก อาจปรากฏเป็นรอยเส้นสีขาวคล้ายร่างแห บางครั้งอาจมีแผลเจ็บร่วมด้วย"
                },
                {
                    id: "scc", title: "มะเร็งเซลล์สความัส (SCC)",
                    description: "รูปแบบมะเร็งช่องปากที่พบบ่อยที่สุด มักปรากฏเป็นแผลเรื้อรังที่ไม่หาย ก้อนเนื้อ หรือฝ้าหนา การตรวจพบแต่เนิ่นๆ ข่วยเพิ่มอัตราการรอดชีวิต"
                },
                {
                    id: "herpes", title: "เริม (Herpes Simplex)",
                    description: "การติดเชื้อไวรัสที่แสดงอาการเป็นตุ่มน้ำใสเจ็บปวด มักเกิดบนหรือรอบริมฝีปาก แต่บางครั้งอาจเกิดขึ้นในช่องปาก มักเกิดเป็นกลุ่มก้อน"
                }
            ]
        },
        dashboard: {
            headerTag: "การประเมินด้วย AI",
            title: "ระบบประเมินความเสี่ยงรอยโรคในช่องปาก",
            desc: "อัปโหลดภาพถ่ายในช่องปาก เลือกโมเดล AI และสามารถกรอกประวัติผู้ป่วยเพิ่มเติมสำหรับการวิเคราะห์แบบมัลติโมดอล",
            uploadTitle: "อัปโหลดภาพถ่าย",
            uploadSubtitle: "ภาพถ่ายรอยโรคภายในช่องปาก",
            dragDrop1: "ลากและวางภาพที่นี่ หรือ ",
            dragDrop2: "คลิกเพื่อเลือกไฟล์",
            uploadReq1: "ภาพถ่ายในช่องปากมีแสงสว่างเพียงพอ",
            uploadReq2: "เห็นรอยโรคชัดเจนในกรอบภาพ",
            uploadReq3: "ขนาดขั้นต่ำ 800 × 600 px",
            modelTitle: "เลือกโมเดล AI",
            modelSubtitle: "เลือกสถาปัตยกรรมสำหรับการวิเคราะห์",
            modelYOLO: "การตรวจจับ (Detection)",
            modelMulti: "มัลติโมดอล (Multimodal)",
            sympTitle: "อาการและประวัติผู้ป่วย",
            sympSub1: "ปัจจัยเสี่ยงและอาการที่สังเกตได้ทางคลินิก",
            sympSub2: "ปัจจัยเสี่ยงทางคลินิกและลักษณะรอยโรคอย่างละเอียด",
            resetForm: "ล้างข้อมูลฟอร์ม",
            errorForm: "โปรดอัปโหลดภาพถ่ายในช่องปากก่อนส่งข้อมูลเพื่อทำการประเมินด้วย AI",
            errorSubmit: "เกิดข้อผิดพลาดในการประเมิน: ",
            processing: "กำลังประมวลผลการประเมิน...",
            startAi: "เริ่มการประเมินด้วย AI",
            modalTitle: "ผลการประเมินจาก AI",
            modalModel: "โมเดล",
            modalLesionDetected: "รอยโรคที่ตรวจพบ",
            modalNoLesion: "ตรวจไม่พบรอยโรค",
            modalConf: "ความเชื่อมั่น",
            modalImgContext: "ผลลัพธ์ภาพประมวลผล AI",
            modalImgTitle: "ภาพถ่ายหลังการประมวลผล / กรอบ Bounding Boxes",
            modalImgDesc: "ผลลัพธ์จากโมเดล",
            modalBboxDetected: "กรอบ Bounding Boxes ที่ตรวจพบ",
            modalClose: "ปิดหน้าต่าง"
        },
        upload: {
            changeImage: "เปลี่ยนภาพถ่าย",
            deleteImage: "ลบรูปภาพ",
            size: "ขนาด:",
            dim: "มิติภาพ:",
            validDim: "ความละเอียดภาพเหมาะสม",
            standardDim: "ความละเอียดมาตรฐาน",
            readyAi: "พร้อมสำหรับการประมวลผลด้วย AI",
            typeError: "โปรดอัปโหลดไฟล์รูปภาพที่ถูกต้อง (JPG, PNG หรือ WEBP)",
            sizeError: "ขนาดไฟล์เกินขีดจำกัด 20MB",
            sizeLimit: "JPG, PNG, WEBP · สูงสุด 20 MB"
        },
        models: {
            detectOutput: "ผลลัพธ์: ตรวจจับรอยโรคและตีกรอบ Bounding Box",
            classOutput: "ผลลัพธ์: การวินิจฉัยจำแนกโรค (Classification)",
            historyTip: "สามารถกรอกประวัติอาการผู้ป่วยเพื่อเพิ่มความแม่นยำในการประเมิน",
            yolo7desc: "โมเดลตรวจจับวัตถุสถาปัตยกรรม YOLOv7 ระบุตำแหน่งและตีกรอบ Bounding Box ของรอยโรคในภาพ",
            yolo8desc: "โมเดลตรวจจับวัตถุสถาปัตยกรรม YOLOv8 ระบุตำแหน่งและตีกรอบ Bounding Box ของรอยโรคในภาพ",
            densedesc: "ผสานคุณลักษณะภาพจาก DenseNet เข้ากับข้อความประวัติทางคลินิกที่แปลงด้วย WangchanBERTa เพื่อวินิจฉัยจำแนกโรคแบบองค์รวม"
        },
        symptoms: {
            yoloHeader: "อาการผู้ป่วย (เลือกอย่างน้อย 1 ข้อ)",
            denseHistHeader: "ประวัติ/อาการผู้ป่วย",
            denseHistHint: 'โปรดเลือกจากรายการ หรือพิมพ์เพิ่มเติม (หากไม่ได้เลือกหรือพิมพ์ ระบบจะบันทึกว่า "ไม่มีอาการผิดปกติ" โดยอัตโนมัติ)',
            denseFeatHeader: "ลักษณะรอยโรค",
            denseLocHeader: "บริเวณรอยโรค",
            denseNoteHeader: "รายละเอียดอาการเพิ่มเติม:",
            denseNoteHint: "เช่น มีอาการปวดเป็นบางครั้ง, เป็นมานาน 2 สัปดาห์ ...",
            noSymptoms: "ไม่มีอาการผิดปกติ",
            drinkAlcohol: "ดื่มเครื่องดื่มแอลกอฮอล์",
            smoking: "สูบบุหรี่",
            chewBet: "เคี้ยวหมาก",
            eatSpicy: "รับประทานอาหารเผ็ดแล้วรู้สึกระคายเคือง",
            wipeOff: "คราบขาวที่สามารถลอกออกได้",
            alwaysHurts: "มีอาการเจ็บหรือระคายเคืองตลอดเวลา",
            whitePatch: "ปื้นขาว",
            whitePlaque: "ฝ้าขาวเช็ดออกได้",
            whiteYellow: "แผลสีขาวเหลือง",
            whiteRet: "เส้นสีขาวคล้ายร่างแห",
            whiteRaised: "เส้นสีขาวนูน",
            tongue: "ลิ้น",
            palate: "เพดานปาก",
            lip: "ริมฝีปาก",
            softTissue: "เยื่อบุริมฝีปากด้านใน",
            buccal: "กระพุ้งแก้ม",
            gingiva: "เหงือก",
            floor: "พื้นปาก",
            pharynx: "คอหอย"
        },
        login: {
            title: "ลงชื่อเข้าใช้งาน",
            subtitle: "ยินดีต้อนรับกลับเข้าสู่ระบบ OralScan AI",
            email: "อีเมล",
            password: "รหัสผ่าน",
            forgotPassword: "ลืมรหัสผ่าน?",
            signIn: "เข้าสู่ระบบ",
            noAccount: "ยังไม่มีบัญชี?",
            signUp: "สมัครใช้งาน"
        }
    },
    EN: {
        nav: {
            home: "Home",
            info: "Information",
            startAssessment: "Assessment",
            login: "Log In"
        },
        home: {
            tag: "Oral Health AI Assessment",
            title1: "Precision Screening for",
            title2: "Oral Lesions.",
            desc: "Empowering dental professionals with expert-level risk assessment. Our AI analyzes visual biomarkers and patient history to provide rapid, reliable second opinions.",
            startScreening: "Start Clinical Screening",
            patientInfo: "Patient Information",
            accuracy: "Accuracy",
            timeText: "Analysis Time",
            commonTitle: "Common Oral Pathologies",
            commonDesc: "Our AI models are trained to recognize various forms of oral lesions. Understanding these visual biomarkers is the first step towards accurate diagnosis and early intervention.",
            exploreAll: "Explore all diseases",
            ulcer: "Aphthous Ulcers",
            ulcerDesc: "Shallow, painful lesions primarily on soft tissues.",
            candidiasis: "Oral Candidiasis",
            candidiasisDesc: "White fungal patches often seen on the tongue or cheeks.",
            leuko: "Leukoplakia",
            leukoDesc: "Thick white patches indicating potential malignant risk."
        },
        info: {
            title: "Clinical Conditions Reference",
            desc: "Our systems screen against a robust library of conditions. Consult this clinical reference outlining the primary pathologies identified by our Multimodal AI.",
            biomarker: "Visual Biomarker",
            diseases: [
                {
                    id: "ulcers", title: "Aphthous Ulcers",
                    description: "Commonly known as canker sores. These are small, shallow lesions developing on soft tissues. Painful, making eating and tracking difficult."
                },
                {
                    id: "candidiasis", title: "Oral Candidiasis",
                    description: "Fungal infection caused by yeast (Candida) developing on mucous membranes. Shows as white patches."
                },
                {
                    id: "leukoplakia", title: "Leukoplakia",
                    description: "Thick white patches that cannot be scraped off, formed on gums or insides of cheeks. Potentially malignant."
                },
                {
                    id: "lichen-planus", title: "Oral Lichen Planus",
                    description: "Chronic inflammatory condition affecting mucous membranes. Appears as lacy white patches, sometimes with painful sores."
                },
                {
                    id: "scc", title: "Squamous Cell Carcinoma",
                    description: "Most common form of oral cancer. Appears as an unexplained sore that doesn't heal, a lump, or thick patch."
                },
                {
                    id: "herpes", title: "Herpes Simplex",
                    description: "Viral infections manifesting as painful blisters filled with fluid, typically on lips but can occur inside mouth."
                }
            ]
        },
        dashboard: {
            headerTag: "AI Assessment",
            title: "Oral Lesion Risk Assessment",
            desc: "Upload an intraoral photograph, select an AI model, and optionally provide patient clinical history for multimodal evaluation.",
            uploadTitle: "Upload Image",
            uploadSubtitle: "Intraoral photograph of lesion",
            dragDrop1: "Drag and drop here, or ",
            dragDrop2: "Browse files",
            uploadReq1: "Adequate lighting",
            uploadReq2: "Clear visual of the lesion",
            uploadReq3: "Minimum size 800 × 600 px",
            modelTitle: "Select AI Model",
            modelSubtitle: "Choose analysis architecture",
            modelYOLO: "Detection",
            modelMulti: "Multimodal",
            sympTitle: "Patient Symptoms",
            sympSub1: "Risk factors and observable signs",
            sympSub2: "Detailed risk factors, symptoms, and lesion specifics",
            resetForm: "Reset Form",
            errorForm: "Please upload an intraoral image before submitting for AI assessment.",
            errorSubmit: "Error during assessment: ",
            processing: "Processing Analysis...",
            startAi: "Run AI Assessment",
            modalTitle: "AI Assessment Result",
            modalModel: "Model",
            modalLesionDetected: "Detected Lesion",
            modalNoLesion: "No lesion detected",
            modalConf: "Confidence",
            modalImgContext: "AI Processed Image Result",
            modalImgTitle: "Processed Image / Bounding Boxes",
            modalImgDesc: "Result from model",
            modalBboxDetected: "Detected Bounding Boxes",
            modalClose: "Close Window"
        },
        upload: {
            changeImage: "Change Image",
            deleteImage: "Remove Image",
            size: "Size:",
            dim: "Dimensions:",
            validDim: "High Resolution",
            standardDim: "Standard Resolution",
            readyAi: "Ready for AI processing",
            typeError: "Please upload a valid image file (JPG, PNG or WEBP)",
            sizeError: "File size exceeds 20MB limit",
            sizeLimit: "JPG, PNG, WEBP · Max 20 MB"
        },
        models: {
            detectOutput: "Output: Localization & Bounding Box",
            classOutput: "Output: Disease Classification",
            historyTip: "Providing patient history improves assessment accuracy.",
            yolo7desc: "YOLOv7 architecture object detection model for localizing intraoral lesions.",
            yolo8desc: "YOLOv8 architecture object detection model for localizing intraoral lesions.",
            densedesc: "Fuses DenseNet image features with WangchanBERTa textual embeddings for holistic diagnosis."
        },
        symptoms: {
            yoloHeader: "Patient Symptoms (Select at least 1)",
            denseHistHeader: "Patient History",
            denseHistHint: "Select from the list or type more details (Default assumes 'No abnormal symptoms').",
            denseFeatHeader: "Lesion Features",
            denseLocHeader: "Lesion Locations",
            denseNoteHeader: "Additional Notes:",
            denseNoteHint: "e.g. Painful for 2 weeks, growing in size...",
            noSymptoms: "No abnormal symptoms",
            drinkAlcohol: "Drinks alcohol regularly",
            smoking: "Smokes Tobacco",
            chewBet: "Chews betel nut",
            eatSpicy: "Irritation when eating spicy food",
            wipeOff: "White patches can be wiped off",
            alwaysHurts: "Constant pain or irritation",
            whitePatch: "White Patch",
            whitePlaque: "White Plaque (wipeable)",
            whiteYellow: "White/Yellow Lesion",
            whiteRet: "White Reticular Lines",
            whiteRaised: "White Raised Lines",
            tongue: "Tongue",
            palate: "Palate",
            lip: "Lips",
            softTissue: "Soft Tissue",
            buccal: "Buccal Mucosa",
            gingiva: "Gingiva",
            floor: "Floor of Mouth",
            pharynx: "Pharynx"
        },
        login: {
            title: "Sign In",
            subtitle: "Welcome back to OralScan AI",
            email: "Email address",
            password: "Password",
            forgotPassword: "Forgot password?",
            signIn: "Sign In",
            noAccount: "Don't have an account?",
            signUp: "Sign up"
        }
    }
};

export function LanguageProvider({ children }) {
    const [lang, setLang] = useState('EN'); // Defaulting to EN as requested "add translation for english" indicates they want to see EN

    const toggleText = (keyPath) => {
        try {
            const keys = keyPath.split('.');
            let result = translations[lang];
            for (const k of keys) result = result[k];
            return result || keyPath;
        } catch {
            return keyPath;
        }
    };

    return (
        <LanguageContext.Provider value={{ lang, setLang, t: toggleText, translations }}>
            {children}
        </LanguageContext.Provider>
    );
}

export const useLanguage = () => useContext(LanguageContext);
