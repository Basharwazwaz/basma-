import { describe, it, expect, vi, beforeEach } from "vitest";
import { apiFetch, tokenStore } from "@/lib/api";

describe("apiFetch", () => {
  beforeEach(() => {
    tokenStore.clear();
    vi.restoreAllMocks();
  });

  it("throws ApiError on non-2xx response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: "Internal Server Error",
        json: () => Promise.resolve({ detail: "Server error" }),
      }),
    );

    await expect(apiFetch("/test")).rejects.toThrow("Server error");
  });

  it("includes Authorization header when token is set", async () => {
    tokenStore.set("test-token");
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ data: "ok" }),
    });
    vi.stubGlobal("fetch", mockFetch);

    await apiFetch("/test");

    const headers = mockFetch.mock.calls[0][1].headers;
    expect(headers["Authorization"]).toBe("Bearer test-token");
  });

  it("sends credentials include for cookie refresh", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({}),
    });
    vi.stubGlobal("fetch", mockFetch);

    await apiFetch("/test");

    expect(mockFetch).toHaveBeenCalled();
    const fetchOpts = mockFetch.mock.calls[0][1];
    expect(fetchOpts.credentials).toBe("include");
  });
});
