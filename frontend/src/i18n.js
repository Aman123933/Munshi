/**
 * UI Label Translations for English and Hindi.
 * Technical terms (API, LLM, Gemini, JWT, CSV, XLSX, Rules R1-R9) are kept strictly in English.
 */

export const translations = {
  en: {
    // Navigation & Tabs
    update: 'Update',
    records: 'Records',
    marks: 'Marks',
    audit: 'Audit',
    principalOnly: 'Principal Only',

    // Core Principle
    principle: 'AI proposes. Rules verify. The teacher confirms.',

    // First-Run 3-Step Explainer
    firstRunTitle: 'How Munshi Works in 3 Steps',
    step1Title: '1. Send',
    step1Desc: 'Speak or type one short classroom update in English, Hindi, or Hinglish.',
    step2Title: '2. Review',
    step2Desc: 'Gemini proposes structured fields. Rules R1 to R9 verify quotes, rosters, and syllabi.',
    step3Title: '3. Confirm',
    step3Desc: 'Resolve any name ambiguities and confirm. Records commit in one atomic transaction.',

    // Composer
    send: 'Send Message',
    processing: 'Processing...',
    dictateVoice: 'Dictate Voice',
    listening: 'Listening...',
    clear: 'Clear',
    languageHint: 'Language Hint',
    composerPlaceholder: "Type or speak a classroom update... e.g. '8A: 3 absent — Kabir, Ayaan, Riya. Covered chapter 4. Homework Ex 4.2.'",

    // Review Screen
    confirm: 'Confirm and create records',
    editMessage: 'Edit message in composer',
    readyToConfirm: 'Ready to Confirm',
    needsReview: 'Needs Teacher Review',
    submissionBlocked: 'Submission Blocked',
    itemsLeft: 'items left',
    itemLeft: 'item left',
    zeroItemsLeft: '0 items left',

    // Records Tab
    exportCsv: 'Export CSV',
    exportXlsx: 'Export XLSX',
    class: 'Class',
    date: 'Date',
    present: 'Present',
    absent: 'Absent',
    totalRoster: 'Total Roster',
    turnout: 'Turnout',

    // Marks Tab
    uploadMarks: 'Upload Marks CSV',
    useDemoFile: 'Use the demo file',
    rowsChecked: 'Rows Checked',
    totalFlags: 'Total Flags',
    blocks: 'Blocks',
    reviews: 'Reviews',
    checkedByTeacher: 'Checked by teacher',
    markAsChecked: 'Mark as checked',

    // Footer
    footerNote: 'Prototype with synthetic data. No real student data.',
    builtWith: 'Munshi © 2026. Built with FastAPI, React, Vite & Tailwind CSS.',
  },
  hi: {
    // Navigation & Tabs
    update: 'अपडेट',
    records: 'अभिलेख',
    marks: 'अंक',
    audit: 'ऑडिट',
    principalOnly: 'केवल प्रधानाचार्य',

    // Core Principle
    principle: 'AI प्रस्तावित करता है। नियम सत्यापन करते हैं। शिक्षक पुष्टि करते हैं।',

    // First-Run 3-Step Explainer
    firstRunTitle: 'मुंशी 3 चरणों में कैसे कार्य करता है',
    step1Title: '1. भेजें (Send)',
    step1Desc: 'अंग्रेजी, हिंदी या हिंग्लिश में कक्षा का एक संक्षिप्त संदेश बोलें या टाइप करें।',
    step2Title: '2. समीक्षा (Review)',
    step2Desc: 'Gemini संरचना प्रस्तुत करता है। नियम R1 से R9 उद्धरण, उपस्थिति व पाठ्यक्रम सत्यापित करते हैं।',
    step3Title: '3. पुष्टि (Confirm)',
    step3Desc: 'नाम संबंधी विकल्पों का चयन करें और पुष्टि करें। सभी रिकॉर्ड्स एक ही लेन-देन में दर्ज होते हैं।',

    // Composer
    send: 'संदेश भेजें',
    processing: 'प्रक्रिया जारी...',
    dictateVoice: 'बोलकर लिखें',
    listening: 'सुन रहे हैं...',
    clear: 'साफ़ करें',
    languageHint: 'भाषा संकेत',
    composerPlaceholder: "कक्षा अपडेट टाइप करें या बोलें... उदा. '8A: 3 absent — Kabir, Ayaan, Riya. Covered chapter 4. Homework Ex 4.2.'",

    // Review Screen
    confirm: 'पुष्टि करें और रिकॉर्ड बनाएं',
    editMessage: 'कंपोज़र में संदेश संपादित करें',
    readyToConfirm: 'पुष्टि के लिए तैयार',
    needsReview: 'समीक्षा आवश्यक',
    submissionBlocked: 'सबमिशन अवरुद्ध',
    itemsLeft: 'शेष',
    itemLeft: 'शेष',
    zeroItemsLeft: '0 शेष',

    // Records Tab
    exportCsv: 'CSV निर्यात',
    exportXlsx: 'XLSX निर्यात',
    class: 'कक्षा',
    date: 'दिनांक',
    present: 'उपस्थित',
    absent: 'अनुपस्थित',
    totalRoster: 'कुल छात्र',
    turnout: 'उपस्थिति दर',

    // Marks Tab
    uploadMarks: 'अंक CSV अपलोड करें',
    useDemoFile: 'डेमो फ़ाइल का उपयोग करें',
    rowsChecked: 'जांची गई पंक्तियां',
    totalFlags: 'कुल फ़्लैग्स',
    blocks: 'अवरोध (Blocks)',
    reviews: 'समीक्षाएं (Reviews)',
    checkedByTeacher: 'शिक्षक द्वारा सत्यापित',
    markAsChecked: 'जांच चिह्नित करें',

    // Footer
    footerNote: 'सिंथेटिक डेटा के साथ प्रोटोटाइप। वास्तविक छात्र डेटा नहीं।',
    builtWith: 'Munshi © 2026. FastAPI, React, Vite और Tailwind CSS द्वारा निर्मित।',
  },
};

export function getTranslation(lang, key) {
  const currentLang = lang === 'hi' ? 'hi' : 'en';
  return translations[currentLang]?.[key] || translations.en[key] || key;
}
