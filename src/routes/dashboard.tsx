import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Activity,
  Brain,
  TrendingUp,
  Heart,
  ArrowLeft,
  Sparkles,
  RefreshCw,
  Plus,
} from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { toast } from "sonner";
import { useAuth } from "@/hooks/use-auth";
import { useCountUp } from "@/hooks/use-count-up";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  apiGetTasks,
  apiCreateTask,
  apiUpdateTask,
  apiGetDashboardSummary,
  apiSubmitMood,
} from "@/lib/api";
import { Loader2, type LucideIcon } from "lucide-react";
import type { DashboardSummaryData } from "@/lib/api";

const ICON_MAP: Record<string, LucideIcon> = {
  Activity,
  Brain,
  TrendingUp,
  Heart,
};

export const Route = createFileRoute("/dashboard")({
  head: () => ({ meta: [{ title: "لوحة التحكم | بصمة+" }] }),
  component: Dashboard,
});

const ALL_SUGGESTIONS = [
  [
    {
      t: "خذ استراحة من الشاشة",
      d: "تجاوزت ٤ ساعات أمام الشاشة. جرّب تمشية ١٠ دقائق.",
      a: "أضف للمخطط",
    },
    {
      t: "تحدٍّ جديد يناسبك",
      d: "تحدّي «أسبوع بلا تيك توك بعد ٩ مساءً» يبدو مثاليًا لك.",
      a: "ابدأ التحدي",
    },
    { t: "كورس مقترح", d: "أساسيات SQL — ٣ ساعات فقط.", a: "اعرض الكورس" },
  ],
  [
    {
      t: "جلسة تركيز قصيرة",
      d: "لم تكمل أي جلسة بومودورو اليوم. ابدأ الآن لمدة ٢٥ دقيقة.",
      a: "ابدأ الجلسة",
    },
    { t: "راجع أهدافك", d: "هدف قراءة الكتب متأخر قليلاً عن المخطط.", a: "تحديث الأهداف" },
    { t: "مقال يهمك", d: "كيف تستعد لمقابلة تقنية في ١٠ أيام.", a: "اقرأ المقال" },
  ],
  [
    { t: "استرخاء وتأمل", d: "مزاجك اليوم متقلب. خصص ١٥ دقيقة للتأمل.", a: "افتح التأمل" },
    { t: "وقت النوم اقترب", d: "تذكر هدفك بالنوم قبل منتصف الليل.", a: "إعداد تنبيه" },
    { t: "ملخص أسبوعي", d: "أداؤك هذا الأسبوع ارتفع بنسبة ١٥٪.", a: "شاهد التقرير" },
  ],
];

const MOODS = [
  { label: "ممتاز", emoji: "🤩", value: 5, color: "hover:bg-success/20 hover:border-success/50" },
  { label: "جيّد", emoji: "😊", value: 4, color: "hover:bg-info/20 hover:border-info/50" },
  { label: "عادي", emoji: "😐", value: 3, color: "hover:bg-warning/20 hover:border-warning/50" },
  {
    label: "سيّء",
    emoji: "😔",
    value: 2,
    color: "hover:bg-destructive/20 hover:border-destructive/50",
  },
  { label: "مُرهق", emoji: "😫", value: 1, color: "hover:bg-accent/20 hover:border-accent/50" },
];

function getGreeting(name: string) {
  const hour = new Date().getHours();
  if (hour >= 5 && hour < 12) return `صباح الخير، ${name} 🌅`;
  if (hour >= 12 && hour < 17) return `مساء الخير، ${name} ☀️`;
  if (hour >= 17 && hour < 21) return `مساء النور، ${name} 🌇`;
  return `تصبح على خير، ${name} 🌙`;
}

function ScoreCard({ s }: { s: DashboardSummaryData["scores"][0] }) {
  const animatedValue = useCountUp(s.v, 1200);
  const Icon = ICON_MAP[s.i] || Activity;

  return (
    <Link to={s.to}>
      <Card className="group p-5 transition-all hover:shadow-glow hover:-translate-y-1">
        <div className="flex items-start justify-between">
          <div
            className={`gradient-warm inline-flex h-10 w-10 items-center justify-center rounded-xl ${s.c}`}
          >
            <Icon className="h-5 w-5" />
          </div>
          <span className="text-xs text-success">+٤٪</span>
        </div>
        <div className="mt-4 text-sm text-muted-foreground">{s.t}</div>
        <div className="mt-1 flex items-end gap-1.5">
          <span className="text-3xl font-extrabold tabular-nums">{animatedValue}</span>
          <span className="text-sm text-muted-foreground">/100</span>
        </div>
        <Progress value={animatedValue} className="mt-3 h-1.5 transition-all duration-300" />
      </Card>
    </Link>
  );
}

