import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { ArrowLeft, ArrowRight, CheckCircle2 } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/onboarding")({
  head: () => ({
    meta: [
      { title: "ابدأ رحلتك | بصمة+" },
      { name: "description", content: "أسئلة سريعة تساعدنا على تخصيص تجربتك في بصمة+." },
    ],
  }),
  component: Onboarding,
});

const steps = ["معلومات شخصية", "السلوك الرقمي", "الحالة النفسية", "أهدافك", "اهتماماتك"];
const goalOptions = [
  "تحسين المعدّل",
  "تعلّم البرمجة",
  "تعلّم الإنجليزية",
  "تقليل وقت الشاشة",
  "إيجاد عمل",
  "تحسين النوم",
];
const interestOptions = ["رياضة", "ألعاب", "تقنية", "موسيقى", "تصميم", "أعمال", "قراءة", "سفر"];

function Onboarding() {
  const [step, setStep] = useState(0);
  const [goals, setGoals] = useState<string[]>([]);
  const [interests, setInterests] = useState<string[]>([]);
  const [screenTime, setScreenTime] = useState([6]);
  const [sleep, setSleep] = useState([7]);
  const [mood, setMood] = useState([6]);

  const toggle = (arr: string[], set: (a: string[]) => void, v: string) =>
    set(arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v]);

  return (
    <div className="gradient-warm min-h-screen px-4 py-10">
      <div className="mx-auto max-w-2xl">
        <Link to="/" className="mb-6 flex items-center justify-center gap-2.5">
          <img src="/logo-icon.png" alt="بصمة+" className="h-10 w-10 object-contain" />
          <span className="text-xl font-extrabold">بصمة+</span>
        </Link>
        <div className="mb-6">
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="font-semibold">{steps[step]}</span>
            <span className="text-muted-foreground">
              الخطوة {step + 1} من {steps.length}
            </span>
          </div>
          <Progress value={((step + 1) / steps.length) * 100} />
        </div>
        <Card className="p-8 shadow-glow">
          {step === 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold">عرّفنا بك أكثر</h2>
              <p className="text-sm text-muted-foreground">نستخدم هذه المعلومات لتخصيص توصياتك.</p>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label>العمر</Label>
                  <Input type="number" placeholder="٢٠" />
                </div>
                <div className="space-y-2">
                  <Label>المدينة</Label>
                  <Input placeholder="عمّان" />
                </div>
              </div>
              <div className="space-y-2">
                <Label>التخصص</Label>
                <Input placeholder="هندسة برمجيات" />
              </div>
            </div>
          )}
          {step === 1 && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold">عاداتك الرقمية</h2>
              <div className="space-y-3">
                <Label>
                  متوسط وقت الشاشة يوميًا:{" "}
                  <span className="text-primary">{screenTime[0]} ساعة</span>
                </Label>
                <Slider
                  value={screenTime}
                  onValueChange={setScreenTime}
                  min={1}
                  max={16}
                  step={1}
                />
              </div>
              <div className="space-y-3">
                <Label>
                  ساعات النوم: <span className="text-primary">{sleep[0]} ساعة</span>
                </Label>
                <Slider value={sleep} onValueChange={setSleep} min={3} max={12} step={1} />
              </div>
              <p className="text-xs text-muted-foreground">
                نستخدم هذه القيم لحساب نقاط الصحة الرقمية.
              </p>
            </div>
          )}
          {step === 2 && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold">كيف حالك هذه الأيام؟</h2>
              <div className="space-y-3">
                <Label>
                  مستوى المزاج العام: <span className="text-primary">{mood[0]}/10</span>
                </Label>
                <Slider value={mood} onValueChange={setMood} min={1} max={10} step={1} />
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                {["متوتر", "هادئ", "متحمّس", "متعب"].map((m) => (
                  <button
                    key={m}
                    type="button"
                    className="rounded-lg border bg-card p-3 text-start transition hover:border-primary hover:bg-muted"
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>
          )}
          {step === 3 && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold">ما الذي تريد تحقيقه؟</h2>
              <p className="text-sm text-muted-foreground">اختر هدفًا واحدًا أو أكثر.</p>
              <div className="flex flex-wrap gap-2">
                {goalOptions.map((g) => (
                  <button key={g} type="button" onClick={() => toggle(goals, setGoals, g)}>
                    <Badge
                      variant={goals.includes(g) ? "default" : "outline"}
                      className="cursor-pointer px-3 py-1.5 text-sm"
                    >
                      {goals.includes(g) && <CheckCircle2 className="ms-1 h-3.5 w-3.5" />}
                      {g}
                    </Badge>
                  </button>
                ))}
              </div>
            </div>
          )}
          {step === 4 && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold">ما الذي يثير اهتمامك؟</h2>
              <div className="flex flex-wrap gap-2">
                {interestOptions.map((g) => (
                  <button key={g} type="button" onClick={() => toggle(interests, setInterests, g)}>
                    <Badge
                      variant={interests.includes(g) ? "default" : "outline"}
                      className="cursor-pointer px-3 py-1.5 text-sm"
                    >
                      {g}
                    </Badge>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="mt-8 flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={() => setStep((s) => Math.max(0, s - 1))}
              disabled={step === 0}
            >
              <ArrowRight className="ms-1 h-4 w-4" /> السابق
            </Button>
            {step < steps.length - 1 ? (
              <Button
                onClick={() => setStep((s) => s + 1)}
                className="gradient-primary shadow-soft"
              >
                التالي <ArrowLeft className="me-1 h-4 w-4" />
              </Button>
            ) : (
              <Button asChild className="gradient-primary shadow-glow">
                <Link to="/dashboard">أكمل وابدأ</Link>
              </Button>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
