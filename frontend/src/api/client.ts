/**
 * Munshi API Client
 * Typed fetch wrapper with JWT header, error handling, and VITE_API_MODE=mock|live switch.
 */

import {
  AttendanceItem,
  AuditItem,
  ConfirmRequest,
  ConfirmResponse,
  DemoMessageItem,
  Flag,
  LoginRequest,
  LoginResponse,
  MarksUploadResponse,
  MessageCreateRequest,
  ReviewObject,
} from './types';
import * as mockApi from './mock';

export type ApiMode = 'mock' | 'live';

// Default mode from Vite env or default to 'live'
let activeApiMode: ApiMode =
  ((import.meta.env.VITE_API_MODE as string) || 'live').toLowerCase() === 'mock'
    ? 'mock'
    : 'live';

const TOKEN_STORAGE_KEY = 'munshi_auth_token';
const TEACHER_STORAGE_KEY = 'munshi_active_teacher';

export class ApiError extends Error {
  status: number;
  data?: any;

  constructor(message: string, status: number = 500, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

export function getApiMode(): ApiMode {
  return activeApiMode;
}

export function setApiMode(mode: ApiMode) {
  activeApiMode = mode;
}

export function getStoredToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
  } catch {
    return null;
  }
}

export function setStoredToken(token: string | null) {
  try {
    if (token) {
      localStorage.setItem(TOKEN_STORAGE_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
    }
  } catch {
    // Ignore storage errors in private/restricted environments
  }
}

export function getStoredTeacher(): any | null {
  try {
    const raw = localStorage.getItem(TEACHER_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setStoredTeacher(teacher: any | null) {
  try {
    if (teacher) {
      localStorage.setItem(TEACHER_STORAGE_KEY, JSON.stringify(teacher));
    } else {
      localStorage.removeItem(TEACHER_STORAGE_KEY);
    }
  } catch {
    // Ignore storage errors
  }
}

/**
 * Low-level typed fetch wrapper for live mode with JWT headers and error handling
 */
async function liveRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getStoredToken();
  const headers = new Headers(options.headers || {});

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(endpoint, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    let errorBody: any = null;
    try {
      errorBody = await response.json();
      if (errorBody && errorBody.detail) {
        errorDetail = typeof errorBody.detail === 'string'
          ? errorBody.detail
          : JSON.stringify(errorBody.detail);
      }
    } catch {
      // Body was not JSON
    }
    throw new ApiError(errorDetail, response.status, errorBody);
  }

  // Handle binary/blob responses (e.g. export)
  const contentType = response.headers.get('content-type') || '';
  if (
    contentType.includes('text/csv') ||
    contentType.includes('spreadsheetml') ||
    contentType.includes('application/octet-stream')
  ) {
    return (await response.blob()) as unknown as T;
  }

  return response.json();
}

/**
 * Simulated latency helper for mock requests to give realistic UI loading skeletons
 */
async function simulateLatency<T>(fn: () => Promise<T>, delayMs: number = 250): Promise<T> {
  await new Promise((resolve) => setTimeout(resolve, delayMs));
  return fn();
}

// Public High-Level API Methods
export const apiClient = {
  // 1. Login
  async login(req: LoginRequest): Promise<LoginResponse> {
    if (activeApiMode === 'mock') {
      const res = await simulateLatency(() => mockApi.mockLogin(req), 150);
      setStoredToken(res.token);
      setStoredTeacher({ ...res.teacher, role: res.role });
      return res;
    }
    const res = await liveRequest<LoginResponse>('/api/login', {
      method: 'POST',
      body: JSON.stringify(req),
    });
    setStoredToken(res.token);
    setStoredTeacher({ ...res.teacher, role: res.role });
    return res;
  },

  // 2. Create message
  async createMessage(req: MessageCreateRequest): Promise<ReviewObject> {
    if (activeApiMode === 'mock') {
      return simulateLatency(() => mockApi.mockCreateMessage(req), 350);
    }
    return liveRequest<ReviewObject>('/api/messages', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  },

  // 3. Get review
  async getReview(messageId: string): Promise<ReviewObject> {
    if (activeApiMode === 'mock') {
      return simulateLatency(() => mockApi.mockGetReview(messageId), 150);
    }
    return liveRequest<ReviewObject>(`/api/messages/${messageId}/review`);
  },

  // 4. Confirm message
  async confirmMessage(messageId: string, req: ConfirmRequest): Promise<ConfirmResponse> {
    if (activeApiMode === 'mock') {
      return simulateLatency(() => mockApi.mockConfirmMessage(messageId, req), 300);
    }
    return liveRequest<ConfirmResponse>(`/api/messages/${messageId}/confirm`, {
      method: 'POST',
      body: JSON.stringify(req),
    });
  },

  // 5. Get attendance
  async getAttendance(classLabel: string, dateVal: string): Promise<AttendanceItem[]> {
    if (activeApiMode === 'mock') {
      return simulateLatency(() => mockApi.mockGetAttendance(classLabel, dateVal), 200);
    }
    return liveRequest<AttendanceItem[]>(
      `/api/attendance?class=${encodeURIComponent(classLabel)}&date=${encodeURIComponent(dateVal)}`
    );
  },

  // 6. Export attendance
  async exportAttendance(
    classLabel: string,
    dateVal: string,
    format: 'csv' | 'xlsx' = 'csv'
  ): Promise<Blob> {
    if (activeApiMode === 'mock') {
      return simulateLatency(() => mockApi.mockExportAttendance(classLabel, dateVal, format), 200);
    }
    return liveRequest<Blob>(
      `/api/attendance/export?class=${encodeURIComponent(classLabel)}&date=${encodeURIComponent(dateVal)}&format=${format}`
    );
  },

  // 7. Upload marks
  async uploadMarks(formData: FormData): Promise<MarksUploadResponse> {
    if (activeApiMode === 'mock') {
      return simulateLatency(() => mockApi.mockUploadMarks(formData), 400);
    }
    return liveRequest<MarksUploadResponse>('/api/marks/upload', {
      method: 'POST',
      body: formData,
    });
  },

  // 8. Get marks flags
  async getMarksFlags(uploadId?: string): Promise<Flag[]> {
    if (activeApiMode === 'mock') {
      return simulateLatency(() => mockApi.mockGetMarksFlags(uploadId), 200);
    }
    const query = uploadId ? `?upload_id=${encodeURIComponent(uploadId)}` : '';
    return liveRequest<Flag[]>(`/api/marks/flags${query}`);
  },

  // 8b. Run demo marks check (GET /api/marks/demo)
  async getMarksDemo(): Promise<MarksUploadResponse> {
    if (activeApiMode === 'mock') {
      return simulateLatency(() => mockApi.mockGetMarksDemo(), 300);
    }
    return liveRequest<MarksUploadResponse>('/api/marks/demo');
  },

  // 9. Get audit logs
  async getAuditLogs(): Promise<AuditItem[]> {
    if (activeApiMode === 'mock') {
      return simulateLatency(() => mockApi.mockGetAuditLogs(), 200);
    }
    return liveRequest<AuditItem[]>('/api/audit');
  },

  // 10. Get demo messages
  async getDemoMessages(): Promise<DemoMessageItem[]> {
    if (activeApiMode === 'mock') {
      return simulateLatency(() => mockApi.mockGetDemoMessages(), 100);
    }
    return liveRequest<DemoMessageItem[]>('/api/demo/messages');
  },

  // 11. Recheck field value through API
  async recheckField(
    messageId: string,
    fieldId: string,
    newValue: string
  ): Promise<ReviewObject> {
    if (activeApiMode === 'mock') {
      return simulateLatency(() => mockApi.mockRecheckField(messageId, fieldId, newValue), 250);
    }
    return liveRequest<ReviewObject>(`/api/messages/${messageId}/recheck`, {
      method: 'POST',
      body: JSON.stringify({ field_id: fieldId, value: newValue }),
    });
  },
};
