/**
 * api.ts — thin wrapper around fetch() for the Basma+ backend.
 *
 * Strategy:
 *  - Access token is stored in memory (not localStorage) to reduce XSS risk.
 *  - The refresh token lives in an HttpOnly cookie — the browser sends it
 *    automatically to POST /auth/refresh.
 *  - On a 401 the client tries one refresh cycle then retries the original
 *    request.  If the refresh also fails, the user is signed out.
 */

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

// ──────────────────────────────────────────────────────────────────
// In-memory token store
// ──────────────────────────────────────────────────────────────────

let _accessToken: string | null = null;

export const tokenStore = {
  get: () => _accessToken,
  set: (t: string | null) => {
    _accessToken = t;
  },
  clear: () => {
    _accessToken = null;
  },
};

// ──────────────────────────────────────────────────────────────────
// Listeners — components subscribe to auth state changes
// ──────────────────────────────────────────────────────────────────

type AuthListener = (authenticated: boolean) => void;
const _listeners = new Set<AuthListener>();

export function onAuthChange(fn: AuthListener) {
  _listeners.add(fn);
  return () => _listeners.delete(fn);
}

function _notifyAuth(authenticated: boolean) {
  _listeners.forEach((fn) => fn(authenticated));
}

// ──────────────────────────────────────────────────────────────────
// Core fetch wrapper
// ──────────────────────────────────────────────────────────────────

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
  /** Skip the 401 → refresh retry (prevents infinite loops). */
  _retry?: boolean;
};

