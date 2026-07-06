import { createFileRoute } from "@tanstack/react-router";
import { useState, useMemo } from "react";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Flame, BookOpen, Moon, Smartphone, Dumbbell, Brain, Trophy, Search } from "lucide-react";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/challenges")({
  head: () => ({ meta: [{ title: "التحديات | بصمة+" }] }),
  component: Challenges,
});

const active = [
  {
    title: "أسبوع بلا تيك توك بعد ٩م",
    days: 7,
    progress: 57,
    icon: Smartphone,
    color: "text-primary",
  },
  { title: "اقرأ ٢٠ دقيقة يوميًا", days: 14, progress: 35, icon: BookOpen, color: "text-info" },
];

const list = {
  daily: [
    {
      t: "نَم قبل ١٢ منتصف الليل",
      d: "صحة أفضل تبدأ بنوم منتظم.",
      level: "سهل",
      pts: 20,
      icon: Moon,
      tag: "صحة",
    },
    {
      t: "٣٠ دقيقة قراءة",
      d: "كتاب من اختيارك.",
      level: "سهل",
      pts: 25,
      icon: BookOpen,
      tag: "تعلّم",
    },
    {
      t: "تمرين رياضي ٢٠ دقيقة",
      d: "حافظ على نشاطك.",
      level: "متوسط",
      pts: 30,
      icon: Dumbbell,
      tag: "صحة",
    },
  ],
  weekly: [
    {
      t: "تقليل وقت الشاشة ٢٠٪",
      d: "خلال ٧ أيام.",
      level: "متوسط",
      pts: 100,
      icon: Smartphone,
      tag: "صحة",
    },
    {
      t: "أكمل كورس قصير",
      d: "أيّ كورس أقل من ٥ ساعات.",
      level: "متوسط",
      pts: 150,
      icon: Brain,
      tag: "تعلّم",
    },
    {
      t: "اكتب ٧ تأمّلات يوميّة",
      d: "تأمّل قصير في نهاية كل يوم.",
      level: "سهل",
      pts: 80,
      icon: BookOpen,
      tag: "رفاه",
    },
  ],
  monthly: [
    {
      t: "احتفظ بسلسلة ٣٠ يوم",
      d: "سلسلة بدون انقطاع.",
      level: "صعب",
      pts: 500,
      icon: Flame,
      tag: "إنجاز",
    },
    {
      t: "تعلّم مهارة جديدة",
      d: "خصّص ٢٠ ساعة هذا الشهر.",
      level: "صعب",
      pts: 400,
      icon: Brain,
      tag: "تعلّم",
    },
  ],
};

// All unique tags across all tabs
const ALL_TAGS = ["الكل", "صحة", "تعلّم", "رفاه", "إنجاز"];

type TabKey = keyof typeof list;

function Section({
  items,
  searchQuery,
  activeTag,
}: {
  items: typeof list.daily;
  searchQuery: string;
  activeTag: string;
}) {
  const filtered = useMemo(() => {
    return items.filter((c) => {
      const tagMatch = activeTag === "الكل" || c.tag === activeTag;
      const searchMatch = !searchQuery || c.t.includes(searchQuery) || c.d.includes(searchQuery);
      return tagMatch && searchMatch;
    });
  }, [items, searchQuery, activeTag]);

  if (filtered.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed py-16 text-center">
        <Search className="mb-3 h-8 w-8 text-muted-foreground/40" />
        <p className="font-semibold text-muted-foreground">لا توجد تحديات مطابقة</p>
        <p className="mt-1 text-sm text-muted-foreground/70">جرّب تغيير الفلتر أو البحث</p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {filtered.map((c) => {
        const Icon = c.icon;
        return (
          <Card key={c.t} className="group flex flex-col p-5 transition-all hover:shadow-glow">
            <div className="mb-3 flex items-start justify-between">
              <div className="gradient-warm flex h-11 w-11 items-center justify-center rounded-xl text-primary">
                <Icon className="h-5 w-5" />
              </div>
              <Badge variant="secondary">{c.tag}</Badge>
            </div>
            <h3 className="font-bold">{c.t}</h3>
            <p className="mt-1 flex-1 text-sm text-muted-foreground">{c.d}</p>
            <div className="mt-4 flex items-center justify-between text-xs">
              <span className="text-muted-foreground">{c.level}</span>
              <span className="font-semibold text-warning-foreground">+{c.pts} نقطة</span>
            </div>
            <Button className="mt-4 gradient-primary shadow-soft transition-transform hover:-translate-y-1">
              انضمّ
            </Button>
          </Card>
        );
      })}
    </div>
  );
}

function Challenges() {
  const [activeTag, setActiveTag] = useState("الكل");
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <AppShell title="التحديات" subtitle="ابنِ عاداتك من خلال تحديات قصيرة وملموسة.">
      {/* Active challenges */}
      {active.length > 0 && (
        <Card className="mb-6 p-5">
          <div className="mb-4 flex items-center gap-2">
            <Trophy className="h-5 w-5 text-warning-foreground" />
            <h3 className="text-lg font-bold">تحدياتك النشطة</h3>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {active.map((a) => {
              const Icon = a.icon;
              return (
                <div key={a.title} className="rounded-xl border bg-muted/30 p-4">
                  <div className="mb-2 flex items-center gap-3">
                    <div
                      className={`gradient-warm inline-flex h-9 w-9 items-center justify-center rounded-lg ${a.color}`}
                    >
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="font-semibold">{a.title}</div>
                  </div>
                  <Progress value={a.progress} className="h-2" />
                  <div className="mt-2 flex justify-between text-xs text-muted-foreground">
                    <span>
                      {Math.round((a.progress / 100) * a.days)} / {a.days} يوم
                    </span>
                    <span>{a.progress}٪</span>
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Search + Tag filter bar */}
      <Card className="mb-4 p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="ابحث في التحديات..."
              className="ps-4 pe-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              id="challenges-search"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            {ALL_TAGS.map((tag) => (
              <Badge
                key={tag}
                variant={activeTag === tag ? "default" : "outline"}
                className={cn(
                  "cursor-pointer select-none transition-all",
                  activeTag === tag && "shadow-soft",
                )}
                onClick={() => setActiveTag(tag)}
              >
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="daily">
        <TabsList>
          <TabsTrigger value="daily">يومي</TabsTrigger>
          <TabsTrigger value="weekly">أسبوعي</TabsTrigger>
          <TabsTrigger value="monthly">شهري</TabsTrigger>
        </TabsList>
        {(["daily", "weekly", "monthly"] as TabKey[]).map((tab) => (
          <TabsContent key={tab} value={tab} className="mt-6">
            <Section items={list[tab]} searchQuery={searchQuery} activeTag={activeTag} />
          </TabsContent>
        ))}
      </Tabs>
    </AppShell>
  );
}
