/**
 * Munshi Mock API Implementation
 * Implements every endpoint from docs/CONTEXT.md with realistic school data.
 */

import {
  AttendanceItem,
  AuditItem,
  Candidate,
  ConfirmRequest,
  ConfirmResponse,
  DemoMessageItem,
  Flag,
  LLMMode,
  LoginRequest,
  LoginResponse,
  MarksUploadResponse,
  MessageCreateRequest,
  NotificationDraft,
  ReviewFieldItem,
  ReviewObject,
  TeacherInfo,
} from './types';

// Default mock teachers
export const MOCK_TEACHERS: (TeacherInfo & {
  pin: string;
  role: 'teacher' | 'principal';
  classes: string[];
})[] = [
  { id: 'T01', name: 'Rajesh Sharma', subject: 'Mathematics', pin: '1234', role: 'teacher', classes: ['8A', '8B', '9A'] },
  { id: 'T02', name: 'Sunita Verma', subject: 'English', pin: '1234', role: 'teacher', classes: ['8A', '9B', '10A'] },
  { id: 'T03', name: 'Vikram Malhotra', subject: 'Science', pin: '1234', role: 'teacher', classes: ['7A', '8A', '10B'] },
  { id: 'T04', name: 'Meenakshi Sundaram', subject: 'Social Science', pin: '1234', role: 'teacher', classes: ['7B', '8A', '9A'] },
  { id: 'T05', name: 'Anita Gupta', subject: 'Hindi', pin: '1234', role: 'teacher', classes: ['6A', '6B', '8A'] },
  { id: 'T06', name: 'Pradeep Joshi', subject: 'Physics', pin: '1234', role: 'teacher', classes: ['11A', '12A'] },
  { id: 'T07', name: 'Neha Kapoor', subject: 'Chemistry', pin: '1234', role: 'teacher', classes: ['11B', '12B'] },
  { id: 'T08', name: 'Ramesh Iyer', subject: 'Economics', pin: '1234', role: 'teacher', classes: ['11A', '12B'] },
  { id: 'P01', name: 'Dr. Anand Swaminathan', subject: null, pin: '1234', role: 'principal', classes: [] },
];

export const DEMO_MESSAGES: DemoMessageItem[] = [
  {
    id: 'demo-1',
    title: 'Clean English Attendance',
    scenario: 'Standard clear attendance with two unique students in 8A (Status: Ready)',
    class_label: '8A',
    text: '8A: 2 absent - Sneha Reddy, Aditya Das. Covered Chapter 3 Linear Equations. Homework Ex 3.2.',
  },
  {
    id: 'demo-2',
    title: 'Hindi Devanagari Script',
    scenario: 'Devanagari message demonstrating transliteration and Hindi NLP',
    class_label: '8A',
    text: '8A में आज 2 अनुपस्थित - स्नेहा, आदित्य। पाठ 3 पढ़ाया। गृहकार्य अभ्यास 3.2।',
  },
  {
    id: 'demo-3',
    title: 'Hinglish Classroom Update',
    scenario: 'Colloquial Hinglish phrase structure with lesson diary',
    class_label: '8A',
    text: '8A: 2 absent the - Sneha, Aditya. Aaj chapter 3 Linear Equations padhaya. Homework Ex 3.2.',
  },
  {
    id: 'demo-4',
    title: 'Three-Kabirs Name Collision',
    scenario: 'Ambiguity detection: 3 students named Kabir in class 8A (Roll 801, 806, 811)',
    class_label: '8A',
    text: '8A: 1 absent - Kabir. Covered chapter 3 Linear Equations. Homework Ex 3.2.',
  },
  {
    id: 'demo-5',
    title: 'Stated Count Mismatch',
    scenario: 'Rule R4 verification: teacher stated 3 absent but only named 2 students',
    class_label: '8A',
    text: '8A: 3 absent - Sneha Reddy, Aditya Das. Covered chapter 3 Linear Equations. Homework Ex 3.2.',
  },
  {
    id: 'demo-6',
    title: 'Sunday Date Verification',
    scenario: 'Rule R6 block: teacher attempted to submit attendance for a Sunday (Status: Blocked)',
    class_label: '8A',
    text: '8A: 1 absent - Sneha Reddy on 2026-11-15. Covered chapter 3 Linear Equations.',
  },
];

// Candidates for Kabir in 8A
const KABIR_CANDIDATES: Candidate[] = [
  { student_id: 'MUN0041', name: 'Kabir Bansal', roll_no: 801, class_label: '8A' },
  { student_id: 'MUN0046', name: 'Kabir Mehta', roll_no: 806, class_label: '8A' },
  { student_id: 'MUN0051', name: 'Kabir Patel', roll_no: 811, class_label: '8A' },
];

const AYAAN_CANDIDATES: Candidate[] = [
  { student_id: 'MUN0042', name: 'Ayaan Verma', roll_no: 802, class_label: '8A' },
  { student_id: 'MUN0048', name: 'Ayaan Chauhan', roll_no: 808, class_label: '8A' },
  { student_id: 'MUN0060', name: 'Ayaan Kapoor', roll_no: 820, class_label: '8A' },
];

const RIYA_CANDIDATES: Candidate[] = [
  { student_id: 'MUN0027', name: 'Riya Patel', roll_no: 707, class_label: '7A' },
];

// In-memory store of reviews
const reviewStore = new Map<string, ReviewObject>();

// Configurable mock LLM mode selector
let currentMockLlmMode: LLMMode = 'gemini';

