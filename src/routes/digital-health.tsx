import { createFileRoute } from "@tanstack/react-router";
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

export const Route = createFileRoute("/digital-health")({
  head: () => ({ meta: [{ title: "الصحة الرقمية | بصمة+" }] }),
  component: DH,
});

const screen = [
  { d: "س", h: 6.2 },
  { d: "ح", h: 5.4 },
  { d: "ن", h: 4.8 },
  { d: "ث", h: 5.1 },
  { d: "ر", h: 3.9 },
  { d: "خ", h: 4.5 },
  { d: "ج", h: 4.2 },
];
const sleepStress = [
  { d: "س", sleep: 6.5, stress: 7 },
  { d: "ح", sleep: 7.2, stress: 5 },
  { d: "ن", sleep: 8, stress: 4 },
  { d: "ث", sleep: 6, stress: 8 },
  { d: "ر", sleep: 7.5, stress: 5 },
  { d: "خ", sleep: 8.2, stress: 3 },
  { d: "ج", sleep: 7.8, stress: 4 },
];
const apps = [
  { name: "تواصل اجتماعي", value: 38, color: "var(--chart-1)" },
  { name: "فيديو", value: 22, color: "var(--chart-2)" },
  { name: "ألعاب", value: 15, color: "var(--chart-3)" },
  { name: "إنتاجية", value: 17, color: "var(--chart-4)" },
  { name: "أخرى", value: 8, color: "var(--chart-5)" },
];

function DH() {
  return (
    <AppShell
      title="الصحة الرقمية"
      subtitle="نظرة عميقة على عاداتك الرقمية وتأثيرها."
      actions={
        <Select defaultValue="7">
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
      <Card className="mb-6 p-6">
        <div className="flex flex-col items-start gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="text-sm text-muted-foreground">نقاط الصحة الرقميّة</div>
            <div className="mt-1 flex items-end gap-3">
              <span className="text-5xl font-extrabold text-primary">٨٢</span>
              <span className="mb-2 text-sm text-success">+٧ منذ الأسبوع الماضي</span>
            </div>
            <p className="mt-2 max-w-md text-sm text-muted-foreground">
              صحّتك الرقمية ممتازة. تابع التركيز على تقليل وقت التواصل الاجتماعي ليلاً.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-4 sm:gap-6">
            {[
              { l: "خطر الإدمان", v: "منخفض", t: "text-success" },
              { l: "تركيز", v: "٧٤٪", t: "text-info" },
              { l: "توازن", v: "جيد", t: "text-primary" },
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
            <h3 className="font-bold">وقت الشاشة اليومي</h3>
            <Badge variant="secondary">انخفاض ١٢٪</Badge>
          </div>
          <div className="h-64">
            <ResponsiveContainer>
              <BarChart data={screen}>
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
                <Bar dataKey="h" fill="var(--primary)" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="p-5">
          <h3 className="mb-4 font-bold">النوم مقابل التوتر</h3>
          <div className="h-64">
            <ResponsiveContainer>
              <LineChart data={sleepStress}>
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
          <h3 className="mb-4 font-bold">توزيع وقت التطبيقات</h3>
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
              <Button variant="outline" className="mt-2 w-full">
                رؤى مفصّلة
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
