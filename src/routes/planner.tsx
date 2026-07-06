import { createFileRoute } from "@tanstack/react-router";
import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import {
  Play,
  Pause,
  RotateCcw,
  SkipForward,
  Settings,
  Plus,
  Sparkles,
  Loader2,
  X,
} from "lucide-react";
import { usePomodoro, type PomodoroSettings, type SessionType } from "@/hooks/use-pomodoro";
import { apiGetTasks, apiCreateTask, apiUpdateTask, apiDeleteTask, apiGetPlanner } from "@/lib/api";
import { toast } from "sonner";
import { Input } from "@/components/ui/input";

export const Route = createFileRoute("/planner")({
  head: () => ({ meta: [{ title: "المخطط الأسبوعي | بصمة+" }] }),
  component: Planner,
});

const days = ["السبت", "الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة"];
// Keep initial mocked for display when there's no data, but let's just make it empty by default
// const slots = [ ... ];
const catColor: Record<string, string> = {
  study: "bg-info/15 text-info border-info/30",
  learn: "bg-primary/15 text-primary border-primary/30",
  exam: "bg-destructive/15 text-destructive border-destructive/30",
  health: "bg-success/15 text-success border-success/30",
  personal: "bg-warning/15 text-warning-foreground border-warning/30",
  career: "bg-accent/40 text-accent-foreground border-accent",
};

const SESSION_LABELS: Record<SessionType, string> = {
  work: "وقت العمل",
  shortBreak: "استراحة قصيرة",
  longBreak: "استراحة طويلة",
};

const SESSION_COLORS: Record<SessionType, string> = {
  work: "gradient-primary",
  shortBreak: "bg-gradient-to-br from-emerald-500 to-teal-600",
  longBreak: "bg-gradient-to-br from-violet-500 to-purple-700",
};

/** Convert a plain number to Eastern Arabic numerals */
function toArabicNumerals(n: number): string {
  return n
    .toString()
    .split("")
    .map((c) => "٠١٢٣٤٥٦٧٨٩"[parseInt(c)] ?? c)
    .join("");
}

function pad(n: number) {
  return n.toString().padStart(2, "0");
}

function PomodoroSettingsDialog({
  settings,
  onChange,
}: {
  settings: PomodoroSettings;
  onChange: (s: PomodoroSettings) => void;
}) {
  const [local, setLocal] = useState(settings);

  function apply() {
    onChange(local);
  }

  return (
    <DialogContent className="max-w-sm">
      <DialogHeader>
        <DialogTitle>إعدادات بومودورو</DialogTitle>
      </DialogHeader>
      <div className="space-y-6 pt-2">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label className="text-sm font-medium">مدة العمل</Label>
            <span className="text-sm font-bold text-primary">{local.workMinutes} دقيقة</span>
          </div>
          <Slider
            min={5}
            max={60}
            step={5}
            value={[local.workMinutes]}
            onValueChange={([v]) => setLocal((p) => ({ ...p, workMinutes: v }))}
          />
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label className="text-sm font-medium">استراحة قصيرة</Label>
            <span className="text-sm font-bold text-emerald-500">
              {local.shortBreakMinutes} دقيقة
            </span>
          </div>
          <Slider
            min={1}
            max={15}
            step={1}
            value={[local.shortBreakMinutes]}
            onValueChange={([v]) => setLocal((p) => ({ ...p, shortBreakMinutes: v }))}
          />
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label className="text-sm font-medium">استراحة طويلة</Label>
            <span className="text-sm font-bold text-violet-500">
              {local.longBreakMinutes} دقيقة
            </span>
          </div>
          <Slider
            min={10}
            max={30}
            step={5}
            value={[local.longBreakMinutes]}
            onValueChange={([v]) => setLocal((p) => ({ ...p, longBreakMinutes: v }))}
          />
        </div>

        <Button className="w-full gradient-primary shadow-soft" onClick={apply}>
          حفظ الإعدادات
        </Button>
      </div>
    </DialogContent>
  );
}

const TASKS_QUERY_KEY = ["tasks"];

