import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import {
  Calendar,
  TrendingUp,
  Smartphone,
  BookOpen,
  Heart,
  Target,
  Sparkles,
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  TrendingDown,
  Award,
} from "lucide-react";

export const Route = createFileRoute("/weekly-report")({
  head: () => ({ meta: [{ title: "التقرير الأسبوعي | بصمة+" }] }),
  component: WeeklyReport,
});

const METRICS = [
  { t: "وقت الشاشة", v: "٤.٢ س/يوم", trend: -12, icon: Smartphone, color: "text-primary" },
  { t: "ساعات الدراسة", v: "١٨ ساعة", trend: +15, icon: BookOpen, color: "text-info" },
  { t: "متوسط المزاج", v: "٧.٨/١٠", trend: +5, icon: Heart, color: "text-success" },
  { t: "الأهداف المنجزة", v: "٣ أهداف", trend: 0, icon: Target, color: "text-warning" },
];

const INSIGHTS = [
  {
    t: "أداء متميز في التعلّم",
    d: "لقد زادت ساعات دراستك بنسبة ١٥٪ مقارنة بالأسبوع الماضي، مع التزام عالي بجلسات بومودورو.",
    tag: "تعلّم",
    tagColor: "bg-info/10 text-info hover:bg-info/20",
  },
  {
    t: "تحسّن في الصحة الرقمية",
    d: "نجحت في خفض وقت استخدام التيك توك بعد الـ ٩ مساءً، مما انعكس إيجابياً على جودة نومك.",
    tag: "صحة رقمية",
    tagColor: "bg-primary/10 text-primary hover:bg-primary/20",
  },
  {
    t: "ارتباط المزاج بالرياضة",
    d: "لاحظنا أن أيام تسجيلك لمزاج «ممتاز» تتزامن مع الأيام التي مارست فيها الرياضة لمدة ٢٠ دقيقة.",
    tag: "رفاه",
    tagColor: "bg-success/10 text-success hover:bg-success/20",
  },
];

const RECOMMENDATIONS = [
  {
    t: "تحدي القراءة المتقدم",
    d: "معدل قراءتك ممتاز، ننصحك بالانضمام لتحدي قراءة كتاب في أسبوعين.",
    a: "انضم للتحدي",
  },
  {
    t: "ضبط وقت الشاشة الصباحي",
    d: "لاحظنا استخدامك للهاتف فور الاستيقاظ. حاول تأجيل ذلك لمدة ٣٠ دقيقة.",
    a: "إعداد تنبيه",
  },
  {
    t: "مراجعة شاملة للرياضيات",
    d: "اقتربت فترة الامتحانات، ابدأ بتلخيص مادة الرياضيات غداً.",
    a: "أضف للمخطط",
  },
];

const COMPARISON_DATA = [
  { name: "السبت", lastWeek: 6.5, thisWeek: 5.2 },
  { name: "الأحد", lastWeek: 5.8, thisWeek: 4.5 },
  { name: "الاثنين", lastWeek: 5.2, thisWeek: 4.8 },
  { name: "الثلاثاء", lastWeek: 6.0, thisWeek: 5.1 },
  { name: "الأربعاء", lastWeek: 5.5, thisWeek: 3.9 },
  { name: "الخميس", lastWeek: 4.8, thisWeek: 4.5 },
  { name: "الجمعة", lastWeek: 5.0, thisWeek: 4.2 },
];