export function setMockLlmMode(mode: LLMMode) {
  currentMockLlmMode = mode;
}

export function getMockLlmMode(): LLMMode {
  return currentMockLlmMode;
}

// 1. Mock Login
export async function mockLogin(req: LoginRequest): Promise<LoginResponse> {
  const teacher = MOCK_TEACHERS.find((t) => t.id === req.teacher_id);
  if (!teacher || teacher.pin !== req.pin) {
    const error: any = new Error('Invalid teacher ID or PIN. Use PIN: 1234');
    error.status = 401;
    throw error;
  }

  const token = `mock-jwt-token.${btoa(JSON.stringify({ sub: teacher.id, role: teacher.role, name: teacher.name }))}.signature`;

  return {
    token,
    role: teacher.role,
    teacher: {
      id: teacher.id,
      name: teacher.name,
      subject: teacher.subject,
    },
  };
}

// Scenario 1: Ready Review Object
export function createReadyReview(
  msgId: string = 'msg-ready-001',
  llmMode: LLMMode = 'gemini'
): ReviewObject {
  const text = '8A: 2 absent - Sneha Reddy, Aditya Das. Covered Chapter 3 Linear Equations. Homework Ex 3.2.';
  return {
    message_id: msgId,
    text,
    status: 'ready',
    llm_mode: llmMode,
    fields: [
      {
        id: 'f-ready-class',
        type: 'class',
        label: 'Class Section',
        value: '8A',
        quote: '8A',
        start: 0,
        end: 2,
        status: 'OK',
        rule_id: 'R2',
        reason: 'Class 8A is valid and assigned to Rajesh Sharma.',
        candidates: [],
      },
      {
        id: 'f-ready-count',
        type: 'stated_count',
        label: 'Stated Absent Count',
        value: '2',
        quote: '2',
        start: 4,
        end: 5,
        status: 'OK',
        rule_id: 'R4',
        reason: 'Stated count (2) exactly matches the 2 extracted student names.',
        candidates: [],
      },
      {
        id: 'f-ready-sneha',
        type: 'absent_student',
        label: 'Absent Student',
        value: 'Sneha Reddy',
        quote: 'Sneha Reddy',
        roman: 'Sneha Reddy',
        start: 16,
        end: 27,
        status: 'OK',
        rule_id: 'R3',
        reason: 'Unique match found: Sneha Reddy (Roll 812, Class 8A).',
        candidates: [
          { student_id: 'MUN0052', name: 'Sneha Reddy', roll_no: 812, class_label: '8A' },
        ],
        resolved_student_id: 'MUN0052',
      },
      {
        id: 'f-ready-aditya',
        type: 'absent_student',
        label: 'Absent Student',
        value: 'Aditya Das',
        quote: 'Aditya Das',
        roman: 'Aditya Das',
        start: 29,
        end: 39,
        status: 'OK',
        rule_id: 'R3',
        reason: 'Unique match found: Aditya Das (Roll 813, Class 8A).',
        candidates: [
          { student_id: 'MUN0053', name: 'Aditya Das', roll_no: 813, class_label: '8A' },
        ],
        resolved_student_id: 'MUN0053',
      },
      {
        id: 'f-ready-topic',
        type: 'topic',
        label: 'Class Diary Topic',
        value: 'Covered Chapter 3 Linear Equations',
        quote: 'Covered Chapter 3 Linear Equations',
        start: 41,
        end: 76,
        status: 'OK',
        rule_id: 'R7',
        reason: 'Chapter 3 Linear Equations matches Mathematics syllabus.',
        candidates: [],
      },
      {
        id: 'f-ready-hw',
        type: 'homework',
        label: 'Homework Task',
        value: 'Homework Ex 3.2',
        quote: 'Homework Ex 3.2',
        start: 78,
        end: 93,
        status: 'OK',
        rule_id: 'R1',
        reason: 'Verified verbatim quote from teacher message.',
        candidates: [],
      },
    ],
    rule_results: [
      { rule_id: 'R1', status: 'OK', reason: 'All field quotes verified with exact substring offsets.' },
      { rule_id: 'R2', status: 'OK', reason: 'Class 8A is valid and assigned to teacher.' },
      { rule_id: 'R3', status: 'OK', reason: 'All students resolved uniquely.' },
      { rule_id: 'R4', status: 'OK', reason: 'Stated count (2) equals names count (2).' },
      { rule_id: 'R5', status: 'OK', reason: 'No duplicate students in list.' },
      { rule_id: 'R6', status: 'OK', reason: 'Active school day, not a holiday or weekend.' },
      { rule_id: 'R7', status: 'OK', reason: 'Mathematics Chapter 3 is in syllabus.' },
      { rule_id: 'R9', status: 'OK', reason: 'No existing submission for 8A today.' },
    ],
  };
}

