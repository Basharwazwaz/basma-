import { createFileRoute } from "@tanstack/react-router";
import { useState, useRef, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Sparkles, CheckCircle2, Loader2 } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
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
  Legend,
} from "recharts";
import { apiGetMoods, apiSubmitMood, apiGetPlanner, apiGetTasks } from "@/lib/api";
import { Slider } from "@/components/ui/slider";
import { toast } from "sonner";

export const Route = createFileRoute("/mood")({
  head: () => ({ meta: [{ title: "تتبّع المزاج | بصمة+" }] }),
  component: Mood,
});

const emojis = [
  { e: "😫", state: "TERRIBLE", l: "سيّئ جدًا", v: 1 },
  { e: "😔", state: "BAD", l: "متعب", v: 3 },
  { e: "😐", state: "NEUTRAL", l: "عادي", v: 5 },
  { e: "🙂", state: "GOOD", l: "جيّد", v: 7 },
  { e: "😄", state: "EXCELLENT", l: "ممتاز", v: 10 },
];

function Mood() {
  const queryClient = useQueryClient();
  const today = new Date().toISOString().split("T")[0];

  const { data: moodLogs = [], isLoading } = useQuery({
    queryKey: ["moods"],
    queryFn: () => apiGetMoods(),
  });

  const todayLog = moodLogs.find((m) => m.record_date === today);

  const [sel, setSel] = useState<number | null>(todayLog?.mood_score || null);
  const [stressScore, setStressScore] = useState(todayLog?.stress_score ?? 5);
  const [note, setNote] = useState(todayLog?.note || "");
  const [showConfetti, setShowConfetti] = useState(false);

  const submitMoodMutation = useMutation({
    mutationFn: apiSubmitMood,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["moods"] });
      setShowConfetti(true);
      setTimeout(() => setShowConfetti(false), 1000);
      toast.success("تم حفظ مزاجك اليوم!");
      localStorage.setItem("basma-mood-date", today);
    },
    onError: () => {
      toast.error("فشل حفظ المزاج");
    },
  });

  const handleSave = () => {
    if (!sel) return;
    const emojiConfig = emojis.find((e) => e.v === sel) || emojis[2];
    submitMoodMutation.mutate({
      record_date: today,
      mood_score: sel,
      stress_score: stressScore,
      mood_state: emojiConfig.state,
      note: note.trim() || undefined,
    });
  };

  const isSaved = todayLog?.mood_score === sel && todayLog?.note === note && todayLog?.stress_score === stressScore;

  const chartData = useMemo(() => {
    // Reverse so oldest is first (for chart LTR or RTL logic)
    const sorted = [...moodLogs].sort(
      (a, b) => new Date(a.record_date).getTime() - new Date(b.record_date).getTime(),
    );
    return sorted
      .map((log) => ({
        d: new Date(log.record_date).toLocaleDateString("ar-EG", { weekday: "short" }),
        v: log.mood_score,
      }))
      .slice(-7); // Last 7 days
  }, [moodLogs]);

  const { data: plannerItems = [] } = useQuery({
    queryKey: ["planner"],
    queryFn: () => apiGetPlanner(),
  });

  const { data: tasks = [] } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => apiGetTasks(),
  });

  // Build study hours per day of week from planner items (start/end time)
  const corrData = useMemo(() => {
    const dayNames = ["س", "ح", "ن", "ث", "ر", "خ", "ج"];
    const studyHours: number[] = new Array(7).fill(0);

    plannerItems.forEach((p) => {
      if (p.start_time && p.end_time) {
        const start = new Date(`2000-01-01T${p.start_time}`);
        const end = new Date(`2000-01-01T${p.end_time}`);
        const hours = (end.getTime() - start.getTime()) / (1000 * 60 * 60);
        if (hours > 0) {
          const d = new Date(p.plan_date).getDay();
          const dayIdx = d === 0 ? 6 : d - 1; // Convert: Sun=6, Mon=0, ...
          studyHours[dayIdx] += hours;
        }
      }
    });

    const sorted = [...moodLogs].sort(
      (a, b) => new Date(a.record_date).getTime() - new Date(b.record_date).getTime(),
    );

    // Group mood by day of week (last 7 days)
    const moodByDay: Record<number, number[]> = {};
    sorted.slice(-7).forEach((log) => {
      const dayIdx = new Date(log.record_date).getDay();
      const idx = dayIdx === 0 ? 6 : dayIdx - 1;
      if (!moodByDay[idx]) moodByDay[idx] = [];
      moodByDay[idx].push(log.mood_score);
    });

    return dayNames.map((d, i) => ({
      d,
      mood: moodByDay[i]?.length ? Math.round(moodByDay[i].reduce((a, b) => a + b, 0) / moodByDay[i].length) : 0,
      study: Math.round(studyHours[i] * 10) / 10,
    }));
  }, [moodLogs, plannerItems]);

  return (
    <AppShell title="تتبّع المزاج" subtitle="افهم مشاعرك وعلاقتها بعاداتك.">
      <Card className="mb-6 p-6 relative">
        <h2 className="text-lg font-bold">كيف تشعر اليوم؟</h2>
        <div className="mt-5 flex flex-wrap justify-around gap-3">
          {emojis.map((m) => (
            <button
              key={m.v}
              onClick={() => setSel(m.v)}
              className={`flex flex-col items-center gap-2 rounded-2xl border-2 px-4 py-3 transition-transform duration-200 hover:scale-110 ${sel === m.v ? "border-primary bg-primary/10 shadow-glow scale-110" : "border-transparent bg-muted/40 hover:bg-muted"}`}
            >
              <span className="text-4xl">{m.e}</span>
              <span className="text-xs font-semibold">{m.l}</span>
            </button>
          ))}
        </div>
        <div className="mt-6">
          <Textarea
            placeholder="اكتب ما يدور في بالك (اختياري)..."
            rows={3}
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
        </div>
        <div className="mt-6">
          <div className="flex items-center justify-between mb-2">
            <Label className="text-sm font-medium">مستوى التوتر</Label>
            <span className="text-sm font-bold text-primary">{stressScore}/10</span>
          </div>
          <Slider
            min={1}
            max={10}
            step={1}
            value={[stressScore]}
            onValueChange={([v]) => setStressScore(v)}
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>هادئ</span>
            <span>توتر شديد</span>
          </div>
        </div>
        <div className="mt-4 relative">
          <Button
            onClick={handleSave}
            disabled={isSaved || !sel || submitMoodMutation.isPending}
            className={`gradient-primary shadow-soft transition-all ${isSaved ? "bg-success hover:bg-success text-success-foreground" : ""}`}
          >
            {submitMoodMutation.isPending ? (
              <Loader2 className="me-2 h-4 w-4 animate-spin" />
            ) : isSaved ? (
              <>
                <CheckCircle2 className="me-2 h-4 w-4" /> تم الحفظ
              </>
            ) : (
              "حفظ مزاج اليوم"
            )}
          </Button>

          {/* Confetti container */}
          {showConfetti && (
            <div className="absolute top-0 right-1/2 translate-x-1/2 pointer-events-none">
              <div
                className="confetti-dot"
                style={{ background: "#ff3b30", transform: "translate(-20px, -30px)" }}
              ></div>
              <div
                className="confetti-dot"
                style={{
                  background: "#34c759",
                  transform: "translate(20px, -40px)",
                  animationDelay: "0.1s",
                }}
              ></div>
              <div
                className="confetti-dot"
                style={{
                  background: "#007aff",
                  transform: "translate(0px, -50px)",
                  animationDelay: "0.05s",
                }}
              ></div>
              <div
                className="confetti-dot"
                style={{
                  background: "#ffcc00",
                  transform: "translate(-40px, -10px)",
                  animationDelay: "0.15s",
                }}
              ></div>
              <div
                className="confetti-dot"
                style={{
                  background: "#af52de",
                  transform: "translate(40px, -20px)",
                  animationDelay: "0.2s",
                }}
              ></div>
            </div>
          )}
        </div>
      </Card>

      {sel && sel >= 7 && isSaved && (
        <Card className="mb-6 bg-success/10 p-4 text-success-foreground">
          <strong className="text-success">رائع!</strong> يومك يبدو إيجابيًا. حاول الحفاظ على هذا
          الإيقاع بنوم منتظم وتعرّض كافٍ للشمس.
        </Card>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="p-5">
          <h3 className="mb-4 font-bold">مزاجك خلال الأسبوع</h3>
          <div className="h-64">
            {isLoading ? (
              <div className="h-full flex items-center justify-center">
                <Loader2 className="animate-spin text-muted-foreground" />
              </div>
            ) : chartData.length > 0 ? (
              <ResponsiveContainer>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.4} />
                  <XAxis dataKey="d" fontSize={12} />
                  <YAxis domain={[0, 10]} fontSize={12} />
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
                    dot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-muted-foreground">
                لا توجد بيانات كافية
              </div>
            )}
          </div>
        </Card>
        <Card className="p-5">
          <h3 className="mb-4 font-bold">المزاج مقابل ساعات الدراسة</h3>
          <div className="h-64">
            <ResponsiveContainer>
              <BarChart data={corrData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.4} />
                <XAxis dataKey="d" fontSize={12} />
                <YAxis fontSize={12} />
                <Tooltip
                  contentStyle={{
                    background: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: 8,
                  }}
                />
                <Legend />
                <Bar name="مزاج" dataKey="mood" fill="var(--chart-1)" radius={[6, 6, 0, 0]} />
                <Bar name="دراسة" dataKey="study" fill="var(--chart-2)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 sm:grid-cols-2">
        <Card className="p-5 border-l-4 border-l-warning bg-warning/5">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="h-5 w-5 text-warning-foreground" />
            <h3 className="font-bold">رؤية ذكية</h3>
          </div>
          <p className="text-sm text-muted-foreground">
            كلما زاد عدد الأيام التي تسجل فيها مزاجك، كلما تمكنّا من إعطائك تحليلات أدق عن عاداتك!
          </p>
        </Card>

        <Card className="p-5 flex items-center justify-between">
          <div>
            <h3 className="font-bold">سلسلة الأيام</h3>
            <p className="text-sm text-muted-foreground mt-1">
              سجّلت مزاجك {moodLogs.length} يومًا في النظام 🔥
            </p>
          </div>
          <div className="flex items-center justify-center h-14 w-14 rounded-full bg-accent/20 text-accent-foreground font-black text-2xl">
            {moodLogs.length}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
