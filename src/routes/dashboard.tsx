import { createFileRoute, Link } from "@tanstack/react-router";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Activity, Brain, TrendingUp, Heart, ArrowLeft, Sparkles } from "lucide-react";
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

export const Route = createFileRoute("/dashboard")({
  head: () => ({ meta: [{ title: "لوحة التحكم | بصمة+" }] }),
  component: Dashboard,
});

const screen = [
  { d: "السبت", h: 6.2 },
  { d: "الأحد", h: 5.4 },
  { d: "الاثنين", h: 4.8 },
  { d: "الثلاثاء", h: 5.1 },
  { d: "الأربعاء", h: 3.9 },
  { d: "الخميس", h: 4.5 },
  { d: "الجمعة", h: 4.2 },
];
const mood = [
  { d: "س", v: 6 },
  { d: "ح", v: 7 },
  { d: "ن", v: 5 },
  { d: "ث", v: 8 },
  { d: "ر", v: 7 },
  { d: "خ", v: 8 },
  { d: "ج", v: 9 },
];
const scores = [
  { t: "الصحة الرقمية", v: 82, c: "text-primary", i: Activity, to: "/digital-health" as const },
  { t: "التعلّم", v: 74, c: "text-info", i: Brain, to: "/learning-hub" as const },
  { t: "الإنتاجية", v: 68, c: "text-warning", i: TrendingUp, to: "/planner" as const },
  { t: "الرفاه", v: 79, c: "text-success", i: Heart, to: "/mood" as const },
];
const tasks = [
  { t: "جلسة بومودورو لمادة الخوارزميات", done: true },
  { t: "قراءة فصل من كتاب التعلم العميق", done: true },
  { t: "تمرين رياضي ٢٠ دقيقة", done: false },
  { t: "تسجيل المزاج اليومي", done: false },
  { t: "مراجعة الأهداف الأسبوعية", done: false },
];
const suggestions = [
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
];

function Dashboard() {
  return (
    <AppShell
      title="مساء الخير، بشّار 👋"
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
        {scores.map((s) => {
          const Icon = s.i;
          return (
            <Link key={s.t} to={s.to}>
              <Card className="group p-5 transition-all hover:shadow-glow">
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
                  <span className="text-3xl font-extrabold">{s.v}</span>
                  <span className="text-sm text-muted-foreground">/100</span>
                </div>
                <Progress value={s.v} className="mt-3 h-1.5" />
              </Card>
            </Link>
          );
        })}
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        <Card className="p-5 xl:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold">وقت الشاشة هذا الأسبوع</h3>
              <p className="text-xs text-muted-foreground">متوسط ٤.٨ ساعة يوميًا</p>
            </div>
            <Badge variant="secondary">انخفاض ١٢٪</Badge>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={screen}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.4} />
                <XAxis dataKey="d" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    background: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: 8,
                  }}
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
              <LineChart data={mood}>
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

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        <Card className="p-5 xl:col-span-2">
          <h3 className="mb-4 text-lg font-bold">مهام اليوم</h3>
          <div className="space-y-2">
            {tasks.map((t, i) => (
              <label
                key={i}
                className="flex cursor-pointer items-center gap-3 rounded-lg p-3 transition hover:bg-muted/60"
              >
                <Checkbox defaultChecked={t.done} />
                <span className={t.done ? "flex-1 text-muted-foreground line-through" : "flex-1"}>
                  {t.t}
                </span>
                {t.done && (
                  <Badge variant="secondary" className="text-success">
                    +١٠ نقاط
                  </Badge>
                )}
              </label>
            ))}
          </div>
        </Card>
        <Card className="p-5">
          <div className="mb-3 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <h3 className="text-lg font-bold">اقتراحات ذكيّة</h3>
          </div>
          <div className="space-y-3">
            {suggestions.map((s) => (
              <div key={s.t} className="rounded-lg border bg-muted/30 p-3">
                <div className="text-sm font-semibold">{s.t}</div>
                <p className="mt-1 text-xs text-muted-foreground">{s.d}</p>
                <Button size="sm" variant="ghost" className="mt-2 -mb-1 px-2 text-primary">
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