// Scenario 2: The Three-Kabirs Choice (needs_review)
export function createKabirCollisionReview(
  msgId: string = 'msg-collision-001',
  llmMode: LLMMode = 'gemini'
): ReviewObject {
  const text = '8A: 3 absent — Kabir, Ayaan, Riya. Covered chapter 4. Homework Ex 4.2.';
  return {
    message_id: msgId,
    text,
    status: 'needs_review',
    llm_mode: llmMode,
    fields: [
      {
        id: 'f-class-1',
        type: 'class',
        label: 'Class Section',
        value: '8A',
        quote: '8A',
        start: 0,
        end: 2,
        status: 'OK',
        rule_id: 'R2',
        reason: 'Class 8A is assigned to teacher Rajesh Sharma.',
        candidates: [],
      },
      {
        id: 'f-count-1',
        type: 'stated_count',
        label: 'Stated Absent Count',
        value: '3',
        quote: '3',
        start: 4,
        end: 5,
        status: 'OK',
        rule_id: 'R4',
        reason: 'Stated count (3) equals the 3 extracted student names.',
        candidates: [],
      },
      {
        id: 'f-student-kabir',
        type: 'absent_student',
        label: 'Absent Student',
        value: 'Kabir',
        quote: 'Kabir',
        roman: 'Kabir',
        start: 16,
        end: 21,
        status: 'Review',
        rule_id: 'R3',
        reason: "Multiple students found with name 'Kabir' in 8A (3 candidates). Teacher choice required.",
        candidates: KABIR_CANDIDATES,
        resolved_student_id: null,
      },
      {
        id: 'f-student-ayaan',
        type: 'absent_student',
        label: 'Absent Student',
        value: 'Ayaan',
        quote: 'Ayaan',
        roman: 'Ayaan',
        start: 23,
        end: 28,
        status: 'OK',
        rule_id: 'R3',
        reason: 'Unique match found: Ayaan Verma (Roll 802, Class 8A).',
        candidates: [
          { student_id: 'MUN0042', name: 'Ayaan Verma', roll_no: 802, class_label: '8A' },
        ],
        resolved_student_id: 'MUN0042',
      },
      {
        id: 'f-student-riya',
        type: 'absent_student',
        label: 'Absent Student',
        value: 'Riya',
        quote: 'Riya',
        roman: 'Riya',
        start: 30,
        end: 34,
        status: 'OK',
        rule_id: 'R3',
        reason: 'Unique match found: Riya Patel (Roll 815, Class 8A).',
        candidates: [
          { student_id: 'MUN0055', name: 'Riya Patel', roll_no: 815, class_label: '8A' },
        ],
        resolved_student_id: 'MUN0055',
      },
      {
        id: 'f-topic-1',
        type: 'topic',
        label: 'Class Diary Topic',
        value: 'Covered chapter 4',
        quote: 'Covered chapter 4',
        start: 36,
        end: 53,
        status: 'OK',
        rule_id: 'R7',
        reason: 'Chapter 4 matches Grade 8 Mathematics syllabus.',
        candidates: [],
      },
      {
        id: 'f-hw-1',
        type: 'homework',
        label: 'Homework Task',
        value: 'Homework Ex 4.2',
        quote: 'Homework Ex 4.2',
        start: 55,
        end: 70,
        status: 'OK',
        rule_id: 'R1',
        reason: 'Extracted homework matches message quote verbatim.',
        candidates: [],
      },
    ],
    rule_results: [
      { rule_id: 'R1', status: 'OK', reason: 'All field quotes verified with exact substring offsets.' },
      { rule_id: 'R2', status: 'OK', reason: 'Class 8A is valid and assigned to the active teacher.' },
      { rule_id: 'R3', status: 'Review', reason: 'Ambiguous name matches detected: Kabir (3 candidates), Ayaan (3 candidates).' },
      { rule_id: 'R4', status: 'OK', reason: 'Stated count (3) equals the 3 student names extracted.' },
      { rule_id: 'R5', status: 'OK', reason: 'No duplicate students in absent list.' },
      { rule_id: 'R6', status: 'OK', reason: 'Today is an active school day.' },
      { rule_id: 'R7', status: 'OK', reason: 'Mathematics Chapter 4 matches syllabus.' },
      { rule_id: 'R9', status: 'OK', reason: 'No prior attendance or diary submission recorded for 8A today.' },
    ],
  };
}

// Scenario 3: Blocked Sunday Case
export function createSundayBlockedReview(
  msgId: string = 'msg-sunday-002',
  llmMode: LLMMode = 'fallback'
): ReviewObject {
  const text = '8A: 1 absent - Sneha Reddy on 2026-11-15. Covered chapter 3 Linear Equations.';
  return {
    message_id: msgId,
    text,
    status: 'blocked',
    llm_mode: llmMode,
    fields: [
      {
        id: 'f-class-sb',
        type: 'class',
        label: 'Class Section',
        value: '8A',
        quote: '8A',
        start: 0,
        end: 2,
        status: 'OK',
        rule_id: 'R2',
        reason: 'Class 8A is assigned to teacher.',
        candidates: [],
      },
      {
        id: 'f-count-sb',
        type: 'stated_count',
        label: 'Stated Absent Count',
        value: '1',
        quote: '1',
        start: 4,
        end: 5,
        status: 'OK',
        rule_id: 'R4',
        reason: 'Stated absent count (1) equals extracted name count.',
        candidates: [],
      },
      {
        id: 'f-student-sb',
        type: 'absent_student',
        label: 'Absent Student',
        value: 'Sneha Reddy',
        quote: 'Sneha Reddy',
        roman: 'Sneha Reddy',
        start: 15,
        end: 26,
        status: 'OK',
        rule_id: 'R3',
        reason: 'Unique match found: Sneha Reddy (Roll 812, Class 8A).',
        candidates: [{ student_id: 'MUN0052', name: 'Sneha Reddy', roll_no: 812, class_label: '8A' }],
        resolved_student_id: 'MUN0052',
      },
      {
        id: 'f-date-sb',
        type: 'date',
        label: 'Attendance Date',
        value: '2026-11-15',
        quote: '2026-11-15',
        start: 30,
        end: 40,
        status: 'Block',
        rule_id: 'R6',
        reason: 'Rule R6 Violation: 2026-11-15 is a Sunday. Attendance cannot be submitted for weekend.',
        candidates: [],
      },
      {
        id: 'f-topic-sb',
        type: 'topic',
        label: 'Class Diary Topic',
        value: 'Covered chapter 3 Linear Equations',
        quote: 'Covered chapter 3 Linear Equations',
        start: 42,
        end: 76,
        status: 'OK',
        rule_id: 'R7',
        reason: 'Chapter 3 Linear Equations matches Mathematics syllabus.',
        candidates: [],
      },
    ],
    rule_results: [
      { rule_id: 'R1', status: 'OK', reason: 'Span verification passed for all fields.' },
      { rule_id: 'R2', status: 'OK', reason: 'Class 8A is valid and assigned to the active teacher.' },
      { rule_id: 'R3', status: 'OK', reason: 'Student Sneha Reddy resolved unambiguously.' },
      { rule_id: 'R6', status: 'Block', reason: 'Rule R6: 2026-11-15 is a Sunday (school closed). Attendance cannot be submitted.' },
    ],
  };
}