export async function apiFetch<T = unknown>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { body, _retry, ...rest } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(rest.headers as Record<string, string> | undefined),
  };

  if (_accessToken) {
    headers["Authorization"] = `Bearer ${_accessToken}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...rest,
    credentials: "include", // sends HttpOnly refresh_token cookie
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  // ── 401 → try to refresh, then retry once ────────────────────────
  if (response.status === 401 && !_retry) {
    const refreshed = await _refreshAccessToken();
    if (refreshed) {
      return apiFetch<T>(path, { ...options, _retry: true });
    }
    // Refresh failed → sign out
    tokenStore.clear();
    _notifyAuth(false);
    throw new ApiError(401, "Session expired — please sign in again.");
  }

  if (!response.ok) {
    let detail: string;
    try {
      const err = await response.json();
      detail = err?.detail ?? response.statusText;
    } catch {
      detail = response.statusText;
    }
    throw new ApiError(response.status, detail);
  }

  // 204 No Content
  if (response.status === 204) return undefined as T;

  return response.json() as Promise<T>;
}

// ──────────────────────────────────────────────────────────────────
// Refresh helper
// ──────────────────────────────────────────────────────────────────

async function _refreshAccessToken(): Promise<boolean> {
  try {
    const data = await apiFetch<{ access_token: string }>("/auth/refresh", {
      method: "POST",
      _retry: true, // prevent recursion
    });
    tokenStore.set(data.access_token);
    return true;
  } catch {
    return false;
  }
}

// ──────────────────────────────────────────────────────────────────
// Custom error class
// ──────────────────────────────────────────────────────────────────

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ──────────────────────────────────────────────────────────────────
// Auth helpers
// ──────────────────────────────────────────────────────────────────

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

/** POST /auth/login — uses form-encoding required by OAuth2PasswordRequestForm */
export async function apiLogin(payload: LoginPayload) {
  const body = new URLSearchParams({
    username: payload.email,
    password: payload.password,
  });

  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });

  if (!response.ok) {
    let detail: string;
    try {
      const err = await response.json();
      detail = err?.detail ?? response.statusText;
    } catch {
      detail = response.statusText;
    }
    throw new ApiError(response.status, detail);
  }

  const data: { access_token: string; token_type: string } = await response.json();
  tokenStore.set(data.access_token);
  _notifyAuth(true);
  return data;
}

export async function apiRegister(payload: RegisterPayload) {
  const data = await apiFetch<{ id: string; email: string }>("/auth/register", {
    method: "POST",
    body: payload,
  });
  return data;
}

export async function apiLogout() {
  await apiFetch("/auth/logout", { method: "POST" }).catch(() => {});
  tokenStore.clear();
  _notifyAuth(false);
}

// ──────────────────────────────────────────────────────────────────
// Profile helpers
// ──────────────────────────────────────────────────────────────────

export interface ProfileData {
  id: string;
  user_id: string;
  first_name: string | null;
  last_name: string | null;
  age: number | null;
  gender: string | null;
  city: string | null;
  major: string | null;
  target_screen_time: number | null;
  target_sleep_time: number | null;
  points: number;
  interests: string[];
  language: string;
  theme: string;
  notifications_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface FullUserData {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
  profile: ProfileData | null;
}

export async function apiGetProfile(): Promise<FullUserData> {
  return apiFetch<FullUserData>("/profile/");
}

export interface OnboardingPayload {
  personal: {
    age?: number;
    city?: string;
    major?: string;
  };
  digital: {
    screen_time_hours: number;
    social_media_hours: number;
    sleep_hours: number;
  };
  mental: {
    mood_score: number;
    stress_score: number;
    mood_state?: string;
  };
  plan: {
    goals: string[];
    interests: string[];
  };
}

export async function apiSubmitOnboarding(payload: OnboardingPayload): Promise<ProfileData> {
  return apiFetch<ProfileData>("/profile/onboarding", {
    method: "POST",
    body: payload,
  });
}

export interface ProfileUpdatePayload {
  first_name?: string;
  last_name?: string;
  age?: number;
  gender?: string;
  city?: string;
  major?: string;
  interests?: string[];
}

export async function apiUpdateProfile(payload: ProfileUpdatePayload): Promise<ProfileData> {
  return apiFetch<ProfileData>("/profile/", {
    method: "PUT",
    body: payload,
  });
}

export interface SettingsPayload {
  language?: string;
  theme?: string;
  notifications_enabled?: boolean;
}

export async function apiUpdateSettings(payload: SettingsPayload): Promise<ProfileData> {
  return apiFetch<ProfileData>("/profile/settings", {
    method: "PUT",
    body: payload,
  });
}

// ──────────────────────────────────────────────────────────────────
// Productivity helpers
// ──────────────────────────────────────────────────────────────────

export interface GoalData {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  category: string | null;
  status: "NOT_STARTED" | "IN_PROGRESS" | "COMPLETED" | "ABANDONED";
  target_date: string | null;
  progress_percent: number;
  created_at: string;
  updated_at: string;
}

export async function apiGetGoals(): Promise<GoalData[]> {
  return apiFetch<GoalData[]>("/productivity/goals");
}

export async function apiCreateGoal(payload: Partial<GoalData>): Promise<GoalData> {
  return apiFetch<GoalData>("/productivity/goals", {
    method: "POST",
    body: payload,
  });
}

export async function apiUpdateGoal(id: string, payload: Partial<GoalData>): Promise<GoalData> {
  return apiFetch<GoalData>(`/productivity/goals/${id}`, {
    method: "PUT",
    body: payload,
  });
}

export async function apiDeleteGoal(id: string): Promise<void> {
  await apiFetch(`/productivity/goals/${id}`, { method: "DELETE" });
}

export interface TaskData {
  id: string;
  user_id: string;
  goal_id: string | null;
  title: string;
  is_completed: boolean;
  status: "PENDING" | "IN_PROGRESS" | "DONE";
  due_date: string | null;
  pomodoro_sessions: number;
  created_at: string;
  updated_at: string;
}

export async function apiGetTasks(params?: { goal_id?: string; due_date?: string }): Promise<TaskData[]> {
  const qs = new URLSearchParams();
  if (params?.goal_id) qs.append("goal_id", params.goal_id);
  if (params?.due_date) qs.append("due_date", params.due_date);
  const query = qs.toString();
  return apiFetch<TaskData[]>(`/productivity/tasks${query ? "?" + query : ""}`);
}

export async function apiCreateTask(payload: Partial<TaskData>): Promise<TaskData> {
  return apiFetch<TaskData>("/productivity/tasks", {
    method: "POST",
    body: payload,
  });
}

export async function apiUpdateTask(id: string, payload: Partial<TaskData>): Promise<TaskData> {
  return apiFetch<TaskData>(`/productivity/tasks/${id}`, {
    method: "PUT",
    body: payload,
  });
}

export async function apiDeleteTask(id: string): Promise<void> {
  await apiFetch(`/productivity/tasks/${id}`, { method: "DELETE" });
}

export interface PlannerData {
  id: string;
  user_id: string;
  title: string;
  plan_date: string;
  start_time: string | null;
  end_time: string | null;
  is_completed: boolean;
  created_at: string;
}

export async function apiGetPlanner(plan_date?: string): Promise<PlannerData[]> {
  const query = plan_date ? `?plan_date=${plan_date}` : "";
  return apiFetch<PlannerData[]>(`/productivity/planner${query}`);
}

export async function apiCreatePlannerItem(payload: Partial<PlannerData>): Promise<PlannerData> {
  return apiFetch<PlannerData>("/productivity/planner", {
    method: "POST",
    body: payload,
  });
}

export async function apiUpdatePlannerItem(id: string, payload: Partial<PlannerData>): Promise<PlannerData> {
  return apiFetch<PlannerData>(`/productivity/planner/${id}`, {
    method: "PUT",
    body: payload,
  });
}

export async function apiDeletePlannerItem(id: string): Promise<void> {
  await apiFetch(`/productivity/planner/${id}`, { method: "DELETE" });
}