function Planner() {
  const queryClient = useQueryClient();
  const [settings, setSettings] = useState<PomodoroSettings>({
    workMinutes: 25,
    shortBreakMinutes: 5,
    longBreakMinutes: 15,
  });

  const { state, toggle, reset, skip } = usePomodoro(settings);

  const { data: tasks = [], isLoading: isLoadingTasks } = useQuery({
    queryKey: TASKS_QUERY_KEY,
    queryFn: () => apiGetTasks(),
  });

  const { data: plannerItems = [], isLoading: isLoadingPlanner } = useQuery({
    queryKey: ["planner"],
    queryFn: () => apiGetPlanner(),
  });

  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [isAddingTask, setIsAddingTask] = useState(false);

  const createTaskMutation = useMutation({
    mutationFn: apiCreateTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
      setNewTaskTitle("");
      setIsAddingTask(false);
      toast.success("تم إضافة المهمة");
    },
  });

  const deleteTaskMutation = useMutation({
    mutationFn: apiDeleteTask,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY }),
  });

  const handleAddTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;
    createTaskMutation.mutate({
      title: newTaskTitle.trim(),
      status: "PENDING",
      is_completed: false,
    });
  };

  const timeDisplay = useMemo(
    () => `${toArabicNumerals(state.minutes)}:${pad(state.seconds)}`,
    [state.minutes, state.seconds],
  );

  const cyclePosition = state.sessionCount % 4;
  const unscheduled = tasks.filter((t) => !t.is_completed);

  const displaySlots = plannerItems.map((p) => {
    const d = new Date(p.plan_date);
    let dayIndex = d.getDay() + 1; // getDay() is 0=Sun, we want 0=Sat. So Sun=1. Mon=2. Tue=3. Wed=4. Thu=5. Fri=6. Sat=0.
    if (dayIndex === 7) dayIndex = 0;

    // start_time comes like "HH:MM:SS"
    const tStr = p.start_time ? p.start_time.substring(0, 5) : "١٢:٠٠";
    const mappedT =
      toArabicNumerals(parseInt(tStr.split(":")[0])) +
      ":" +
      toArabicNumerals(parseInt(tStr.split(":")[1]));

    return {
      d: dayIndex,
      t: mappedT,
      title: p.title,
      cat: "study", // default for now
    };
  });

  return (
    <AppShell
      title="المخطط الأسبوعي"
      subtitle="نظّم وقتك بذكاء ووازن بين الدراسة والراحة."
      actions={
        <Button className="gradient-primary shadow-soft">
          <Sparkles className="ms-1 h-4 w-4" /> خطّة ذكيّة
        </Button>
      }
    >
      <div className="grid gap-6 xl:grid-cols-[1fr_320px]">
        {/* Weekly Calendar - Hardcoded for now until we fully integrate Planner model */}
        <Card className="overflow-hidden p-0">
          <div className="grid grid-cols-7 border-b bg-muted/40 text-center text-xs font-semibold">
            {days.map((d, i) => (
              <div key={d} className={`p-3 ${i === 0 ? "" : "border-r"}`}>
                {d}
              </div>
            ))}
          </div>
          <div className="grid grid-cols-7 relative">
            {isLoadingPlanner && (
              <div className="absolute inset-0 flex justify-center items-center bg-background/50 z-10">
                <Loader2 className="animate-spin" />
              </div>
            )}
            {days.map((_, di) => (
              <div key={di} className={`min-h-[320px] space-y-2 p-2 ${di === 0 ? "" : "border-r"}`}>
                {displaySlots
                  .filter((s) => s.d === di)
                  .map((s, i) => (
                    <div key={i} className={`rounded-lg border p-2 text-xs ${catColor[s.cat]}`}>
                      <div className="font-bold">{s.t}</div>
                      <div className="mt-0.5">{s.title}</div>
                    </div>
                  ))}
              </div>
            ))}
          </div>
        </Card>

        <div className="space-y-4">
          <Card
            className={`${SESSION_COLORS[state.sessionType]} overflow-hidden p-6 text-center text-white shadow-glow transition-all duration-700`}
          >
            <div className="text-xs font-semibold tracking-widest uppercase opacity-90">
              {SESSION_LABELS[state.sessionType]}
            </div>

            <div
              className="my-4 text-6xl font-extrabold tabular-nums tracking-tight"
              style={{ fontVariantNumeric: "tabular-nums", direction: "ltr" }}
            >
              {timeDisplay}
            </div>

            <div className="mb-4 flex items-center justify-center gap-2">
              {[0, 1, 2, 3].map((i) => (
                <div
                  key={i}
                  className={`h-2 rounded-full transition-all duration-300 ${
                    i < cyclePosition
                      ? "w-6 bg-white"
                      : i === cyclePosition && state.sessionType === "work"
                        ? "w-4 bg-white/70"
                        : "w-2 bg-white/30"
                  }`}
                />
              ))}
            </div>

            <div className="flex items-center justify-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                className="text-white/70 hover:bg-white/10"
                onClick={reset}
              >
                <RotateCcw className="h-4 w-4" />
              </Button>
              <Button variant="secondary" className="w-36 gap-2 font-semibold" onClick={toggle}>
                {state.running ? (
                  <>
                    <Pause className="h-4 w-4" /> إيقاف مؤقت
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4" /> ابدأ الجلسة
                  </>
                )}
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="text-white/70 hover:bg-white/10"
                onClick={skip}
              >
                <SkipForward className="h-4 w-4" />
              </Button>
            </div>

            <div className="mt-4 flex items-center justify-between text-xs opacity-80">
              <span>
                جلسة{" "}
                {toArabicNumerals(state.sessionCount % 4 || (state.sessionType !== "work" ? 4 : 0))}{" "}
                من {toArabicNumerals(4)} اليوم
              </span>
              <Dialog>
                <DialogTrigger asChild>
                  <button className="flex items-center gap-1 rounded px-2 py-1 hover:bg-white/10 transition-colors">
                    <Settings className="h-3.5 w-3.5" />
                    <span>إعدادات</span>
                  </button>
                </DialogTrigger>
                <PomodoroSettingsDialog settings={settings} onChange={setSettings} />
              </Dialog>
            </div>
          </Card>

          <Card className="p-4">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-bold">مهام بدون موعد</h3>
              <Button size="icon" variant="ghost" onClick={() => setIsAddingTask(!isAddingTask)}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>

            {isAddingTask && (
              <form onSubmit={handleAddTask} className="mb-3 flex items-center gap-2">
                <Input
                  size={1}
                  className="h-8 text-sm"
                  placeholder="مهمة جديدة..."
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  autoFocus
                />
                <Button
                  size="icon"
                  type="submit"
                  className="h-8 w-8 shrink-0"
                  disabled={createTaskMutation.isPending}
                >
                  {createTaskMutation.isPending ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <Plus className="h-3 w-3" />
                  )}
                </Button>
              </form>
            )}

            <div className="space-y-2">
              {isLoadingTasks ? (
                <div className="py-4 flex justify-center">
                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                </div>
              ) : unscheduled.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-4">
                  لا توجد مهام حالياً
                </p>
              ) : (
                unscheduled.map((t) => (
                  <div
                    key={t.id}
                    className="group flex items-center justify-between rounded-lg border bg-muted/30 p-2 px-3 text-sm transition-colors hover:border-border"
                  >
                    <span>{t.title}</span>
                    <button
                      onClick={() => deleteTaskMutation.mutate(t.id)}
                      className="text-muted-foreground opacity-0 group-hover:opacity-100 hover:text-destructive transition-opacity"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="mb-2 text-sm font-bold">ملخّص اليوم</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">جلسات دراسة مكتملة</span>
                <Badge>{toArabicNumerals(state.sessionCount)}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">وقت تعلّم</span>
                <Badge>
                  {toArabicNumerals(Math.floor((state.sessionCount * settings.workMinutes) / 60))}س{" "}
                  {toArabicNumerals((state.sessionCount * settings.workMinutes) % 60)}د
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">الجلسة الحالية</span>
                <Badge variant="secondary">{SESSION_LABELS[state.sessionType]}</Badge>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
