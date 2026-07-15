import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
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
  Heart,
  Target,
  Sparkles,
  TrendingDown,
  Award,
  Loader2,
} from "lucide-react";
import { apiGetWeeklyReports, apiGenerateWeeklyReport, type WeeklyReportData } from "@/lib/api";
import { toast } from "sonner";

export const Route = createFileRoute("/weekly-report")({
  head: () => ({ meta: [{ title: "التقرير الأسبوعي | بصمة+" }] }),
  component: WeeklyReport,
});

function WeeklyReport() {
  const queryClient = useQueryClient();

  const {
    data: reports,
    isLoading,
    error,
  } = useQuery<WeeklyReportData[], Error>({
    queryKey: ["weekly-reports"],
    queryFn: apiGetWeeklyReports,
  });

  const generateMutation = useMutation({
    mutationFn: apiGenerateWeeklyReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["weekly-reports"] });
      toast.success("تم إنشاء التقرير الأسبوعي!");
    },
    onError: () => {
      toast.error("فشل إنشاء التقرير");
    },
  });

  const latestReport = reports?.[0] ?? null;
  const metrics = (latestReport?.metrics_summary as Record<string, unknown>) ?? {};
  const screenTimeAvg = (metrics.screen_time_avg_hrs as number) ?? 0;
  const moodAvg = (metrics.mood_avg as number) ?? 0;
  const completedTasks = (metrics.completed_tasks as number) ?? 0;
  const totalTasks = (metrics.total_tasks as number) ?? 0;
  const completedGoals = (metrics.completed_goals as number) ?? 0;
  const totalGoals = (metrics.total_goals as number) ?? 0;
  const healthScore = (metrics.health_score as number) ?? 0;
  const wellbeingScore = (metrics.wellbeing_score as number) ?? 0;
  const learningScore = (metrics.learning_score as number) ?? 0;
  const productivityPct = (metrics.productivity_pct as number) ?? 0;
  const screenTimeChangePct = (metrics.screen_time_change_pct as number) ?? 0;
  const completedContent = (metrics.completed_content as number) ?? 0;

  const overallScore = latestReport
    ? Math.round((healthScore + wellbeingScore + learningScore) / 3)
    : 0;

  const comparisonData =
    (metrics.screen_time_comparison as { name: string; lastWeek: number; thisWeek: number }[]) ??
    [];

  const AR_METRICS = [
    {
      t: "وقت الشاشة",
      v: `${screenTimeAvg} س/يوم`,
      trend: screenTimeChangePct,
      icon: Smartphone,
      color: "text-primary",
    },
    {
      t: "الإنتاجية",
      v: `${productivityPct}٪`,
      trend: 0,
      icon: TrendingUp,
      color: "text-warning",
    },
    { t: "متوسط المزاج", v: `${moodAvg}/١٠`, trend: 0, icon: Heart, color: "text-success" },
    { t: "الأهداف", v: `${completedGoals}/${totalGoals}`, trend: 0, icon: Target, color: "text-warning" },
  ];

  const INSIGHTS = [];
  if (latestReport?.ai_summary) {
    INSIGHTS.push({ t: "ملخص الأسبوع", d: latestReport.ai_summary, tag: "AI", tagColor: "bg-primary/10 text-primary" });
  }
  if (healthScore >= 70) {
    INSIGHTS.push({ t: "صحة رقمية جيدة", d: `درجة صحتك الرقمية ${healthScore}/١٠٠. استمر في الحفاظ على وقت شاشة معتدل.`, tag: "صحة", tagColor: "bg-success/10 text-success" });
  }
  if (wellbeingScore >= 70) {
    INSIGHTS.push({ t: "رفاهية ممتازة", d: `مستوى الرفاهية لديك ${wellbeingScore}/١٠٠. مزاجك إيجابي هذا الأسبوع.`, tag: "رفاه", tagColor: "bg-info/10 text-info" });
  }
  if (learningScore > 0) {
    INSIGHTS.push({ t: "تعلّم مستمر", d: `أكملت ${completedContent} محتوى تعليمي هذا الأسبوع.`, tag: "تعلّم", tagColor: "bg-warning/10 text-warning" });
  }
  if (INSIGHTS.length === 0) {
    INSIGHTS.push({ t: "ابدأ التسجيل", d: "سجّل مزاجك وعاداتك الرقمية يوميًا لتحصل على تحليلات دقيقة.", tag: "نصيحة", tagColor: "bg-primary/10 text-primary" });
  }

  const RECOMMENDATIONS: { t: string; d: string; a: string }[] = [];
  if (screenTimeAvg > 5) {
    RECOMMENDATIONS.push({ t: "قلّل وقت الشاشة", d: "متوسط وقت شاشة مرتفع. جرّب تقليل ساعتين يوميًا ومارس الرياضة.", a: "عرض الإحصائيات" });
  }
  if (productivityPct < 50) {
    RECOMMENDATIONS.push({ t: "حسّن الإنتاجية", d: "نسبة إنجاز المهام منخفضة. جرّب تقسيم المهام الكبيرة إلى أجزاء أصغر.", a: "عرض المهام" });
  }
  if (moodAvg < 5) {
    RECOMMENDATIONS.push({ t: "اعتني بصحتك النفسية", d: "متوسط المزاج منخفض هذا الأسبوع. جرّب تمارين التنفس أو المشي.", a: "عرض تمارين" });
  }
  if (RECOMMENDATIONS.length === 0) {
    RECOMMENDATIONS.push({ t: "أحسنت!", d: "كل المؤشرات إيجابية. حافظ على نمط حياتك الصحي.", a: "عرض التقرير" });
  }

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
              <span className="text-sm font-medium">
                {latestReport
                  ? `${latestReport.start_date} - ${latestReport.end_date}`
                  : "لا توجد تقارير بعد"}
              </span>
            </div>
            <h2 className="text-2xl font-bold">
              {latestReport
                ? (latestReport.ai_summary ?? "تقرير الأسبوع")
                : "لم يتم إنشاء أي تقرير بعد"}
            </h2>
          </div>

          {latestReport ? (
            <div className="flex items-center gap-4 bg-white/10 rounded-2xl p-4 backdrop-blur-sm shrink-0">
              <div className="text-center">
                <div className="text-3xl font-black tabular-nums">{overallScore}</div>
                <div className="text-[10px] opacity-80 uppercase tracking-widest mt-1">النقاط</div>
              </div>
              <div className="h-10 w-px bg-white/20" />
              <div className="flex flex-col items-center">
                <Badge variant="secondary" className="bg-success text-success-foreground border-none">
                  <TrendingUp className="h-3 w-3 me-1" />
                  {screenTimeChangePct < 0 ? Math.abs(screenTimeChangePct) : 0}٪
                </Badge>
                <div className="text-[10px] opacity-80 uppercase tracking-widest mt-1.5">النمو</div>
              </div>
            </div>
          ) : (
            <Button
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending}
              className="bg-white text-primary hover:bg-white/90 shrink-0"
              size="lg"
            >
              {generateMutation.isPending ? (
                <Loader2 className="h-4 w-4 ml-2 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4 ml-2" />
              )}
              {generateMutation.isPending ? "جارٍ الإنشاء..." : "إنشاء التقرير"}
            </Button>
          )}
        </div>
      </Card>

      {/* Loading skeleton */}
      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="p-4">
              <div className="flex items-center gap-3">
                <Skeleton className="h-10 w-10 rounded-xl" />
                <div className="space-y-2">
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-6 w-16" />
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {error && (
        <Card className="p-6 text-center text-destructive">
          خطأ في تحميل التقارير. جرّب مرة أخرى لاحقًا.
        </Card>
      )}

      {!isLoading && !error && (
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
                {AR_METRICS.map((m) => {
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
            {comparisonData.length > 0 && (
              <section>
                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  <h3 className="text-lg font-bold">مقارنة وقت الشاشة (ساعة/يوم)</h3>
                </div>
                <Card className="p-5 h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={comparisonData}
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
            )}
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
                      <Button
                        size="sm"
                        variant="outline"
                        className="w-full text-xs h-8"
                        onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
                      >
                        {rec.a}
                      </Button>
                    </div>
                  ))}
                </div>
              </Card>
            </section>
          </div>
        </div>
      )}
    </AppShell>
  );
}
