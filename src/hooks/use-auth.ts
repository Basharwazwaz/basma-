/**
 * use-auth.ts — React hook for authentication state + mutations.
 *
 * State model:
 *  - `user`         — FullUserData from GET /profile (null = unauthenticated)
 *  - `isLoading`    — true while the initial profile fetch is in flight
 *  - `login()`      — mutation: POST /auth/login → stores token → refetches profile
 *  - `register()`   — mutation: POST /auth/register → navigates to /auth/login
 *  - `logout()`     — clears token + query cache + navigates to /
 */

import { useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import {
  apiLogin,
  apiRegister,
  apiLogout,
  apiGetProfile,
  tokenStore,
  type LoginPayload,
  type RegisterPayload,
  type FullUserData,
} from "@/lib/api";

export const PROFILE_QUERY_KEY = ["auth", "profile"] as const;

// ──────────────────────────────────────────────────────────────────
// Main hook
// ──────────────────────────────────────────────────────────────────

export function useAuth() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  // Fetch the authenticated user's full profile.
  // Returns null/undefined when unauthenticated (401 → treated as null).
  const {
    data: user,
    isLoading,
    isError,
  } = useQuery<FullUserData | null>({
    queryKey: PROFILE_QUERY_KEY,
    queryFn: async () => {
      if (!tokenStore.get()) return null;
      try {
        return await apiGetProfile();
      } catch {
        return null;
      }
    },
    staleTime: 1000 * 60 * 5, // 5 min
    retry: false,
  });

  // Refetch profile when user returns to the tab — detects JWT expiry.
  useEffect(() => {
    const onVisible = () => {
      if (document.visibilityState === "visible" && tokenStore.get()) {
        queryClient.invalidateQueries({ queryKey: PROFILE_QUERY_KEY });
      }
    };
    document.addEventListener("visibilitychange", onVisible);
    return () => document.removeEventListener("visibilitychange", onVisible);
  }, [queryClient]);

  // ── Login ─────────────────────────────────────────────────────
  const loginMutation = useMutation({
    mutationFn: (payload: LoginPayload) => apiLogin(payload),
    onSuccess: async () => {
      // Refetch the profile so `user` becomes populated
      const profile = await queryClient.fetchQuery<FullUserData | null>({
        queryKey: PROFILE_QUERY_KEY,
        queryFn: async () => {
          try {
            return await apiGetProfile();
          } catch {
            return null;
          }
        },
        staleTime: 0,
      });

      // Check if onboarding is needed (no age = not completed)
      if (profile?.profile && !profile.profile.age) {
        navigate({ to: "/onboarding" });
      } else {
        navigate({ to: "/dashboard" });
      }
    },
  });

  // ── Register ──────────────────────────────────────────────────
  const registerMutation = useMutation({
    mutationFn: (payload: RegisterPayload) => apiRegister(payload),
    onSuccess: () => {
      navigate({ to: "/auth/login" });
    },
  });

  // ── Logout ────────────────────────────────────────────────────
  const logoutMutation = useMutation({
    mutationFn: () => apiLogout(),
    onSuccess: () => {
      queryClient.setQueryData(PROFILE_QUERY_KEY, null);
      queryClient.clear();
      navigate({ to: "/" });
    },
  });

  return {
    /** Currently authenticated user or null */
    user: user ?? null,
    /** True while the initial profile query is loading */
    isLoading,
    /** True when the profile query ended in error (network issues etc.) */
    isError,
    /** Whether there is an authenticated session */
    isAuthenticated: !!user,

    // Mutations — call .mutate() / .mutateAsync()
    login: loginMutation,
    register: registerMutation,
    logout: logoutMutation,
  };
}
