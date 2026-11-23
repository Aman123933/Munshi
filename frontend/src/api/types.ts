/**
 * Munshi API Types
 * Copied directly and strictly from docs/CONTEXT.md API contract & backend schemas.
 */

export type Role = 'teacher' | 'principal';

export interface TeacherInfo {
  id: string;
  name: string;
  subject?: string | null;
}

export interface LoginRequest {
  teacher_id: string;
  pin: string;
}

export interface LoginResponse {
  token: string;
  role: Role | string;
  teacher: TeacherInfo;
}

export interface MessageCreateRequest {
  text: string;
  lang_hint?: string | null;
}

export interface Candidate {
  student_id: string;
  name: string;
  roll_no: number;
  class_label?: string;
}

export type FieldStatus = 'OK' | 'Review' | 'Block';

export type FieldType =
  | 'class'
  | 'date'
  | 'stated_count'
  | 'absent_student'
  | 'topic'
  | 'homework'
  | string;

export interface ReviewFieldItem {
  id: string;
  type: FieldType;
  label?: string | null;
  value: string;
  quote: string;
  roman?: string | null;
  start?: number | null;
  end?: number | null;
  status: FieldStatus | string;
  reason?: string | null;
  rule_id?: string | null;
  candidates: Candidate[];
  resolved_student_id?: string | null;
}

export interface RuleResult {
  rule_id: string;
  status: 'OK' | 'Review' | 'Block' | string;
  reason?: string | null;
  field_id?: string | null;
}

export type ReviewStatus = 'ready' | 'needs_review' | 'blocked';
export type LLMMode = 'gemini' | 'fallback' | 'cached';

export interface ReviewObject {
  message_id: string;
  text: string;
  status: ReviewStatus;
  llm_mode: LLMMode;
  fields: ReviewFieldItem[];
  rule_results: RuleResult[];
}

export interface ConfirmRequest {
  resolutions: Record<string, string>; // field_id -> student_id
  edits: Record<string, any>;          // field_id -> value
}

export interface NotificationDraft {
  id: string;
  audience: string;
  language: 'English' | 'Hindi' | string;
  text: string;
}

export interface ConfirmRecords {
  attendance?: number;
  diary?: number;
  homework?: number;
  [key: string]: number | undefined;
}

export interface ConfirmResponse {
  records: ConfirmRecords;
  drafts: NotificationDraft[];
  audit_id: string;
}

export interface AttendanceItem {
  student_id: string;
  name: string;
  roll_no: number;
  present: boolean;
}

export type FlagSeverity = 'review' | 'block';

export interface Flag {
  id?: string;
  upload_id?: string;
  record_id?: string | null;
  student_name?: string | null;
  class?: string | null;
  subject?: string | null;
  column?: string | null;
  observed?: string | null;
  expected?: string | null;
  rule?: string | null;
  severity: FlagSeverity;
  evidence?: string | null;
  hint?: string | null;
}

export interface MarksUploadResponse {
  upload_id: string;
  rows: number;
  flags: Flag[];
  unmapped_columns?: string[];
}

export interface AuditItem {
  id: string;
  time: string;
  teacher: string;
  message_id: string;
  action: string;
  summary: string;
  text?: string;
  fields?: ReviewFieldItem[];
  rule_results?: RuleResult[];
}

export interface DemoMessageItem {
  id: string;
  title: string;
  scenario?: string;
  class_label?: string;
  text: string;
}

export interface RecheckRequest {
  message_id: string;
  field_id: string;
  value: string;
}