// 2. Mock POST /api/messages
export async function mockCreateMessage(req: MessageCreateRequest): Promise<ReviewObject> {
  const msgId = `msg-${Date.now()}`;
  const text = req.text.trim();

  let review: ReviewObject;

  // Scenario 3: Sunday date block
  if (text.includes('2026-11-15') || text.toLowerCase().includes('sunday')) {
    review = createSundayBlockedReview(msgId, currentMockLlmMode);
    review.text = text;
  }
  // Scenario 2: The Three-Kabirs Choice
  else if (
    text.includes('Kabir, Ayaan, Riya') ||
    (text.includes('Kabir') && (text.includes('Riya') || text.includes('3 absent')))
  ) {
    review = createKabirCollisionReview(msgId, currentMockLlmMode);
    review.text = text;
  }
  // Scenario 1: Clean English Ready Attendance
  else if (text.includes('2 absent') && text.includes('Sneha Reddy, Aditya Das')) {
    review = createReadyReview(msgId, currentMockLlmMode);
    review.text = text;
  }
  // Demo 4: Three-Kabirs single
  else if (text.includes('Kabir') && text.includes('1 absent')) {
    review = createKabirCollisionReview(msgId, currentMockLlmMode);
    review.text = text;
  }
  // Fallback / other messages
  else {
    review = createReadyReview(msgId, currentMockLlmMode);
    review.text = text;
  }

  reviewStore.set(msgId, review);
  return review;
}

// 3. Mock GET /api/messages/{id}/review
export async function mockGetReview(messageId: string): Promise<ReviewObject> {
  const existing = reviewStore.get(messageId);
  if (existing) {
    return existing;
  }
  const defaultReview = createKabirCollisionReview(messageId, currentMockLlmMode);
  reviewStore.set(messageId, defaultReview);
  return defaultReview;
}

// Re-check after editing a value through the API
export async function mockRecheckField(
  messageId: string,
  fieldId: string,
  newValue: string
): Promise<ReviewObject> {
  const review = reviewStore.get(messageId) || createKabirCollisionReview(messageId);

  // Deep clone to modify
  const updatedReview: ReviewObject = JSON.parse(JSON.stringify(review));

  const targetField = updatedReview.fields.find((f) => f.id === fieldId);
  if (targetField) {
    targetField.value = newValue;

    // Check if user edited the Sunday date to a valid school day
    if (targetField.type === 'date') {
      const isSunday =
        newValue === '2026-11-15' ||
        new Date(newValue).getDay() === 0;

      if (!isSunday) {
        targetField.status = 'OK';
        targetField.reason = `Date ${newValue} verified: valid school day.`;
        // Update R6 rule result
        const r6 = updatedReview.rule_results.find((r) => r.rule_id === 'R6');
        if (r6) {
          r6.status = 'OK';
          r6.reason = `Date ${newValue} verified: valid school day.`;
        }
      } else {
        targetField.status = 'Block';
        targetField.reason = `Rule R6 Violation: ${newValue} is a Sunday. Submissions on weekends/holidays are blocked.`;
        const r6 = updatedReview.rule_results.find((r) => r.rule_id === 'R6');
        if (r6) {
          r6.status = 'Block';
          r6.reason = `Rule R6 Violation: ${newValue} is a Sunday.`;
        }
      }
    }

    // Check if user edited topic
    if (targetField.type === 'topic') {
      targetField.status = 'OK';
      targetField.reason = `Topic "${newValue}" matches syllabus.`;
    }

    // Check if user edited stated_count
    if (targetField.type === 'stated_count') {
      const studentCount = updatedReview.fields.filter(
        (f) => f.type === 'absent_student'
      ).length;
      if (parseInt(newValue, 10) === studentCount) {
        targetField.status = 'OK';
        targetField.reason = `Stated count (${newValue}) matches extracted names count (${studentCount}).`;
      }
    }
  }

  // Recompute overall review status
  const hasBlock = updatedReview.fields.some((f) => f.status === 'Block');
  const hasReview = updatedReview.fields.some(
    (f) =>
      f.status === 'Review' ||
      (f.type === 'absent_student' && f.candidates.length > 1 && !f.resolved_student_id)
  );

  if (hasBlock) {
    updatedReview.status = 'blocked';
  } else if (hasReview) {
    updatedReview.status = 'needs_review';
  } else {
    updatedReview.status = 'ready';
  }

  reviewStore.set(messageId, updatedReview);
  return updatedReview;
}

