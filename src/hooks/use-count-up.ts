import { useState, useEffect } from "react";

const _raf =
  typeof window !== "undefined"
    ? window.requestAnimationFrame.bind(window)
    : (cb: FrameRequestCallback) => setTimeout(cb, 16) as unknown as number;
const _caf =
  typeof window !== "undefined" && window.cancelAnimationFrame
    ? window.cancelAnimationFrame.bind(window)
    : (id: number) => clearTimeout(id);

export function useCountUp(endValue: number, duration: number = 1000) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTimestamp: number | null = null;
    let frameId: number;
    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      // easeOutExpo
      const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      setCount(Math.floor(easeProgress * endValue));
      if (progress < 1) {
        frameId = _raf(step);
      } else {
        setCount(endValue);
      }
    };
    frameId = _raf(step);
    return () => _caf(frameId);
  }, [endValue, duration]);

  return count;
}
