import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import { Loader2 } from "lucide-react";
import { apiGetDigitalHealthAnalytics } from "@/lib/api";

export const Route = createFileRoute("/digital-health")({
  head: () => ({ meta: [{ title: "الصحة الرقمية | بصمة+" }] }),
  component: DH,
});

function DH() {
  const [days, setDays] = useState(7);
  const queryClient = useQueryClient();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["digital-health", days],
    queryFn: () => apiGetDigitalHealthAnalytics(days),
  });

  const screen = data?.screen_time_chart || [];
  const sleepStress = data?.sleep_stress_chart || [];
  const apps = data?.app_usage_chart || [];

  return (
    <AppShell
      title="الصحة الرقمية"
      subtitle="نظرة عميقة على عاداتك الرقمية وتأثيرها."
      actions={
        <Select value={days.toString()} onValueChange={(v) => setDays(Number(v))}>
          <SelectTrigger className="w-36">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7">آخر ٧ أيام</SelectItem>
            <SelectItem value="30">آخر ٣٠ يوم</SelectItem>
            <SelectItem value="90">آخر ٩٠ يوم</SelectItem>
          </SelectContent>
        </Select>
      }
    >
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : isError ? (
        <Card className="p-10 text-center text-sm text-destructive">
          فшибка في تحميل البيانات. حاول لاحقاً.
        </Card>
      ) : (
        <>
          <Card className="mb-6 p-6">
            <div className="flex flex-col items-start gap-6 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="text-sm text-muted-foreground">نقاط الصحة الرقميّة</div>
                <div className="mt-1 flex items-end gap-3">
                  <span className="text-5xl font-extrabold text-primary">
                    {data?.health_score || 0}
                  </span>
                  <span
                    className={`mb-2 text-sm ${data?.score_trend && data.score_trend > 0 ? "text-success" : data?.score_trend && data.score_trend < 0 ? "text-destructive" : "text-muted-foreground"}`}
                  >
                    {data?.score_trend && data.score_trend > 0
                      ? `+${data.score_trend}`
                      : data?.score_trend}{" "}
                    منذ الفترة الماضية
                  </span>
                </div>
                <p className="mt-2 max-w-md text-sm text-muted-foreground">
                  {data?.health_score && data.health_score > 80
                    ? "صحّتك الرقمية ممتازة. تابع التركيز على إبقاء الشاشة بعيدة ليلاً."
                    : "نقاطك تحتاج لبعض التحسين. حاول تقليل وقت التواصل الاجتماعي."}
                </p>
              </div>
              <div className="grid grid-cols-3 gap-4 sm:gap-6">
                {[
                  {
                    l: "خطر الإدمان",
                    v: (data?.health_score || 0) > 70 ? "منخفض" : "مرتفع",
                    t: (data?.health_score || 0) > 70 ? "text-success" : "text-destructive",
                  },
                  { l: "استخدام", v: `${data?.health_score || 0}٪`, t: "text-info" },
                  {
                    l: "توازن",
                    v: (data?.health_score || 0) > 80 ? "ممتاز" : "مقبول",
                    t: "text-primary",
                  },
                ].map((s) => (
                  <div key={s.l} className="text-center">
                    <div className="text-xs text-muted-foreground">{s.l}</div>
                    <div className={`mt-1 text-lg font-bold ${s.t}`}>{s.v}</div>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          <div className="grid gap-6 lg:grid-cols-2">
            <Card className="p-5">
              <div className="mb-4 flex items-center justify-between">
                <h3 className="font-bold">وقت الشاشة اليومي (ساعات)</h3>
              </div>
              <div className="h-64">
                <ResponsiveContainer>
                  <BarChart data={screen}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="hsl(var(--border))"
                      opacity={0.4}
                    />
                    <XAxis dataKey="d" fontSize={12} />
                    <YAxis fontSize={12} />
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
              <h3 className="mb-4 font-bold">النوم (ساعات) مقابل التوتر</h3>
              <div className="h-64">
                <ResponsiveContainer>
                  <LineChart data={sleepStress}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="hsl(var(--border))"
                      opacity={0.4}
                    />
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
                    <Line
                      name="نوم (س)"
                      type="monotone"
                      dataKey="sleep"
                      stroke="var(--chart-3)"
                      strokeWidth={3}
                    />
                    <Line
                      name="توتر"
                      type="monotone"
                      dataKey="stress"
                      stroke="var(--chart-4)"
                      strokeWidth={3}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <Card className="p-5 lg:col-span-2">
              <h3 className="mb-4 font-bold">توزيع وقت التطبيقات (تقديري)</h3>
              <div className="grid items-center gap-6 md:grid-cols-2">
                <div className="h-64">
                  <ResponsiveContainer>
                    <PieChart>
                      <Pie
                        data={apps}
                        dataKey="value"
                        nameKey="name"
                        innerRadius={50}
                        outerRadius={90}
                        paddingAngle={2}
                      >
                        {apps.map((a) => (
                          <Cell key={a.name} fill={a.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          background: "var(--card)",
                          border: "1px solid var(--border)",
                          borderRadius: 8,
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-3">
                  {apps.map((a) => (
                    <div key={a.name} className="flex items-center justify-between gap-3">
                      <div className="flex items-center gap-2">
                        <span className="h-3 w-3 rounded-sm" style={{ backgroundColor: a.color }} />
                        <span className="text-sm">{a.name}</span>
                      </div>
                      <span className="text-sm font-semibold">{a.value}٪</span>
                    </div>
                  ))}
                  <Button
                    variant="outline"
                    className="mt-2 w-full"
                    onClick={() => queryClient.invalidateQueries({ queryKey: ["digital-health"] })}
                  >
                    تحديث البيانات
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        </>
      )}
    </AppShell>
  );
}
