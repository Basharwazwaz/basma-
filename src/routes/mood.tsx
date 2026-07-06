import { createFileRoute } from "@tanstack/react-router";
import { useState, useRef } from "react";
import { Sparkles, Flame, CheckCircle2 } from "lucide-react";
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
  const [isSaved, setIsSaved] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);
  const btnRef = useRef<HTMLButtonElement>(null);

  const handleSave = () => {
    setIsSaved(true);
    setShowConfetti(true);
    setTimeout(() => setShowConfetti(false), 1000);
  };

  return (
    <AppShell title="تتبّع المزاج" subtitle="افهم مشاعرك وعلاقتها بعاداتك.">
      <Card className="mb-6 p-6 relative">
        <h2 className="text-lg font-bold">كيف تشعر اليوم؟</h2>
        <div className="mt-5 flex flex-wrap justify-around gap-3">
          {emojis.map((m) => (
            <button
              key={m.v}
              onClick={() => {
                setSel(m.v);
                setIsSaved(false);
              }}
              className={`flex flex-col items-center gap-2 rounded-2xl border-2 px-4 py-3 transition-transform duration-200 hover:scale-110 ${sel === m.v ? "border-primary bg-primary/10 shadow-glow scale-110" : "border-transparent bg-muted/40 hover:bg-muted"}`}
            >
              <span className="text-4xl">{m.e}</span>
              <span className="text-xs font-semibold">{m.l}</span>
            </button>
          ))}
        </div>
        <div className="mt-6">
          <Textarea placeholder="اكتب ما يدور في بالك (اختياري)..." rows={3} />
        </div>
        <div className="mt-4 relative">
          <Button
            ref={btnRef}
            onClick={handleSave}
            disabled={isSaved}
            className={`gradient-primary shadow-soft transition-all ${isSaved ? "bg-success hover:bg-success text-success-foreground" : ""}`}
          >
            {isSaved ? (
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

      <div className="mt-6 grid gap-6 sm:grid-cols-2">
        <Card className="p-5 border-l-4 border-l-warning bg-warning/5">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="h-5 w-5 text-warning-foreground" />
            <h3 className="font-bold">رؤية ذكية</h3>
          </div>
          <p className="text-sm text-muted-foreground">
            مزاجك يكون في أفضل حالاته أيام الخميس والجمعة، ويتزامن ذلك مع انخفاض ملحوظ في وقت
            الشاشة!
          </p>
        </Card>

        <Card className="p-5 flex items-center justify-between">
          <div>
            <h3 className="font-bold">سلسلة الأيام</h3>
            <p className="text-sm text-muted-foreground mt-1">سجّلت مزاجك ٥ أيام متتالية 🔥</p>
          </div>
          <div className="flex items-center justify-center h-14 w-14 rounded-full bg-accent/20 text-accent-foreground font-black text-2xl">
            ٥
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