// 4. Mock POST /api/messages/{id}/confirm
export async function mockConfirmMessage(
  messageId: string,
  req: ConfirmRequest
): Promise<ConfirmResponse> {
  const review = reviewStore.get(messageId) || createKabirCollisionReview(messageId);

  // Return 409 if any field is Block
  if (review.status === 'blocked') {
    const error: any = new Error(
      'Cannot confirm: Message contains Block-level rule violations (e.g. Sunday date). Correct the date first.'
    );
    error.status = 409;
    throw error;
  }

  // Check unresolved candidates
  const ambiguousFields = review.fields.filter(
    (f) =>
      f.type === 'absent_student' &&
      f.candidates.length > 1 &&
      !req.resolutions[f.id] &&
      !f.resolved_student_id
  );

  if (ambiguousFields.length > 0) {
    const error: any = new Error(
      `Cannot confirm: ${ambiguousFields.length} ambiguous student(s) remain unresolved.`
    );
    error.status = 409;
    throw error;
  }

  const attendanceCount = review.fields.filter((f) => f.type === 'absent_student').length;

  // Bilingual parent & class notifications (English and Hindi)
  const drafts: NotificationDraft[] = [
    {
      id: 'draft-en-1',
      audience: 'Parents of Absent Students',
      language: 'English',
      text: 'Dear Parent, your ward was marked absent today in Class 8A. Please contact the school office if you have any questions or to submit a leave note.',
    },
    {
      id: 'draft-en-2',
      audience: 'Class 8A Parents & Students Broadcast',
      language: 'English',
      text: 'Class Diary 8A: Covered Chapter 4. Homework assigned: Ex 4.2. Please ensure homework is completed in notebook by tomorrow.',
    },
    {
      id: 'draft-hi-1',
      audience: 'अनुपस्थित विद्यार्थियों के अभिभावक',
      language: 'Hindi',
      text: 'आदरणीय अभिभावक, आपका बच्चा आज कक्षा 8A में अनुपस्थित रहा। किसी भी स्पष्टीकरण या अवकाश आवेदन के लिए कृपया विद्यालय से संपर्क करें।',
    },
    {
      id: 'draft-hi-2',
      audience: 'कक्षा 8A अभिभावक व छात्र प्रसारण',
      language: 'Hindi',
      text: 'कक्षा 8A दैनिकी: पाठ 4 पढ़ाया गया। गृहकार्य: अभ्यास 4.2। कृपया सुनिश्चित करें कि कार्य कल तक पूर्ण हो।',
    },
  ];

  return {
    records: {
      attendance: attendanceCount || 3,
      diary: 1,
      homework: 1,
    },
    drafts,
    audit_id: `aud-${Date.now().toString(36)}-atomic`,
  };
}

// 5. Mock GET /api/attendance?class=8A&date=YYYY-MM-DD
export async function mockGetAttendance(
  classLabel: string = '8A',
  dateVal: string = '2026-11-23'
): Promise<AttendanceItem[]> {
  const cleanClass = (classLabel || '8A').toUpperCase();

  // Class specific rosters
  const classRosters: Record<string, { id: string; name: string; roll: number; defaultAbsent?: boolean }[]> = {
    '8A': [
      { id: 'MUN0041', name: 'Kabir Bansal', roll: 801, defaultAbsent: true },
      { id: 'MUN0042', name: 'Ayaan Verma', roll: 802 },
      { id: 'MUN0046', name: 'Kabir Mehta', roll: 806 },
      { id: 'MUN0048', name: 'Ayaan Chauhan', roll: 808, defaultAbsent: true },
      { id: 'MUN0049', name: 'Kavya Joshi', roll: 809 },
      { id: 'MUN0051', name: 'Kabir Patel', roll: 811 },
      { id: 'MUN0052', name: 'Sneha Reddy', roll: 812, defaultAbsent: true },
      { id: 'MUN0053', name: 'Aditya Das', roll: 813 },
      { id: 'MUN0054', name: 'Nisha Saini', roll: 814 },
      { id: 'MUN0057', name: 'Om Reddy', roll: 817 },
      { id: 'MUN0058', name: 'Ananya Jain', roll: 818 },
      { id: 'MUN0059', name: 'Vivaan Bansal', roll: 819 },
      { id: 'MUN0060', name: 'Ayaan Kapoor', roll: 820 },
    ],
    '8B': [
      { id: 'MUN0061', name: 'Arjun Verma', roll: 821 },
      { id: 'MUN0062', name: 'Diya Sharma', roll: 822, defaultAbsent: true },
      { id: 'MUN0063', name: 'Ishaan Gupta', roll: 823 },
      { id: 'MUN0064', name: 'Meera Iyer', roll: 824 },
      { id: 'MUN0065', name: 'Pranav Kumar', roll: 825 },
      { id: 'MUN0066', name: 'Rohan Joshi', roll: 826, defaultAbsent: true },
      { id: 'MUN0067', name: 'Sanya Malhotra', roll: 827 },
      { id: 'MUN0068', name: 'Tanvi Nair', roll: 828 },
    ],
    '7A': [
      { id: 'MUN0021', name: 'Aarav Sharma', roll: 701 },
      { id: 'MUN0022', name: 'Ananya Sen', roll: 702 },
      { id: 'MUN0027', name: 'Riya Patel', roll: 707, defaultAbsent: true },
      { id: 'MUN0032', name: 'Rohan Mehta', roll: 712 },
      { id: 'MUN0033', name: 'Siddharth Rao', roll: 713 },
    ],
    '9A': [
      { id: 'MUN0071', name: 'Aryan Mishra', roll: 901 },
      { id: 'MUN0072', name: 'Bhavya Singh', roll: 902, defaultAbsent: true },
      { id: 'MUN0073', name: 'Chirag Sethi', roll: 903 },
      { id: 'MUN0074', name: 'Deepika Paul', roll: 904 },
      { id: 'MUN0075', name: 'Eshaan Roy', roll: 905 },
    ],
    '10A': [
      { id: 'MUN0081', name: 'Gaurav Bhatia', roll: 1001 },
      { id: 'MUN0082', name: 'Harshita Sen', roll: 1002 },
      { id: 'MUN0083', name: 'Jatin Anand', roll: 1003, defaultAbsent: true },
      { id: 'MUN0084', name: 'Kritika Roy', roll: 1004 },
    ],
    '11A': [
      { id: 'MUN0101', name: 'Aarush Pillai', roll: 1101 },
      { id: 'MUN0104', name: 'Dev Kaur', roll: 1104, defaultAbsent: true },
      { id: 'MUN0108', name: 'Simran Chauhan', roll: 1108 },
      { id: 'MUN0111', name: 'Krishna Gupta', roll: 1111 },
    ],
    '12A': [
      { id: 'MUN0121', name: 'Abhinav Saxena', roll: 1201 },
      { id: 'MUN0123', name: 'Pooja Kapoor', roll: 1203, defaultAbsent: true },
      { id: 'MUN0127', name: 'Reyansh Verma', roll: 1207 },
      { id: 'MUN0136', name: 'Kavya Das', roll: 1216 },
    ],
  };

  const selectedRoster = classRosters[cleanClass] || classRosters['8A'];

  return selectedRoster.map((s) => ({
    student_id: s.id,
    name: s.name,
    roll_no: s.roll,
    present: !s.defaultAbsent,
  }));
}

