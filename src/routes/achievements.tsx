import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Flame,
  Star,
  Trophy,
  Brain,
  Moon,
  BookOpen,
  Smartphone,
  Heart,
  Zap,
  Lock,
} from "lucide-react";

export const Route = createFileRoute("/achievements")({
  head: () => ({ meta: [{ title: "الإنجازات | بصمة+" }] }),
  component: Ach,
});

const badges = [
  { t: "أول خطوة", d: "أكمل أول مهمّة.", icon: Star, unlocked: true },
  { t: "سلسلة ٧ أيام", d: "حافظ على نشاطك أسبوعًا.", icon: Flame, unlocked: true },
  { t: "قارئ نَهِم", d: "اقرأ ١٠ ساعات.", icon: BookOpen, unlocked: true },
  { t: "عقل متعطّش", d: "أكمل ٣ كورسات.", icon: Brain, unlocked: true },
  { t: "بطل النوم", d: "نَم ٧ ساعات لـ ١٤ يوم.", icon: Moon, unlocked: false, p: 60 },
  { t: "منفصل عن الشاشة", d: "أسبوع بأقل من ٣س شاشة.", icon: Smartphone, unlocked: false, p: 30 },
  { t: "متوازن", d: "احتفظ بمزاج ٧+ لمدّة ١٤ يوم.", icon: Heart, unlocked: false, p: 50 },
  { t: "صاعقة", d: "أكمل ٥ تحديّات في يوم.", icon: Zap, unlocked: false, p: 0 },
];
const activity = [
  { t: "أنهيت تحدي «اقرأ ٢٠ دقيقة»", time: "منذ ساعة", pts: 25 },
  { t: "وصلت للمستوى ٧", time: "أمس", pts: 100 },
  { t: "حصلت على شارة «قارئ نَهِم»", time: "قبل ٣ أيام", pts: 50 },
  { t: "أكملت ٥٠ جلسة بومودورو", time: "قبل أسبوع", pts: 200 },
];

function Ach() {
  return (
    <AppShell title="الإنجازات" subtitle="احتفل بإنجازاتك واستمر في التقدّم.">
      <Card className="gradient-primary mb-6 p-6 text-primary-foreground shadow-glow">
        <div className="grid items-center gap-6 sm:grid-cols-3">
          <div>
            <div className="text-sm opacity-90">المستوى الحالي</div>
            <div className="mt-1 text-5xl font-extrabold">٧</div>
            <div className="mt-1 text-xs opacity-80">٢٤٠ نقطة للمستوى التالي</div>
          </div>
          <div className="sm:col-span-2">
            <div className="mb-2 flex justify-between text-sm">
              <span>٢٧٦٠ نقطة</span>
              <span className="opacity-80">٣٠٠٠ للمستوى ٨</span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-primary-foreground/20">
              <div className="gradient-warm h-full rounded-full" style={{ width: "92%" }} />
            </div>
            <div className="mt-4 flex gap-3 text-sm">
              <span className="flex items-center gap-1">
                <Flame className="h-4 w-4" /> سلسلة ١٢ يوم
              </span>
              <span className="flex items-center gap-1">
                <Trophy className="h-4 w-4" /> ٤ شارات
              </span>
            </div>
          </div>
        </div>
      </Card>

      <h3 className="mb-3 text-lg font-bold">الشارات</h3>
      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {badges.map((b) => {
          const Icon = b.icon;
          return (
            <Card
              key={b.t}
              className={`p-5 text-center transition-all ${b.unlocked ? "hover:shadow-glow" : "opacity-70"}`}
            >
              <div
                className={`mx-auto flex h-16 w-16 items-center justify-center rounded-2xl ${b.unlocked ? "gradient-primary text-primary-foreground shadow-glow" : "bg-muted text-muted-foreground"}`}
              >
                {b.unlocked ? <Icon className="h-8 w-8" /> : <Lock className="h-7 w-7" />}
              </div>
              <h4 className="mt-3 font-bold">{b.t}</h4>
              <p className="mt-1 text-xs text-muted-foreground">{b.d}</p>
              {!b.unlocked && typeof b.p === "number" && (
                <div className="mt-3">
                  <Progress value={b.p} className="h-1.5" />
                  <div className="mt-1 text-xs text-muted-foreground">{b.p}٪</div>
                </div>
              )}
              {b.unlocked && (
                <Badge className="mt-3" variant="secondary">
                  مفتوحة
                </Badge>
              )}
            </Card>
          );
        })}
      </div>

      <Card className="p-5">
        <h3 className="mb-4 text-lg font-bold">آخر الأنشطة</h3>
        <div className="space-y-2">
          {activity.map((a, i) => (
            <div
              key={i}
              className="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3"
            >
              <div className="flex items-center gap-3">
                <div className="gradient-warm flex h-9 w-9 items-center justify-center rounded-lg text-primary">
                  <Trophy className="h-4 w-4" />
                </div>
                <div>
                  <div className="text-sm font-medium">{a.t}</div>
                  <div className="text-xs text-muted-foreground">{a.time}</div>
                </div>
              </div>
              <Badge variant="secondary" className="text-success">
                +{a.pts}
              </Badge>
            </div>
          ))}
        </div>
      </Card>
    </AppShell>
  );
}
