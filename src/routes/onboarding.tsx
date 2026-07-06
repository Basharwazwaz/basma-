import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, ArrowRight, CheckCircle2, Save, HelpCircle, Loader2 } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { toast } from "sonner";
import { apiSubmitOnboarding, ApiError } from "@/lib/api";
import { PROFILE_QUERY_KEY } from "@/hooks/use-auth";

export const Route = createFileRoute("/onboarding")({
  head: () => ({
    meta: [
      { title: "ابدأ رحلتك | بصمة+" },
      { name: "description", content: "أسئلة سريعة تساعدنا على تخصيص تجربتك في بصمة+." },
    ],
  }),
  component: Onboarding,
});

const STORAGE_KEY = "basma-onboarding";
const PROFILE_KEY = "basma-user-profile";

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

interface OnboardingData {
  step: number;
  age: string;
  city: string;
  major: string;
  screenTime: number;
  socialMediaHours: number;
  sleep: number;
  mood: number;
  stress: number;
  moodState: string;
  goals: string[];
  interests: string[];
}

const DEFAULT_DATA: OnboardingData = {
  step: 0,
  age: "",
  city: "",
  major: "",
  screenTime: 6,
  socialMediaHours: 3,
  sleep: 7,
  mood: 6,
  stress: 5,
  moodState: "",
  goals: [],
  interests: [],
};

function loadFromStorage(): OnboardingData {
  if (typeof window === "undefined") return DEFAULT_DATA;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_DATA;
    return { ...DEFAULT_DATA, ...JSON.parse(raw) };
  } catch {
    return DEFAULT_DATA;
  }
}

function saveToStorage(data: OnboardingData) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (err) {
    console.error("Failed to write to localStorage:", err);
  }
}

function LabelWithTip({ label, tip }: { label: string; tip: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <span>{label}</span>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            type="button"
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <HelpCircle className="h-3.5 w-3.5" />
          </button>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-56 text-right">
          {tip}
        </TooltipContent>
      </Tooltip>
    </div>
  );
}

