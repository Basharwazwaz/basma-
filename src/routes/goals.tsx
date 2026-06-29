import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Plus, Target, CheckCircle2, Calendar } from "lucide-react";

export const Route = createFileRoute("/goals")({
  head: () => ({ meta: [{ title: "الأهداف | بصمة+" }] }),
  component: Goals,
});

const active = [
  {
    t: "تقليل وقت الشاشة إلى ٤س يوميًا",
    cur: 4.8,
    tgt: 4,
    unit: "س",
    deadline: "٢٨ فبراير",
    p: 60,
  },
  { t: "تعلّم البايثون", cur: 18, tgt: 40, unit: "ساعة", deadline: "٣١ مارس", p: 45 },
  { t: "تحسين المعدّل إلى ٨٥٪", cur: 81, tgt: 85, unit: "٪", deadline: "نهاية الفصل", p: 70 },
  { t: "قراءة ١٠ كتب هذا العام", cur: 4, tgt: 10, unit: "كتاب", deadline: "ديسمبر", p: 40 },
];
const done = [
  { t: "تعلّم أساسيات Git", date: "نوفمبر ٢٠٢٥" },
  { t: "روتين نوم منتظم لشهر", date: "أكتوبر ٢٠٢٥" },
];

function Goals() {
  return (
    <AppShell title="الأهداف" subtitle="حدّد أهدافك وتابع تقدّمك خطوة بخطوة.">
      <div className="grid gap-6 xl:grid-cols-[1fr_320px]">
        <div className="space-y-4">
          {active.map((g) => (
            <Card key={g.t} className="p-5">
              <div className="mb-3 flex items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                  <div className="gradient-warm flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-primary">
                    <Target className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-bold">{g.t}</h3>
                    <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                      <Calendar className="h-3.5 w-3.5" />
                      <span>الموعد: {g.deadline}</span>
                    </div>
                  </div>
                </div>
                <Badge variant="secondary">{g.p}٪</Badge>
              </div>
              <Progress value={g.p} className="h-2" />
              <div className="mt-2 flex justify-between text-sm">
                <span className="text-muted-foreground">
                  الحالي: {g.cur} {g.unit}
                </span>
                <span className="font-semibold">
                  الهدف: {g.tgt} {g.unit}
                </span>
              </div>
            </Card>
          ))}

          <Card className="p-5">
            <h3 className="mb-4 flex items-center gap-2 font-bold">
              <CheckCircle2 className="h-5 w-5 text-success" /> أهداف مُحقّقة
            </h3>
            <div className="space-y-2">
              {done.map((d) => (
                <div
                  key={d.t}
                  className="flex items-center justify-between rounded-lg border bg-muted/30 p-3 text-sm"
                >
                  <span>{d.t}</span>
                  <span className="text-xs text-muted-foreground">{d.date}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <Card className="h-fit p-5 shadow-soft">
          <h3 className="mb-4 flex items-center gap-2 font-bold">
            <Plus className="h-4 w-4" /> هدف جديد
          </h3>
          <form className="space-y-3">
            <div className="space-y-1.5">
              <Label>العنوان</Label>
              <Input placeholder="مثل: قراءة ٢٠ دقيقة يوميًا" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>القيمة المستهدفة</Label>
                <Input type="number" placeholder="٢٠" />
              </div>
              <div className="space-y-1.5">
                <Label>الوحدة</Label>
                <Input placeholder="دقيقة" />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label>الموعد النهائي</Label>
              <Input type="date" />
            </div>
            <Button className="w-full gradient-primary shadow-soft">أضف الهدف</Button>
          </form>
        </Card>
      </div>
    </AppShell>
  );
}
