import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
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

export const Route = createFileRoute("/mood")({
  head: () => ({ meta: [{ title: "تتبّع المزاج | بصمة+" }] }),
  component: Mood,
});

const emojis = [
  { e: "😫", l: "سيّئ جدًا", v: 1 },
  { e: "😔", l: "متعب", v: 3 },
  { e: "😐", l: "عادي", v: 5 },
  { e: "🙂", l: "جيّد", v: 7 },
  { e: "😄", l: "ممتاز", v: 10 },
];
const history = [
  { d: "س", v: 6 },
  { d: "ح", v: 7 },
  { d: "ن", v: 5 },
  { d: "ث", v: 8 },
  { d: "ر", v: 7 },
  { d: "خ", v: 8 },
  { d: "ج", v: 9 },
];
const corr = [
  { d: "س", mood: 6, study: 3 },
  { d: "ح", mood: 7, study: 4 },
  { d: "ن", mood: 5, study: 2 },
  { d: "ث", mood: 8, study: 5 },
  { d: "ر", mood: 7, study: 4 },
  { d: "خ", mood: 8, study: 6 },
  { d: "ج", mood: 9, study: 5 },
];

function Mood() {
  const [sel, setSel] = useState<number | null>(7);
  return (
    <AppShell title="تتبّع المزاج" subtitle="افهم مشاعرك وعلاقتها بعاداتك.">
      <Card className="mb-6 p-6">
        <h2 className="text-lg font-bold">كيف تشعر اليوم؟</h2>
        <div className="mt-5 flex flex-wrap justify-around gap-3">
          {emojis.map((m) => (
            <button
              key={m.v}
              onClick={() => setSel(m.v)}
              className={`flex flex-col items-center gap-2 rounded-2xl border-2 px-4 py-3 transition-all ${sel === m.v ? "border-primary bg-primary/10 shadow-glow scale-105" : "border-transparent bg-muted/40 hover:bg-muted"}`}
            >
              <span className="text-4xl">{m.e}</span>
              <span className="text-xs font-semibold">{m.l}</span>
            </button>
          ))}
        </div>
        <div className="mt-6">
          <Textarea placeholder="اكتب ما يدور في بالك (اختياري)..." rows={3} />
        </div>
        <Button className="mt-4 gradient-primary shadow-soft">حفظ مزاج اليوم</Button>
      </Card>

      {sel && sel >= 7 && (
        <Card className="mb-6 bg-success/10 p-4 text-success-foreground">
          <strong className="text-success">رائع!</strong> يومك يبدو إيجابيًا. حاول الحفاظ على هذا
          الإيقاع بنوم منتظم وتعرّض كافٍ للشمس.
        </Card>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="p-5">
          <h3 className="mb-4 font-bold">مزاجك خلال الأسبوع</h3>
          <div className="h-64">
            <ResponsiveContainer>
              <LineChart data={history}>
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
          </div>
        </Card>
        <Card className="p-5">
          <h3 className="mb-4 font-bold">المزاج مقابل ساعات الدراسة</h3>
          <div className="h-64">
            <ResponsiveContainer>
              <BarChart data={corr}>
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
    </AppShell>
  );
}