function Onboarding() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [data, setData] = useState<OnboardingData>(DEFAULT_DATA);

  // Restore from localStorage on mount
  useEffect(() => {
    const saved = loadFromStorage();
    setData(saved);
  }, []);

  // Persist to localStorage on every change (draft fallback)
  useEffect(() => {
    saveToStorage(data);
  }, [data]);

  const set = <K extends keyof OnboardingData>(key: K, value: OnboardingData[K]) =>
    setData((prev) => ({ ...prev, [key]: value }));

  const toggle = (key: "goals" | "interests", value: string) =>
    setData((prev) => ({
      ...prev,
      [key]: prev[key].includes(value)
        ? prev[key].filter((x) => x !== value)
        : [...prev[key], value],
    }));

  const next = () =>
    setData((prev) => ({ ...prev, step: Math.min(steps.length - 1, prev.step + 1) }));
  const back = () => setData((prev) => ({ ...prev, step: Math.max(0, prev.step - 1) }));

  const saveAndExit = () => {
    saveToStorage(data);
    toast("تم الحفظ ✓", { description: "يمكنك إكمال الإعداد لاحقاً من الملف الشخصي." });
    navigate({ to: "/dashboard" });
  };

  // ── Onboarding API mutation ────────────────────────────────────
  const onboardMutation = useMutation({
    mutationFn: () =>
      apiSubmitOnboarding({
        personal: {
          age: data.age ? Number(data.age) : undefined,
          city: data.city || undefined,
          major: data.major || undefined,
        },
        digital: {
          screen_time_hours: data.screenTime,
          social_media_hours: data.socialMediaHours,
          sleep_hours: data.sleep,
        },
        mental: {
          mood_score: data.mood,
          stress_score: data.stress,
          mood_state: data.moodState || undefined,
        },
        plan: {
          goals: data.goals,
          interests: data.interests,
        },
      }),
    onSuccess: () => {
      // Clear draft from localStorage
      try {
        localStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem(PROFILE_KEY);
      } catch (err) {
        console.error(err);
      }
      // Invalidate profile cache so profile.tsx shows fresh data
      queryClient.invalidateQueries({ queryKey: PROFILE_QUERY_KEY });
      toast.success("مرحباً! تم إنشاء ملفك الشخصي 🎉", {
        description: "بصمة+ جاهزة لمساعدتك. لنبدأ!",
        duration: 4000,
      });
      navigate({ to: "/dashboard" });
    },
    onError: (err) => {
      const msg =
        err instanceof ApiError ? err.message : "حدث خطأ أثناء حفظ بياناتك. حاول مرة أخرى.";
      toast.error("فشل حفظ الملف الشخصي", { description: msg });
    },
  });

  const finish = () => {
    if (data.goals.length === 0) {
      toast.warning("اختر هدفاً واحداً على الأقل قبل المتابعة.");
      return;
    }
    onboardMutation.mutate();
  };

  const { step } = data;

  return (
    <TooltipProvider delayDuration={200}>
      <div className="gradient-warm min-h-screen px-4 py-10">
        <div className="mx-auto max-w-2xl">
          {/* Logo */}
          <div className="mb-6 flex items-center justify-center gap-2.5">
            <img src="/logo-icon.png" alt="بصمة+" className="h-10 w-10 object-contain" />
            <span className="text-xl font-extrabold">بصمة+</span>
          </div>

          {/* Progress bar */}
          <div className="mb-6">
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="font-semibold">{steps[step]}</span>
              <span className="text-muted-foreground">
                الخطوة {step + 1} من {steps.length}
              </span>
            </div>
            <Progress
              value={((step + 1) / steps.length) * 100}
              className="transition-all duration-500"
            />
          </div>

          <Card className="p-8 shadow-glow">
            {/* ── Step 0: Personal Info ── */}
            {step === 0 && (
              <div className="space-y-5">
                <div>
                  <h2 className="text-xl font-bold">عرّفنا بك أكثر</h2>
                  <p className="mt-1 text-sm text-muted-foreground">
                    نستخدم هذه المعلومات لتخصيص توصياتك — لن تُشارك مع أي طرف ثالث.
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <Label className="flex items-center gap-1.5" htmlFor="ob-age">
                      <LabelWithTip
                        label="العمر"
                        tip="يساعدنا عمرك في اقتراح تحديات ومحتوى مناسب."
                      />
                    </Label>
                    <Input
                      id="ob-age"
                      type="number"
                      placeholder="٢٠"
                      value={data.age}
                      onChange={(e) => set("age", e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="ob-city">المدينة</Label>
                    <Input
                      id="ob-city"
                      placeholder="عمّان"
                      value={data.city}
                      onChange={(e) => set("city", e.target.value)}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="ob-major">
                    <LabelWithTip
                      label="التخصص"
                      tip="يساعدنا في تخصيص الكورسات والمسارات المهنية لك."
                    />
                  </Label>
                  <Input
                    id="ob-major"
                    placeholder="هندسة برمجيات"
                    value={data.major}
                    onChange={(e) => set("major", e.target.value)}
                  />
                </div>
              </div>
            )}

            {/* ── Step 1: Digital Behaviour ── */}
            {step === 1 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-bold">عاداتك الرقمية</h2>
                  <p className="mt-1 text-sm text-muted-foreground">
                    هذه القيم تُحسب لصالحك فقط لحساب نقاط الصحة الرقمية.
                  </p>
                </div>

                <div className="space-y-3">
                  <Label className="flex items-center gap-1.5">
                    <LabelWithTip
                      label={`متوسط وقت الشاشة يوميًا: ${data.screenTime} ساعة`}
                      tip="إجمالي الوقت على كل الشاشات. نستخدمه لرسم مؤشر صحتك الرقمية."
                    />
                  </Label>
                  <Slider
                    value={[data.screenTime]}
                    onValueChange={([v]) => set("screenTime", v)}
                    min={1}
                    max={16}
                    step={1}
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>١ ساعة</span>
                    <span>١٦ ساعة</span>
                  </div>
                </div>

                <div className="space-y-3">
                  <Label className="flex items-center gap-1.5">
                    <LabelWithTip
                      label={`ساعات التواصل الاجتماعي: ${data.socialMediaHours} ساعة`}
                      tip="يشمل إنستقرام، تيك توك، تويتر، وسناب شات. يساعدنا في تحديد تحديات مناسبة."
                    />
                  </Label>
                  <Slider
                    value={[data.socialMediaHours]}
                    onValueChange={([v]) => set("socialMediaHours", v)}
                    min={0}
                    max={10}
                    step={0.5}
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>صفر</span>
                    <span>١٠ ساعات</span>
                  </div>
                </div>

                <div className="space-y-3">
                  <Label>
                    <LabelWithTip
                      label={`ساعات النوم: ${data.sleep} ساعة`}
                      tip="النوم الجيد له تأثير مباشر على تركيزك وإنتاجيتك."
                    />
                  </Label>
                  <Slider
                    value={[data.sleep]}
                    onValueChange={([v]) => set("sleep", v)}
                    min={3}
                    max={12}
                    step={1}
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>٣ ساعات</span>
                    <span>١٢ ساعة</span>
                  </div>
                </div>
              </div>
            )}

            {/* ── Step 2: Mental State ── */}
            {step === 2 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-bold">كيف حالك هذه الأيام؟</h2>
                  <p className="mt-1 text-sm text-muted-foreground">
                    إجاباتك تساعدنا في تقديم دعم أفضل — لا يراها أحد غيرك.
                  </p>
                </div>

                <div className="space-y-3">
                  <Label>
                    <LabelWithTip
                      label={`مستوى المزاج العام: ${data.mood}/10`}
                      tip="كيف تشعر بشكل عام هذه الأيام؟ سنتابع هذا مع الوقت لنرى تطورك."
                    />
                  </Label>
                  <Slider
                    value={[data.mood]}
                    onValueChange={([v]) => set("mood", v)}
                    min={1}
                    max={10}
                    step={1}
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>صعب جداً 😔</span>
                    <span>ممتاز 🤩</span>
                  </div>
                </div>

                <div className="space-y-3">
                  <Label>
                    <LabelWithTip
                      label={`مستوى الضغط: ${data.stress}/10`}
                      tip="مستوى الضغط النفسي والأكاديمي الذي تشعر به. نستخدمه لاقتراح تمارين الاسترخاء."
                    />
                  </Label>
                  <Slider
                    value={[data.stress]}
                    onValueChange={([v]) => set("stress", v)}
                    min={1}
                    max={10}
                    step={1}
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>هادئ تماماً</span>
                    <span>ضغط شديد</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="text-sm font-medium">حالتي الآن</Label>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    {["متوتر", "هادئ", "متحمّس", "متعب"].map((m) => (
                      <button
                        key={m}
                        type="button"
                        onClick={() => set("moodState", data.moodState === m ? "" : m)}
                        className={`rounded-lg border p-3 text-start transition-all hover:border-primary hover:bg-muted ${
                          data.moodState === m
                            ? "border-primary bg-primary/10 font-semibold"
                            : "bg-card"
                        }`}
                      >
                        {m}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ── Step 3: Goals ── */}
            {step === 3 && (
              <div className="space-y-5">
                <div>
                  <h2 className="text-xl font-bold">ما الذي تريد تحقيقه؟</h2>
                  <p className="mt-1 text-sm text-muted-foreground">
                    اختر هدفاً واحداً أو أكثر — سنبني خطتك حوله.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {goalOptions.map((g) => (
                    <button key={g} type="button" onClick={() => toggle("goals", g)}>
                      <Badge
                        variant={data.goals.includes(g) ? "default" : "outline"}
                        className="cursor-pointer px-3 py-1.5 text-sm transition-all hover:shadow-sm"
                      >
                        {data.goals.includes(g) && <CheckCircle2 className="ms-1 h-3.5 w-3.5" />}
                        {g}
                      </Badge>
                    </button>
                  ))}
                </div>
                {data.goals.length === 0 && (
                  <p className="text-xs text-muted-foreground">
                    اختر هدفاً واحداً على الأقل للمتابعة.
                  </p>
                )}
              </div>
            )}

            {/* ── Step 4: Interests ── */}
            {step === 4 && (
              <div className="space-y-5">
                <div>
                  <h2 className="text-xl font-bold">ما الذي يثير اهتمامك؟</h2>
                  <p className="mt-1 text-sm text-muted-foreground">
                    نستخدم اهتماماتك لاقتراح كورسات وتحديات تناسبك.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {interestOptions.map((g) => (
                    <button key={g} type="button" onClick={() => toggle("interests", g)}>
                      <Badge
                        variant={data.interests.includes(g) ? "default" : "outline"}
                        className="cursor-pointer px-3 py-1.5 text-sm transition-all hover:shadow-sm"
                      >
                        {g}
                      </Badge>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Navigation row */}
            <div className="mt-8 flex items-center justify-between gap-2">
              <Button variant="ghost" onClick={back} disabled={step === 0}>
                <ArrowRight className="ms-1 h-4 w-4" /> السابق
              </Button>

              <Button
                variant="ghost"
                size="sm"
                className="text-muted-foreground text-xs"
                onClick={saveAndExit}
              >
                <Save className="ms-1 h-3.5 w-3.5" />
                حفظ وإكمال لاحقاً
              </Button>

              {step < steps.length - 1 ? (
                <Button onClick={next} className="gradient-primary shadow-soft">
                  التالي <ArrowLeft className="me-1 h-4 w-4" />
                </Button>
              ) : (
                <Button
                  onClick={finish}
                  className="gradient-primary shadow-glow"
                  disabled={onboardMutation.isPending}
                >
                  {onboardMutation.isPending ? (
                    <>
                      <Loader2 className="me-1 h-4 w-4 animate-spin" />
                      جارٍ الحفظ…
                    </>
                  ) : (
                    "أكمل وابدأ 🚀"
                  )}
                </Button>
              )}
            </div>
          </Card>
        </div>
      </div>
    </TooltipProvider>
  );
}
