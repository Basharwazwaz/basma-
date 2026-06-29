import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Play, Pause, Plus, Sparkles } from "lucide-react";

export const Route = createFileRoute("/planner")({
  head: () => ({ meta: [{ title: "المخطط الأسبوعي | بصمة+" }] }),
  component: Planner,
});

const days = ["السبت", "الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة"];
const slots = [
  { d: 0, t: "٩:٠٠", title: "خوارزميات — مراجعة", cat: "study" },
  { d: 0, t: "١٤:٠٠", title: "تمرين رياضي", cat: "health" },
  { d: 1, t: "١٠:٣٠", title: "كورس SQL — وحدة ٣", cat: "learn" },
  { d: 2, t: "٩:٠٠", title: "امتحان قصير: تحليل", cat: "exam" },
  { d: 3, t: "١٦:٠٠", title: "قراءة كتاب", cat: "personal" },
  { d: 4, t: "١١:٠٠", title: "جلسة بومودورو", cat: "study" },
  { d: 5, t: "١٨:٠٠", title: "مقابلة وهمية", cat: "career" },
  { d: 6, t: "١٠:٠٠", title: "تأمّل ١٥د", cat: "health" },
];
const catColor: Record<string, string> = {
  study: "bg-info/15 text-info border-info/30",
  learn: "bg-primary/15 text-primary border-primary/30",
  exam: "bg-destructive/15 text-destructive border-destructive/30",
  health: "bg-success/15 text-success border-success/30",
  personal: "bg-warning/15 text-warning-foreground border-warning/30",
  career: "bg-accent/40 text-accent-foreground border-accent",
};
const unscheduled = ["تلخيص محاضرة الفيزياء", "حلّ ١٠ تمارين leetcode", "تحديث السيرة الذاتية"];

function Planner() {
  const [running, setRunning] = useState(false);
  const [time] = useState("٢٥:٠٠");
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
        <Card className="overflow-hidden p-0">
          <div className="grid grid-cols-7 border-b bg-muted/40 text-center text-xs font-semibold">
            {days.map((d, i) => (
              <div key={d} className={`p-3 ${i === 0 ? "" : "border-r"}`}>
                {d}
              </div>
            ))}
          </div>
          <div className="grid grid-cols-7">
            {days.map((_, di) => (
              <div key={di} className={`min-h-[320px] space-y-2 p-2 ${di === 0 ? "" : "border-r"}`}>
                {slots
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
          <Card className="gradient-primary p-6 text-center text-primary-foreground shadow-glow">
            <div className="text-xs opacity-90">مؤقّت بومودورو</div>
            <div className="my-3 text-5xl font-extrabold tracking-tight">{time}</div>
            <Button variant="secondary" onClick={() => setRunning(!running)} className="w-full">
              {running ? (
                <>
                  <Pause className="ms-1 h-4 w-4" /> إيقاف مؤقت
                </>
              ) : (
                <>
                  <Play className="ms-1 h-4 w-4" /> ابدأ الجلسة
                </>
              )}
            </Button>
            <div className="mt-3 text-xs opacity-80">جلسة ٢ من ٤ اليوم</div>
          </Card>

          <Card className="p-4">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-bold">مهام بدون موعد</h3>
              <Button size="icon" variant="ghost">
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            <div className="space-y-2">
              {unscheduled.map((t) => (
                <div key={t} className="rounded-lg border bg-muted/30 p-3 text-sm">
                  {t}
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="mb-2 text-sm font-bold">ملخّص اليوم</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">جلسات دراسة</span>
                <Badge>٣</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">وقت تعلّم</span>
                <Badge>٢س ٤٥د</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">استراحات</span>
                <Badge variant="secondary">٤</Badge>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