function Dashboard() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const userName = user?.profile?.first_name ?? "يا صديقي";
  const [greeting, setGreeting] = useState(`أهلاً بك، ${userName}`);

  const { data: dashboard, isLoading: isLoadingDashboard } = useQuery({
    queryKey: ["dashboard_summary"],
    queryFn: () => apiGetDashboardSummary(),
  });

  const { data: tasks = [], isLoading: isLoadingTasks } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => apiGetTasks(),
  });

  const updateTaskMutation = useMutation({
    mutationFn: ({
      id,
      is_completed,
      status,
    }: {
      id: string;
      is_completed: boolean;
      status: string;
    }) => apiUpdateTask(id, { is_completed, status: status as "DONE" | "PENDING" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tasks"] }),
    onError: () => toast.error("فشل تحديث المهمة. حاول مرة أخرى."),
  });

  const createTaskMutation = useMutation({
    mutationFn: apiCreateTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      setNewTaskTitle("");
    },
    onError: () => toast.error("فشل إضافة المهمة. حاول مرة أخرى."),
  });

  const [newTaskTitle, setNewTaskTitle] = useState("");

  const [suggIndex, setSuggIndex] = useState(0);

  const [moodLogged, setMoodLogged] = useState(false);
  const moodMutation = useMutation({
    mutationFn: (payload: { mood_score: number; stress_score: number; mood_state: string }) =>
      apiSubmitMood({
        ...payload,
        record_date: new Date().toISOString().split("T")[0],
      }),
    onSuccess: () => {
      setMoodLogged(true);
      toast("تم تسجيل المزاج اليوم ✓");
    },
    onError: () => {
      toast.error("فشل تسجيل المزاج. حاول مرة أخرى.");
    },
  });

  useEffect(() => {
    setGreeting(getGreeting(userName));

    const today = new Date().toISOString().split("T")[0];
    const lastMoodDate = localStorage.getItem("basma-mood-date");
    if (lastMoodDate === today) {
      setMoodLogged(true);
    }
  }, [userName]);

  const toggleTask = (id: string, currentlyDone: boolean) => {
    updateTaskMutation.mutate({
      id,
      is_completed: !currentlyDone,
      status: !currentlyDone ? "DONE" : "PENDING",
    });
    if (!currentlyDone) {
      toast.success("+١٠ نقاط 🎉", {
        description: "تم إنجاز المهمة بنجاح!",
      });
    }
  };

  const addTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;
    createTaskMutation.mutate({
      title: newTaskTitle.trim(),
      status: "PENDING",
      is_completed: false,
    });
  };

  const logMood = (label: string, emoji: string) => {
    const valueMap: Record<string, number> = {
      ممتاز: 5,
      جيّد: 4,
      عادي: 3,
      سيّء: 2,
      مُرهق: 1,
    };
    const moodScore = valueMap[label] ?? 3;
    moodMutation.mutate({
      mood_score: moodScore,
      stress_score: 10 - moodScore,
      mood_state: label,
    });
    try {
      localStorage.setItem("basma-mood-date", new Date().toISOString().split("T")[0]);
      localStorage.setItem("basma-mood-last", label);
    } catch {
      // localStorage may be unavailable
    }
    toast(`تم تسجيل المزاج اليوم ✓`, {
      description: `مزاجك: ${emoji} ${label}`,
      icon: emoji,
    });
  };

  const currentSuggestions = dashboard?.suggestions || [];

  return (
    <AppShell
      title={greeting}
      subtitle="إليك ملخّص يومك."
      actions={
        <Button asChild className="gradient-primary shadow-soft hidden sm:inline-flex">
          <Link to="/ai-coach">
            <Sparkles className="ms-1 h-4 w-4" /> اسأل المدرّب
          </Link>
        </Button>
      }
    >
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {isLoadingDashboard ? (
          <div className="col-span-full py-10 flex justify-center">
            <Loader2 className="animate-spin text-muted-foreground" />
          </div>
        ) : (
          dashboard?.scores.map((s) => <ScoreCard key={s.t} s={s} />)
        )}
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        <Card className="p-5 xl:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold">وقت الشاشة هذا الأسبوع</h3>
              <p className="text-xs text-muted-foreground">
                متوسط {dashboard?.screen_time_avg || 0} ساعة يوميًا
              </p>
            </div>
            <Badge variant="secondary">انخفاض ١٢٪</Badge>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dashboard?.screen_time || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.4} />
                <XAxis dataKey="d" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    background: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: 8,
                  }}
                  cursor={{ fill: "hsl(var(--muted)/0.4)" }}
                />
                <Bar dataKey="h" fill="var(--primary)" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card className="p-5">
          <h3 className="text-lg font-bold">مزاجك</h3>
          <p className="text-xs text-muted-foreground">آخر ٧ أيام</p>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dashboard?.mood_chart || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.4} />
                <XAxis dataKey="d" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis domain={[0, 10]} stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    background: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: 8,
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="v"
                  stroke="var(--chart-3)"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Mood Quick Log */}
      {!moodLogged && (
        <Card className="mt-6 p-5 border-primary/20 bg-primary/5">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div>
              <h3 className="font-bold flex items-center gap-2">
                <Heart className="h-4 w-4 text-primary" />
                كيف حالك الآن؟
              </h3>
              <p className="text-xs text-muted-foreground mt-1">
                تسجيل المزاج يساعد المدرّب على تقديم نصائح أفضل.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 justify-center">
              {MOODS.map((m) => (
                <button
                  key={m.label}
                  onClick={() => logMood(m.label, m.emoji)}
                  className={`flex flex-col items-center justify-center p-3 rounded-xl border bg-card transition-all hover:scale-105 ${m.color}`}
                >
                  <span className="text-2xl">{m.emoji}</span>
                  <span className="text-[10px] mt-1 font-medium">{m.label}</span>
                </button>
              ))}
            </div>
          </div>
        </Card>
      )}

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        <Card className="p-5 xl:col-span-2 flex flex-col">
          <h3 className="mb-4 text-lg font-bold">مهام اليوم</h3>
          <div className="space-y-2 flex-1">
            {isLoadingTasks ? (
              <div className="py-10 flex justify-center">
                <Loader2 className="animate-spin text-muted-foreground" />
              </div>
            ) : tasks.length === 0 ? (
              <div className="flex flex-col items-center justify-center rounded-xl border border-dashed py-10 text-center bg-muted/20 h-full">
                <Activity className="mb-3 h-10 w-10 text-muted-foreground/30" />
                <p className="font-semibold text-muted-foreground">لا توجد مهام اليوم</p>
                <p className="mt-1 text-sm text-muted-foreground/70">
                  أضف مهمتك الأولى لتنظيم يومك
                </p>
              </div>
            ) : (
              tasks.map((t) => (
                <label
                  key={t.id}
                  className="flex cursor-pointer items-center gap-3 rounded-lg border border-transparent p-3 transition-all hover:bg-muted/60 hover:border-border"
                >
                  <Checkbox
                    checked={t.is_completed}
                    onCheckedChange={() => toggleTask(t.id, t.is_completed)}
                    disabled={updateTaskMutation.isPending}
                  />
                  <span
                    className={
                      t.is_completed
                        ? "flex-1 text-muted-foreground line-through transition-all"
                        : "flex-1 transition-all"
                    }
                  >
                    {t.title}
                  </span>
                  {t.is_completed && (
                    <Badge
                      variant="secondary"
                      className="text-success bg-success/10 animate-in fade-in zoom-in duration-300"
                    >
                      +١٠ نقاط
                    </Badge>
                  )}
                </label>
              ))
            )}
          </div>
          <form onSubmit={addTask} className="mt-4 flex items-center gap-2 border-t pt-4">
            <Input
              placeholder="إضافة مهمة جديدة..."
              value={newTaskTitle}
              onChange={(e) => setNewTaskTitle(e.target.value)}
              className="flex-1 bg-muted/30"
              disabled={createTaskMutation.isPending}
            />
            <Button
              type="submit"
              size="icon"
              disabled={!newTaskTitle.trim() || createTaskMutation.isPending}
            >
              {createTaskMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
            </Button>
          </form>
        </Card>

        <Card className="p-5">
          <div className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary" />
              <h3 className="text-lg font-bold">اقتراحات ذكيّة</h3>
            </div>
          </div>
          <div className={`space-y-3 transition-opacity duration-300`}>
            {currentSuggestions.map((s) => (
              <div key={s.t} className="rounded-lg border bg-muted/30 p-3">
                <div className="text-sm font-semibold">{s.t}</div>
                <p className="mt-1 text-xs text-muted-foreground">{s.d}</p>
                <Button
                  size="sm"
                  variant="ghost"
                  className="mt-2 -mb-1 px-2 text-primary hover:bg-primary/10"
                  onClick={() => {
                    if (s.a.includes("المخطط")) navigate({ to: "/planner" });
                    else if (s.a.includes("التحدي")) navigate({ to: "/challenges" });
                    else if (s.a.includes("الكورس") || s.a.includes("المقال"))
                      navigate({ to: "/learning-hub" });
                    else if (s.a.includes("الجلسة")) navigate({ to: "/planner" });
                    else if (s.a.includes("الأهداف")) navigate({ to: "/goals" });
                    else if (s.a.includes("التأمل")) navigate({ to: "/mood" });
                    else navigate({ to: "/dashboard" });
                  }}
                >
                  {s.a} <ArrowLeft className="me-1 h-3.5 w-3.5" />
                </Button>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
