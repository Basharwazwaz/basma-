import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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

import { useQuery } from "@tanstack/react-query";
import { apiGetAchievements, apiGetProfile } from "@/lib/api";
import { Loader2 } from "lucide-react";

export const Route = createFileRoute("/achievements")({
  head: () => ({ meta: [{ title: "الإنجازات | بصمة+" }] }),
  component: Ach,
});

const iconMap: Record<string, typeof Star> = {
  "أول خطوة": Star,
  "سلسلة ٧ أيام": Flame,
  "قارئ نَهِم": BookOpen,
  "عقل متعطّش": Brain,
  "بطل النوم": Moon,
  "منفصل عن الشاشة": Smartphone,
  متوازن: Heart,
  صاعقة: Zap,
  تحدي: Trophy,
  تعلم: Brain,
  نشاط: Flame,
  نوم: Moon,
  قراءة: BookOpen,
  صحة: Heart,
};

function getIcon(title: string, icon?: string | null) {
  if (icon && iconMap[icon]) return iconMap[icon];
  return iconMap[title] ?? Trophy;
}

function Ach() {
  const { data: userProfile, isLoading: isProfileLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: () => apiGetProfile(),
  });

  const {
    data: earnedAchievements = [],
    isLoading: isAchLoading,
    isError: isAchError,
  } = useQuery({
    queryKey: ["achievements"],
    queryFn: () => apiGetAchievements(),
  });

  const points = userProfile?.profile?.points || 0;
  const level = Math.floor(points / 300) + 1;
  const nextLevelPoints = level * 300;
  const progressPercent = ((points % 300) / 300) * 100;

  // Build activity feed from earned achievements (most recent first)
  const activityFeed = [...earnedAchievements]
    .sort((a, b) => new Date(b.earned_at).getTime() - new Date(a.earned_at).getTime())
    .slice(0, 10);

  function timeAgo(dateStr: string): string {
    const diff = Date.now() - new Date(dateStr).getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    if (hours < 1) return "الآن";
    if (hours < 24) return `منذ ${hours} ساعة`;
    const days = Math.floor(hours / 24);
    if (days === 1) return "أمس";
    if (days < 7) return `قبل ${days} أيام`;
    return `قبل ${Math.floor(days / 7)} أسبوع`;
  }

  return (
    <AppShell title="الإنجازات" subtitle="احتفل بإنجازاتك واستمر في التقدّم.">
      <Card className="gradient-primary mb-6 p-6 text-primary-foreground shadow-glow">
        <div className="grid items-center gap-6 sm:grid-cols-3">
          <div>
            <div className="text-sm opacity-90">المستوى الحالي</div>
            <div className="mt-1 text-5xl font-extrabold">{level}</div>
            <div className="mt-1 text-xs opacity-80">
              {nextLevelPoints - points} نقطة للمستوى التالي
            </div>
          </div>
          <div className="sm:col-span-2">
            <div className="mb-2 flex justify-between text-sm">
              <span>{points} نقطة</span>
              <span className="opacity-80">
                {nextLevelPoints} للمستوى {level + 1}
              </span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-primary-foreground/20">
              <div
                className="gradient-warm h-full rounded-full transition-all"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            <div className="mt-4 flex gap-3 text-sm">
              <span className="flex items-center gap-1">
                <Flame className="h-4 w-4" /> سلسلة ٧ أيام
              </span>
              <span className="flex items-center gap-1">
                <Trophy className="h-4 w-4" /> {earnedAchievements.length} شارات
              </span>
            </div>
          </div>
        </div>
      </Card>

      <h3 className="mb-3 text-lg font-bold">الشارات</h3>
      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {isAchLoading ? (
          <div className="col-span-full py-10 flex justify-center">
            <Loader2 className="animate-spin text-muted-foreground" />
          </div>
        ) : isAchError ? (
          <div className="col-span-full py-10 text-center text-sm text-destructive">
            فشل في تحميل الشارات. حاول لاحقاً.
          </div>
        ) : earnedAchievements.length === 0 ? (
          <div className="col-span-full py-10 text-center text-sm text-muted-foreground">
            لم تحصل على أي شارة بعد. استمر في النشاط!
          </div>
        ) : (
          earnedAchievements.map((ach) => {
            const Icon = getIcon(ach.title, ach.icon);
            return (
              <Card key={ach.id} className="p-5 text-center transition-all hover:shadow-glow">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl gradient-primary text-primary-foreground shadow-glow relative overflow-hidden animate-shimmer">
                  <Icon className="h-8 w-8" />
                </div>
                <h4 className="mt-3 font-bold">{ach.title}</h4>
                <p className="mt-1 text-xs text-muted-foreground">{ach.description}</p>
                <Badge className="mt-3" variant="secondary">
                  مفتوحة
                </Badge>
                {ach.earned_at && (
                  <p className="mt-1 text-xs text-muted-foreground">{timeAgo(ach.earned_at)}</p>
                )}
              </Card>
            );
          })
        )}
      </div>

      <Card className="p-5">
        <h3 className="mb-4 text-lg font-bold">آخر الأنشطة</h3>
        <div className="space-y-2">
          {activityFeed.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">لا توجد أنشطة بعد.</p>
          ) : (
            activityFeed.map((ach) => (
              <div
                key={ach.id}
                className="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3"
              >
                <div className="flex items-center gap-3">
                  <div className="gradient-warm flex h-9 w-9 items-center justify-center rounded-lg text-primary">
                    <Trophy className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="text-sm font-medium">حصلت على شارة "{ach.title}"</div>
                    <div className="text-xs text-muted-foreground">{timeAgo(ach.earned_at)}</div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>
    </AppShell>
  );
}
