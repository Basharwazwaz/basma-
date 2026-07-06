import { createFileRoute } from "@tanstack/react-router";
import { Link } from "@tanstack/react-router";
import { useState, useEffect, useRef } from "react";
import {
  Sparkles,
  Activity,
  Bot,
  CalendarDays,
  GraduationCap,
  Trophy,
  Shield,
  ArrowLeft,
  CheckCircle2,
  Download,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "بصمة+ | منصة التطوير الذاتي للشباب العربي" },
      {
        name: "description",
        content:
          "بصمة+ تساعدك على تحسين عاداتك الرقمية، تنظيم دراستك، ورسم مسارك المهني مع مدرّب ذكي يفهمك.",
      },
      { property: "og:title", content: "بصمة+ — رفيقك الذكي للنمو الشخصي" },
      {
        property: "og:description",
        content: "صحة رقمية، تخطيط دراسي، تتبّع مزاج، وأهداف ذكية في مكان واحد.",
      },
    ],
  }),
  component: Index,
});

function Index() {
  // ── PWA install banner ─────────────────────────────────────────────────────
  const deferredPromptRef = useRef<
    (Event & { prompt: () => Promise<void>; userChoice: Promise<{ outcome: string }> }) | null
  >(null);
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      deferredPromptRef.current = e as typeof deferredPromptRef.current;
      // Only show if not already dismissed
      if (!sessionStorage.getItem("pwa-banner-dismissed")) {
        setShowBanner(true);
      }
    };
    window.addEventListener("beforeinstallprompt", handler);
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  const handleInstall = async () => {
    if (!deferredPromptRef.current) return;
    await deferredPromptRef.current.prompt();
    const { outcome } = await deferredPromptRef.current.userChoice;
    if (outcome === "accepted") setShowBanner(false);
    deferredPromptRef.current = null;
  };

  const dismissBanner = () => {
    setShowBanner(false);
    sessionStorage.setItem("pwa-banner-dismissed", "1");
  };
  const features = [
    {
      icon: Activity,
      title: "الصحة الرقمية",
      desc: "حلّل وقت الشاشة، النوم، والتركيز لتعرف أين تذهب طاقتك.",
    },
    {
      icon: Bot,
      title: "المدرّب الذكي",
      desc: "محادثة ذكية تجيب أسئلتك في الدراسة، المهارات، والصحة النفسية.",
    },
    {
      icon: CalendarDays,
      title: "المخطّط الأسبوعي",
      desc: "خطة دراسة ذكية مع مؤقّت بومودورو وتذكيرات مرنة.",
    },
    { icon: GraduationCap, title: "مركز التعلّم", desc: "كورسات ومقالات ومسارات مهنية مختارة لك." },
    {
      icon: Trophy,
      title: "تحديات وإنجازات",
      desc: "ابنِ عاداتك من خلال تحديات يومية ومكافآت تحفّزك.",
    },
    {
      icon: Shield,
      title: "خصوصية كاملة",
      desc: "بياناتك ملكك. مشفّرة ولا تُشارك مع أي طرف ثالث.",
    },
  ];
  const steps = [
    { n: "١", t: "التسجيل", d: "أنشئ حسابك خلال دقيقة واحدة." },
    { n: "٢", t: "التقييم", d: "أجب على أسئلة قصيرة عن عاداتك وأهدافك." },
    { n: "٣", t: "رؤى ذكية", d: "يحلّل الذكاء الاصطناعي بياناتك ويضع خطتك." },
    { n: "٤", t: "تقارير أسبوعية", d: "تابع تقدّمك واكتشف عادات جديدة." },
  ];
  const testimonials = [
    {
      name: "ليلى م.",
      role: "طالبة هندسة",
      quote: "ساعدتني بصمة+ على تقليل وقت الشاشة ٣ ساعات يوميًا وتنظيم دراستي.",
    },
    {
      name: "كريم ع.",
      role: "خرّيج جديد",
      quote: "المدرّب الذكي وجّهني لمسار مطوّر واجهات وأصبح لدي خطة واضحة.",
    },
    {
      name: "نور ج.",
      role: "طالبة طب",
      quote: "تتبّع المزاج غيّر علاقتي بالامتحانات. أشعر بهدوء أكبر.",
    },
  ];
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-2.5">
            <img src="/logo-icon.png" alt="بصمة+" className="h-9 w-9 object-contain" />
            <span className="text-lg font-extrabold">بصمة+</span>
          </Link>
          <nav className="hidden items-center gap-6 text-sm md:flex">
            <a href="#features" className="text-muted-foreground transition hover:text-foreground">
              المميزات
            </a>
            <a href="#how" className="text-muted-foreground transition hover:text-foreground">
              كيف يعمل
            </a>
            <a href="#faq" className="text-muted-foreground transition hover:text-foreground">
              الأسئلة الشائعة
            </a>
          </nav>
          <div className="flex items-center gap-2">
            <Button variant="ghost" asChild>
              <Link to="/auth/login">دخول</Link>
            </Button>
            <Button asChild className="gradient-primary shadow-soft">
              <Link to="/auth/register">ابدأ الآن</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 -z-10 gradient-warm opacity-40" />
        <div className="mx-auto grid max-w-7xl items-center gap-10 px-4 py-16 sm:px-6 md:grid-cols-2 md:py-24 lg:px-8">
          <div className="space-y-6">
            <span className="inline-flex items-center gap-2 rounded-full border bg-card px-3 py-1 text-xs font-medium text-muted-foreground shadow-soft">
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              مدعوم بالذكاء الاصطناعي
            </span>
            <h1 className="text-4xl font-extrabold leading-tight sm:text-5xl lg:text-6xl">
              ابنِ نسختك الأفضل
              <br />
              <span className="bg-gradient-to-l from-primary to-accent-foreground bg-clip-text text-transparent">
                خطوة كل يوم.
              </span>
            </h1>
            <p className="max-w-lg text-lg text-muted-foreground">
              بصمة+ منصّة عربية تجمع الصحة الرقمية، التخطيط الدراسي، تتبّع المزاج، والإرشاد المهني
              في تجربة واحدة بسيطة وذكيّة.
            </p>
            <div className="flex flex-wrap gap-3">
              <Button size="lg" asChild className="gradient-primary shadow-glow">
                <Link to="/auth/register">
                  ابدأ مجانًا
                  <ArrowLeft className="mr-1 h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link to="/dashboard">جولة سريعة</Link>
              </Button>
            </div>
            <div className="flex flex-wrap items-center gap-4 pt-2 text-sm text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-success" /> بدون بطاقة ائتمان
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-success" /> خصوصية كاملة
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-success" /> عربي ١٠٠٪
              </span>
            </div>
          </div>
          <div className="relative">
            <div className="gradient-primary absolute -inset-4 -z-10 rounded-3xl opacity-20 blur-2xl" />
            <Card className="overflow-hidden p-0 shadow-glow">
              <div className="gradient-primary p-6 text-primary-foreground">
                <div className="text-xs opacity-80">مساء الخير، بشّار 👋</div>
                <div className="mt-1 text-2xl font-bold">صحتك الرقمية ٨٢٪</div>
                <div className="mt-1 text-sm opacity-90">+٧٪ مقارنة بالأسبوع الماضي</div>
              </div>
              <div className="grid grid-cols-3 divide-x divide-x-reverse">
                {[
                  { l: "وقت الشاشة", v: "٤س ١٢د" },
                  { l: "ساعات دراسة", v: "٣س ٤٥د" },
                  { l: "نوم", v: "٧س ٢٠د" },
                ].map((s) => (
                  <div key={s.l} className="p-4 text-center">
                    <div className="text-xs text-muted-foreground">{s.l}</div>
                    <div className="mt-1 text-base font-bold">{s.v}</div>
                  </div>
                ))}
              </div>
              <div className="space-y-2 p-4">
                {["إنجاز جلسة بومودورو", "قراءة ٢٠ دقيقة", "كتابة هدف اليوم"].map((t, i) => (
                  <div
                    key={t}
                    className="flex items-center gap-3 rounded-lg bg-muted/50 p-3 text-sm"
                  >
                    <CheckCircle2
                      className={i < 2 ? "h-5 w-5 text-success" : "h-5 w-5 text-muted-foreground"}
                    />
                    <span className={i < 2 ? "line-through text-muted-foreground" : ""}>{t}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="border-y bg-card">
        <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 md:py-24 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold sm:text-4xl">كل ما تحتاجه للنموّ في مكان واحد</h2>
            <p className="mt-3 text-muted-foreground">
              أدوات مصمّمة خصيصًا للشاب العربي لتجمع بين الصحة، التعلم، والإنتاجية.
            </p>
          </div>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((f) => {
              const Icon = f.icon;
              return (
                <Card key={f.title} className="group p-6 transition-all hover:shadow-glow">
                  <div className="gradient-warm mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl text-primary">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-lg font-bold">{f.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{f.desc}</p>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 md:py-24 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold sm:text-4xl">كيف تعمل بصمة+؟</h2>
          <p className="mt-3 text-muted-foreground">أربع خطوات بسيطة تفصلك عن خطّتك الشخصية.</p>
        </div>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {steps.map((s) => (
            <Card key={s.n} className="p-6">
              <div className="gradient-primary mb-4 inline-flex h-10 w-10 items-center justify-center rounded-full text-lg font-bold text-primary-foreground">
                {s.n}
              </div>
              <div className="text-lg font-bold">{s.t}</div>
              <p className="mt-2 text-sm text-muted-foreground">{s.d}</p>
            </Card>
          ))}
        </div>
      </section>

      {/* Testimonials */}
      <section className="bg-secondary/30">
        <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 md:py-20 lg:px-8">
          <h2 className="mb-10 text-center text-3xl font-bold sm:text-4xl">يتحدثون عن بصمة+</h2>
          <div className="grid gap-6 md:grid-cols-3">
            {testimonials.map((t) => (
              <Card key={t.name} className="p-6">
                <p className="text-foreground">«{t.quote}»</p>
                <div className="mt-4 flex items-center gap-3">
                  <div className="gradient-primary flex h-10 w-10 items-center justify-center rounded-full font-bold text-primary-foreground">
                    {t.name[0]}
                  </div>
                  <div>
                    <div className="text-sm font-semibold">{t.name}</div>
                    <div className="text-xs text-muted-foreground">{t.role}</div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="mx-auto max-w-3xl px-4 py-16 sm:px-6 md:py-24 lg:px-8">
        <h2 className="text-center text-3xl font-bold sm:text-4xl">الأسئلة الشائعة</h2>
        <Accordion type="single" collapsible className="mt-8">
          <AccordionItem value="1">
            <AccordionTrigger>هل بياناتي خاصّة؟</AccordionTrigger>
            <AccordionContent>
              نعم، جميع بياناتك مشفّرة ولا تُشارك مع أي طرف ثالث. أنت تتحكّم بكل شيء.
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="2">
            <AccordionTrigger>هل بصمة+ مجانية؟</AccordionTrigger>
            <AccordionContent>
              الخطة الأساسية مجانية بالكامل وتتضمّن جميع الميزات الأساسية.
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="3">
            <AccordionTrigger>كيف يعمل المدرّب الذكي؟</AccordionTrigger>
            <AccordionContent>
              يستخدم نماذج لغوية متقدّمة لفهم سياقك وأهدافك ويقدّم نصائح مخصّصة، مع احترام كامل
              لخصوصيّتك.
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="4">
            <AccordionTrigger>هل تدعم اللغة الإنجليزية؟</AccordionTrigger>
            <AccordionContent>
              حاليًا التطبيق متاح بالعربية بشكل كامل، ودعم الإنجليزية قادم قريبًا.
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-7xl px-4 pb-16 sm:px-6 lg:px-8">
        <Card className="gradient-primary overflow-hidden p-10 text-center text-primary-foreground shadow-glow md:p-16">
          <h2 className="text-3xl font-extrabold sm:text-4xl">ابدأ رحلتك اليوم</h2>
          <p className="mx-auto mt-3 max-w-xl opacity-90">
            انضمّ لآلاف الشباب الذين يبنون عاداتهم الجديدة مع بصمة+.
          </p>
          <Button size="lg" variant="secondary" asChild className="mt-6">
            <Link to="/auth/register">أنشئ حسابك المجاني</Link>
          </Button>
        </Card>
      </section>

      <footer className="border-t bg-card">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 py-8 text-sm text-muted-foreground sm:flex-row sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <span>© ٢٠٢٦ بصمة+ — جميع الحقوق محفوظة</span>
          </div>
          <div className="flex gap-5">
            <a href="#" className="hover:text-foreground">
              الخصوصية
            </a>
            <a href="#" className="hover:text-foreground">
              الشروط
            </a>
            <a href="#" className="hover:text-foreground">
              تواصل
            </a>
          </div>
        </div>
      </footer>
      {/* PWA Install Banner */}
      {showBanner && (
        <div
          className="fixed bottom-0 inset-x-0 z-50 flex items-center justify-between gap-3 border-t bg-card/95 px-4 py-3 shadow-glow backdrop-blur-md sm:px-6 animate-in slide-in-from-bottom duration-300"
          role="banner"
        >
          <div className="flex items-center gap-3">
            <div className="gradient-primary flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-primary-foreground">
              <Download className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-bold">أضف بصمة+ إلى شاشتك الرئيسية</p>
              <p className="text-xs text-muted-foreground">تجربة أسرع وأفضل بدون متصفح</p>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Button
              size="sm"
              className="gradient-primary shadow-soft text-xs"
              onClick={handleInstall}
            >
              تثبيت
            </Button>
            <Button
              size="icon"
              variant="ghost"
              className="h-8 w-8 text-muted-foreground"
              onClick={dismissBanner}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