// 6. Mock GET /api/attendance/export?class=&date=&format=csv|xlsx
export async function mockExportAttendance(
  classLabel: string = '8A',
  dateVal: string = '2026-11-23',
  format: 'csv' | 'xlsx' = 'csv'
): Promise<Blob> {
  const roster = await mockGetAttendance(classLabel, dateVal);
  let content = 'Roll No,Student ID,Student Name,Class,Date,Status\n';
  roster.forEach((r) => {
    content += `${r.roll_no},${r.student_id},${r.name},${classLabel},${dateVal},${r.present ? 'Present' : 'Absent'}\n`;
  });
  const type =
    format === 'csv'
      ? 'text/csv'
      : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
  return new Blob([content], { type });
}

// 14 Realistic Flags matching ground truth & demo error test dataset
export const DEMO_MARKS_FLAGS: Flag[] = [
  {
    id: 'flag-01',
    upload_id: 'demo_error_test',
    record_id: 'REC0553',
    student_name: 'Krishna Gupta',
    class: '11A',
    subject: 'Business Studies',
    column: 'theory_marks',
    observed: '95.0',
    expected: 'Max: 80',
    rule: 'theory_above_max',
    severity: 'block',
    evidence: 'Theory marks 95.0 exceeds maximum allowed component theory marks of 80.',
    hint: 'Possible digit swap of 59',
  },
  {
    id: 'flag-02',
    upload_id: 'demo_error_test',
    record_id: 'REC0104',
    student_name: 'Ananya Jain',
    class: '7B',
    subject: 'Science',
    column: 'total_marks',
    observed: '108.0',
    expected: 'Range: 0-100 (Max 100)',
    rule: 'total_above_max',
    severity: 'block',
    evidence: 'Total marks 108.0 exceeds maximum allowed total score of 100.',
    hint: 'Verify score calculation against original answer sheet.',
  },
  {
    id: 'flag-03',
    upload_id: 'demo_error_test',
    record_id: 'REC0520',
    student_name: 'Dev Kaur',
    class: '11A',
    subject: 'Biology',
    column: 'theory_marks',
    observed: '-5.0',
    expected: 'Range: 0-80 (Min 0)',
    rule: 'negative_value',
    severity: 'block',
    evidence: 'Theory marks cannot be negative (-5.0). Rule R8 forbids scores < 0.',
    hint: 'Check mark sheet for intended positive score.',
  },
  {
    id: 'flag-04',
    upload_id: 'demo_error_test',
    record_id: 'REC0540',
    student_name: 'Simran Chauhan',
    class: '11A',
    subject: 'Mathematics',
    column: 'internal_marks',
    observed: '25.0',
    expected: 'Max: 20',
    rule: 'internal_above_max',
    severity: 'block',
    evidence: 'Internal marks 25.0 exceeds maximum internal component weightage of 20.',
    hint: 'Check practical notebook score ledger.',
  },
  {
    id: 'flag-05',
    upload_id: 'demo_error_test',
    record_id: 'REC0039',
    student_name: 'Nisha Kumar',
    class: '6B',
    subject: 'Science',
    column: 'theory_marks',
    observed: '(empty)',
    expected: 'Numeric (0-80)',
    rule: 'missing_value',
    severity: 'block',
    evidence: 'Theory marks column is empty or missing.',
    hint: 'Enter theory score or confirm Absent status.',
  },
  {
    id: 'flag-06',
    upload_id: 'demo_error_test',
    record_id: 'REC0678',
    student_name: 'Kavya Das',
    class: '12A',
    subject: 'Political Science',
    column: 'internal_marks',
    observed: '(empty)',
    expected: 'Numeric (0-20)',
    rule: 'missing_value',
    severity: 'block',
    evidence: 'Internal marks is missing or blank.',
    hint: 'Enter internal project evaluation score.',
  },
  {
    id: 'flag-07',
    upload_id: 'demo_error_test',
    record_id: 'REC0633',
    student_name: 'Reyansh Verma',
    class: '12A',
    subject: 'Chemistry',
    column: 'internal_marks',
    observed: 'twenty',
    expected: 'Numeric (0-20)',
    rule: 'non_numeric',
    severity: 'block',
    evidence: 'Internal marks contains word "twenty" instead of a numeric digit.',
    hint: 'Replace word text with digit 20.',
  },
  {
    id: 'flag-08',
    upload_id: 'demo_error_test',
    record_id: 'REC0612',
    student_name: 'Pooja Kapoor',
    class: '12A',
    subject: 'Physics',
    column: 'total_marks',
    observed: '(empty)',
    expected: '67.0 (55.0 + 12.0)',
    rule: 'missing_total',
    severity: 'block',
    evidence: 'Total marks field is blank; expected calculated sum of 67.0.',
    hint: 'Confirm total calculation.',
  },
  {
    id: 'flag-09',
    upload_id: 'demo_error_test',
    record_id: 'DUP001',
    student_name: 'Simran Joshi',
    class: '9B',
    subject: 'English',
    column: 'record_id',
    observed: 'DUP001',
    expected: 'Unique record',
    rule: 'duplicate_record',
    severity: 'block',
    evidence: 'Duplicate record found for Simran Joshi in 9B English (duplicate of REC0386).',
    hint: 'Remove duplicate record from submission.',
  },
  {
    id: 'flag-10',
    upload_id: 'demo_error_test',
    record_id: 'DUP002',
    student_name: 'Rohan Mehta',
    class: '7A',
    subject: 'Mathematics',
    column: 'record_id',
    observed: 'DUP002',
    expected: 'Unique record',
    rule: 'duplicate_record',
    severity: 'block',
    evidence: 'Duplicate record found for Rohan Mehta in 7A Mathematics (duplicate of REC0158).',
    hint: 'Remove duplicate record from submission.',
  },
  {
    id: 'flag-11',
    upload_id: 'demo_error_test',
    record_id: 'DUP003',
    student_name: 'Arjun Bansal',
    class: '7B',
    subject: 'Hindi',
    column: 'record_id',
    observed: 'DUP003',
    expected: 'Unique record',
    rule: 'duplicate_record',
    severity: 'block',
    evidence: 'Duplicate record found for Arjun Bansal in 7B Hindi (duplicate of REC0167).',
    hint: 'Remove duplicate record from submission.',
  },
  {
    id: 'flag-12',
    upload_id: 'demo_error_test',
    record_id: 'REC0345',
    student_name: 'Dev Kapoor',
    class: '9A',
    subject: 'Social Science',
    column: 'theory_marks',
    observed: 'Absent',
    expected: 'Numeric (0-80)',
    rule: 'non_numeric',
    severity: 'review',
    evidence: 'Theory marks contains string "Absent". Verification required to confirm zero score.',
    hint: 'Confirm student was officially absent from examination.',
  },
  {
    id: 'flag-13',
    upload_id: 'demo_error_test',
    record_id: 'REC0135',
    student_name: 'Riya Patel',
    class: '7A',
    subject: 'Social Science',
    column: 'total_marks',
    observed: '60.0',
    expected: '53.0 (38.0 + 15.0)',
    rule: 'total_mismatch',
    severity: 'review',
    evidence: 'Total marks (60.0) does not match Theory (38.0) + Internal (15.0) which equals 53.0.',
    hint: 'Check component sum.',
  },
  {
    id: 'flag-14',
    upload_id: 'demo_error_test',
    record_id: 'REC0228',
    student_name: 'Kabir Mehta',
    class: '8A',
    subject: 'Mathematics',
    column: 'theory_marks',
    observed: '46.0',
    expected: 'Median: 62.0 ± 8.0',
    rule: 'statistical_outlier',
    severity: 'review',
    evidence: 'Theory score 46.0 is 2.5 MAD below the class median (62.0) for 8A Mathematics.',
    hint: 'Verify score against student answer script.',
  },
];

