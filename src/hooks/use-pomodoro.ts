import { useState, useEffect, useRef, useCallback } from "react";

export type SessionType = "work" | "shortBreak" | "longBreak";

export interface PomodoroSettings {
  workMinutes: number;
  shortBreakMinutes: number;
  longBreakMinutes: number;
}

export interface PomodoroState {
  minutes: number;
  seconds: number;
  running: boolean;
  sessionType: SessionType;
  sessionCount: number; // completed work sessions today
}

const STORAGE_KEY = "basma_pomodoro_sessions";
const TODAY_KEY = "basma_pomodoro_date";

const DEFAULT_SETTINGS: PomodoroSettings = {
  workMinutes: 25,
  shortBreakMinutes: 5,
  longBreakMinutes: 15,
};

function getTodaySessionCount(): number {
  if (typeof window === "undefined") return 0;
  try {
    const stored = localStorage.getItem(TODAY_KEY);
    const today = new Date().toDateString();
    if (stored !== today) {
      localStorage.setItem(TODAY_KEY, today);
      localStorage.setItem(STORAGE_KEY, "0");
      return 0;
    }
    return parseInt(localStorage.getItem(STORAGE_KEY) ?? "0", 10);
  } catch {
    return 0;
  }
}

function saveTodaySessionCount(count: number) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(TODAY_KEY, new Date().toDateString());
    localStorage.setItem(STORAGE_KEY, String(count));
  } catch {
    // ignore
  }
}

/** Play a subtle two-tone beep using the Web Audio API */
function playBeep() {
  try {
    const ctx = new AudioContext();
    const times = [0, 0.25];
    times.forEach((offset) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.type = "sine";
      osc.frequency.value = offset === 0 ? 880 : 660;
      gain.gain.setValueAtTime(0.3, ctx.currentTime + offset);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + offset + 0.4);
      osc.start(ctx.currentTime + offset);
      osc.stop(ctx.currentTime + offset + 0.45);
    });
  } catch {
    // Web Audio API not available
  }
}

export function usePomodoro(settings: PomodoroSettings = DEFAULT_SETTINGS) {
  const [state, setState] = useState<PomodoroState>(() => ({
    minutes: settings.workMinutes,
    seconds: 0,
    running: false,
    sessionType: "work",
    sessionCount: getTodaySessionCount(),
  }));

  // Keep settings ref up-to-date without restarting the interval
  const settingsRef = useRef(settings);
  useEffect(() => {
    settingsRef.current = settings;
  }, [settings]);

  // Keep state ref for interval callback
  const stateRef = useRef(state);
  useEffect(() => {
    stateRef.current = state;
  }, [state]);

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearTimer = useCallback(() => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const getNextSession = useCallback(
    (
      currentType: SessionType,
      currentCount: number,
    ): { type: SessionType; minutes: number; count: number } => {
      const s = settingsRef.current;
      if (currentType === "work") {
        const newCount = currentCount + 1;
        saveTodaySessionCount(newCount);
        const isLongBreak = newCount % 4 === 0;
        return {
          type: isLongBreak ? "longBreak" : "shortBreak",
          minutes: isLongBreak ? s.longBreakMinutes : s.shortBreakMinutes,
          count: newCount,
        };
      } else {
        return { type: "work", minutes: s.workMinutes, count: currentCount };
      }
    },
    [],
  );

  // Countdown tick
  useEffect(() => {
    if (!state.running) {
      clearTimer();
      return;
    }

    intervalRef.current = setInterval(() => {
      setState((prev) => {
        const totalSeconds = prev.minutes * 60 + prev.seconds - 1;

        if (totalSeconds < 0) {
          // Session ended
          playBeep();
          const next = getNextSession(prev.sessionType, prev.sessionCount);
          return {
            ...prev,
            minutes: next.minutes,
            seconds: 0,
            sessionType: next.type,
            sessionCount: next.count,
            running: false, // pause between sessions so user can choose
          };
        }

        return {
          ...prev,
          minutes: Math.floor(totalSeconds / 60),
          seconds: totalSeconds % 60,
        };
      });
    }, 1000);

    return clearTimer;
  }, [state.running, clearTimer, getNextSession]);

  const toggle = useCallback(() => {
    setState((prev) => ({ ...prev, running: !prev.running }));
  }, []);

  const reset = useCallback(() => {
    clearTimer();
    setState((prev) => ({
      ...prev,
      minutes: settingsRef.current.workMinutes,
      seconds: 0,
      running: false,
      sessionType: "work",
    }));
  }, [clearTimer]);

  const skip = useCallback(() => {
    clearTimer();
    setState((prev) => {
      const next = getNextSession(prev.sessionType, prev.sessionCount);
      return {
        ...prev,
        minutes: next.minutes,
        seconds: 0,
        running: false,
        sessionType: next.type,
        sessionCount: next.count,
      };
    });
  }, [clearTimer, getNextSession]);

  return { state, toggle, reset, skip };
}
