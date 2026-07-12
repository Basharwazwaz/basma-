import { describe, it, expect, vi, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useCountUp } from "@/hooks/use-count-up";

describe("useCountUp", () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it("starts at 0", () => {
    vi.useFakeTimers();
    const { result } = renderHook(() => useCountUp(100, 500));
    expect(result.current).toBe(0);
  });

  it("reaches target value after animation completes", () => {
    vi.useFakeTimers();
    const { result } = renderHook(() => useCountUp(100, 100));
    act(() => {
      vi.advanceTimersByTime(200);
    });
    expect(result.current).toBe(100);
  });

  it("cleans up animation frame on unmount", () => {
    vi.useFakeTimers();
    const { unmount } = renderHook(() => useCountUp(100, 5000));
    unmount();
    act(() => {
      vi.advanceTimersByTime(10000);
    });
  });
});