// 7. Mock POST /api/marks/upload
export async function mockUploadMarks(formData: FormData): Promise<MarksUploadResponse> {
  return {
    upload_id: `upload-${Date.now().toString(36)}`,
    rows: 703,
    flags: DEMO_MARKS_FLAGS,
    unmapped_columns: [],
  };
}

// 7b. Mock GET /api/marks/demo
export async function mockGetMarksDemo(): Promise<MarksUploadResponse> {
  return {
    upload_id: 'demo_error_test',
    rows: 703,
    flags: DEMO_MARKS_FLAGS,
    unmapped_columns: [],
  };
}

// 8. Mock GET /api/marks/flags?upload_id=
export async function mockGetMarksFlags(uploadId?: string): Promise<Flag[]> {
  return DEMO_MARKS_FLAGS;
}

// 9. Mock GET /api/audit (principal only)
export async function mockGetAuditLogs(): Promise<AuditItem[]> {
  return [
    {
      id: 'aud-001',
      time: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
      teacher: 'Rajesh Sharma',
      message_id: 'msg-collision-001',
      action: 'CONFIRM_ATTENDANCE_DIARY',
      summary: 'Confirmed attendance for 8A: 3 absent (Kabir Bansal 801, Ayaan Verma 802, Riya Patel 707). Diary: Chapter 4. Homework: Ex 4.2.',
      text: '8A: 3 absent — Kabir, Ayaan, Riya. Covered chapter 4. Homework Ex 4.2.',
      fields: [
        {
          id: 'f-class-1',
          type: 'class',
          label: 'Class Section',
          value: '8A',
          quote: '8A',
          status: 'OK',
          candidates: [],
        },
        {
          id: 'f-count-1',
          type: 'stated_count',
          label: 'Stated Absent Count',
          value: '3',
          quote: '3',
          status: 'OK',
          candidates: [],
        },
        {
          id: 'f-student-kabir',
          type: 'absent_student',
          label: 'Absent Student',
          value: 'Kabir Bansal',
          quote: 'Kabir',
          status: 'OK',
          reason: 'Resolved by teacher: Kabir Bansal (Roll 801, Class 8A)',
          candidates: KABIR_CANDIDATES,
          resolved_student_id: 'MUN0041',
        },
        {
          id: 'f-student-ayaan',
          type: 'absent_student',
          label: 'Absent Student',
          value: 'Ayaan Verma',
          quote: 'Ayaan',
          status: 'OK',
          reason: 'Resolved by teacher: Ayaan Verma (Roll 802, Class 8A)',
          candidates: AYAAN_CANDIDATES,
          resolved_student_id: 'MUN0042',
        },
        {
          id: 'f-student-riya',
          type: 'absent_student',
          label: 'Absent Student',
          value: 'Riya Patel',
          quote: 'Riya',
          status: 'OK',
          reason: 'Resolved by teacher: Riya Patel (Roll 707, Class 7A)',
          candidates: RIYA_CANDIDATES,
          resolved_student_id: 'MUN0027',
        },
        {
          id: 'f-topic-1',
          type: 'topic',
          label: 'Class Diary Topic',
          value: 'Covered chapter 4',
          quote: 'Covered chapter 4',
          status: 'OK',
          reason: 'Chapter 4 matches syllabus',
          candidates: [],
        },
        {
          id: 'f-hw-1',
          type: 'homework',
          label: 'Homework Task',
          value: 'Homework Ex 4.2',
          quote: 'Homework Ex 4.2',
          status: 'OK',
          candidates: [],
        },
      ],
      rule_results: [
        { rule_id: 'R1', status: 'OK', reason: 'Quotes verified.' },
        { rule_id: 'R2', status: 'OK', reason: 'Class 8A assigned.' },
        { rule_id: 'R3', status: 'OK', reason: 'Ambiguities resolved by teacher.' },
        { rule_id: 'R4', status: 'OK', reason: 'Counts match.' },
      ],
    },
    {
      id: 'aud-002',
      time: new Date(Date.now() - 1000 * 60 * 55).toISOString(),
      teacher: 'Sunita Verma',
      message_id: 'msg-prev-002',
      action: 'CONFIRM_ATTENDANCE',
      summary: 'Confirmed attendance for 8A: 2 absent (Sneha Reddy 812, Aditya Das 813).',
      text: '8A: 2 absent - Sneha Reddy, Aditya Das. Covered Chapter 3 Linear Equations. Homework Ex 3.2.',
      fields: [
        { id: 'f-c-8a', type: 'class', label: 'Class Section', value: '8A', quote: '8A', status: 'OK', candidates: [] },
        { id: 'f-s-1', type: 'absent_student', label: 'Absent Student', value: 'Sneha Reddy', quote: 'Sneha Reddy', status: 'OK', candidates: [] },
        { id: 'f-s-2', type: 'absent_student', label: 'Absent Student', value: 'Aditya Das', quote: 'Aditya Das', status: 'OK', candidates: [] },
        { id: 'f-t-1', type: 'topic', label: 'Class Diary Topic', value: 'Covered Chapter 3 Linear Equations', quote: 'Covered Chapter 3 Linear Equations', status: 'OK', candidates: [] },
      ],
      rule_results: [
        { rule_id: 'R1', status: 'OK', reason: 'Quotes verified.' },
        { rule_id: 'R2', status: 'OK', reason: 'Class 8A assigned.' },
      ],
    },
    {
      id: 'aud-003',
      time: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
      teacher: 'Vikram Malhotra',
      message_id: 'msg-prev-003',
      action: 'CONFIRM_HOMEWORK',
      summary: 'Assigned Science Homework: Chapter 3 Worksheet to 8A.',
      text: '8A Science: assigned chapter 3 worksheet for tomorrow.',
      fields: [
        { id: 'f-c-sci', type: 'class', label: 'Class Section', value: '8A', quote: '8A', status: 'OK', candidates: [] },
        { id: 'f-hw-sci', type: 'homework', label: 'Homework Task', value: 'chapter 3 worksheet', quote: 'chapter 3 worksheet', status: 'OK', candidates: [] },
      ],
      rule_results: [
        { rule_id: 'R1', status: 'OK', reason: 'Quotes verified.' },
      ],
    },
  ];
}

// 10. Mock GET /api/demo/messages
export async function mockGetDemoMessages(): Promise<DemoMessageItem[]> {
  return DEMO_MESSAGES;
}