function WeeklyReport() {
  return (
    <AppShell
      title="التقرير الأسبوعي"
      subtitle="تحليل شامل لأدائك وعاداتك خلال الأيام السبعة الماضية."
    >
      {/* Header Card */}
      <Card className="gradient-primary mb-6 p-6 text-primary-foreground shadow-glow">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2 opacity-90">
              <Calendar className="h-4 w-4" />
              <span className="text-sm font-medium">٢٢ - ٢٨ أكتوبر ٢٠٢٥</span>
            </div>
            <h2 className="text-2xl font-bold">أسبوع ممتاز، استمر! 🚀</h2>
            <p className="mt-1 opacity-80 text-sm">
              معدل أدائك العام ارتفع بشكل ملحوظ مقارنة بالأسبوع الماضي.
            </p>
          </div>

          <div className="flex items-center gap-4 bg-white/10 rounded-2xl p-4 backdrop-blur-sm shrink-0">
            <div className="text-center">
              <div className="text-3xl font-black tabular-nums">٨٤</div>
              <div className="text-[10px] opacity-80 uppercase tracking-widest mt-1">النقاط</div>
            </div>
            <div className="h-10 w-px bg-white/20" />
            <div className="flex flex-col items-center">
              <Badge variant="secondary" className="bg-success text-success-foreground border-none">
                <TrendingUp className="h-3 w-3 me-1" /> +٨٪
              </Badge>
              <div className="text-[10px] opacity-80 uppercase tracking-widest mt-1.5">النمو</div>
            </div>
          </div>
        </div>
      </Card>

      <div className="grid gap-6 xl:grid-cols-[1fr_320px]">
        {/* Main Content Column */}
        <div className="space-y-6">
          {/* Section 1: Metrics summary */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Award className="h-5 w-5 text-primary" />
              <h3 className="text-lg font-bold">ملخّص الأسبوع</h3>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              {METRICS.map((m) => {
                const Icon = m.icon;
                const isPositive = m.trend > 0;
                const isNegative = m.trend < 0;
                const isNeutral = m.trend === 0;

                // For screen time, negative trend is "good"
                const isGoodTrend = m.t === "وقت الشاشة" ? isNegative : isPositive;

                return (
                  <Card key={m.t} className="p-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className={`h-10 w-10 flex items-center justify-center rounded-xl bg-muted ${m.color}`}
                      >
                        <Icon className="h-5 w-5" />
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">{m.t}</div>
                        <div className="text-xl font-bold">{m.v}</div>
                      </div>
                    </div>

                    {!isNeutral && (
                      <Badge
                        variant="secondary"
                        className={
                          isGoodTrend
                            ? "text-success bg-success/10"
                            : "text-destructive bg-destructive/10"
                        }
                      >
                        {isPositive ? (
                          <TrendingUp className="h-3 w-3 me-1" />
                        ) : (
                          <TrendingDown className="h-3 w-3 me-1" />
                        )}
                        {Math.abs(m.trend)}٪
                      </Badge>
                    )}
                    {isNeutral && (
                      <Badge variant="outline" className="text-muted-foreground">
                        ثابت
                      </Badge>
                    )}
                  </Card>
                );
              })}
            </div>
          </section>

          {/* Section 4: Chart */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="h-5 w-5 text-primary" />
              <h3 className="text-lg font-bold">مقارنة وقت الشاشة (ساعة/يوم)</h3>
            </div>
            <Card className="p-5 h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={COMPARISON_DATA}
                  margin={{ top: 10, right: 0, left: -20, bottom: 0 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="hsl(var(--border))"
                    vertical={false}
                    opacity={0.4}
                  />
                  <XAxis
                    dataKey="name"
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={12}
                    tickMargin={10}
                  />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      background: "var(--card)",
                      border: "1px solid var(--border)",
                      borderRadius: 8,
                      direction: "rtl",
                    }}
                    cursor={{ fill: "hsl(var(--muted)/0.4)" }}
                  />
                  <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
                  <Bar
                    dataKey="lastWeek"
                    name="الأسبوع الماضي"
                    fill="hsl(var(--muted-foreground)/0.3)"
                    radius={[4, 4, 0, 0]}
                  />
                  <Bar
                    dataKey="thisWeek"
                    name="هذا الأسبوع"
                    fill="var(--primary)"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </section>
        </div>

        {/* Sidebar Column */}
        <div className="space-y-6">
          {/* Section 2: Insights */}
          <section>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-warning-foreground" />
                <h3 className="text-lg font-bold">رؤى ذكية</h3>
              </div>
            </div>
            <div className="space-y-3">
              {INSIGHTS.map((insight, idx) => (
                <Card
                  key={idx}
                  className="p-4 border-l-4 border-l-primary hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-bold text-sm">{insight.t}</h4>
                    <Badge variant="secondary" className={`text-[10px] ${insight.tagColor}`}>
                      {insight.tag}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">{insight.d}</p>
                </Card>
              ))}
            </div>
          </section>

          {/* Section 3: Recommendations */}
          <section>
            <div className="flex items-center gap-2 mb-4 mt-2">
              <Target className="h-5 w-5 text-primary" />
              <h3 className="text-lg font-bold">توصيات الأسبوع القادم</h3>
            </div>
            <Card className="p-1 overflow-hidden">
              <div className="divide-y">
                {RECOMMENDATIONS.map((rec, idx) => (
                  <div key={idx} className="p-4 hover:bg-muted/30 transition-colors">
                    <h4 className="font-bold text-sm mb-1">{rec.t}</h4>
                    <p className="text-xs text-muted-foreground mb-3">{rec.d}</p>
                    <Button size="sm" variant="outline" className="w-full text-xs h-8">
                      {rec.a}
                    </Button>
                  </div>
                ))}
              </div>
            </Card>
          </section>
        </div>
      </div>
    </AppShell>
  );
}
