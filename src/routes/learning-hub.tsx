import { createFileRoute } from "@tanstack/react-router";
import { useState, useMemo } from "react";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Bookmark, Clock, Search, PlayCircle, BookOpen, FileText, Briefcase } from "lucide-react";

export const Route = createFileRoute("/learning-hub")({
  head: () => ({ meta: [{ title: "مركز التعلّم | بصمة+" }] }),
  component: Hub,
});

const TYPE_MAP: Record<string, string> = {
  الكل: "all",
  كورسات: "course",
  فيديوهات: "video",
  كتب: "book",
  مقالات: "article",
};

const FILTERS = ["الكل", "كورسات", "فيديوهات", "كتب", "مقالات"];
const LEVELS = ["مبتدئ", "متوسط", "متقدّم"];

const ALL_ITEMS = [
  {
    type: "course",
    t: "أساسيات SQL للبيانات",
    dur: "٣ س",
    level: "مبتدئ",
    topic: "بيانات",
    icon: PlayCircle,
  },
  {
    type: "book",
    t: "العادات الذرية",
    dur: "٢٥٠ ص",
    level: "—",
    topic: "تطوير ذاتي",
    icon: BookOpen,
  },
  {
    type: "article",
    t: "كيف تستعدّ لمقابلة تقنية",
    dur: "٨ د",
    level: "متوسط",
    topic: "مهنة",
    icon: FileText,
  },
  {
    type: "course",
    t: "بايثون للمبتدئين",
    dur: "٦ س",
    level: "مبتدئ",
    topic: "برمجة",
    icon: PlayCircle,
  },
  {
    type: "video",
    t: "تقنيات تركيز عميقة",
    dur: "٢٠ د",
    level: "متوسط",
    topic: "إنتاجية",
    icon: PlayCircle,
  },
  {
    type: "article",
    t: "إدارة وقت الدراسة الجامعيّة",
    dur: "١٢ د",
    level: "مبتدئ",
    topic: "دراسة",
    icon: FileText,
  },
  {
    type: "course",
    t: "تصميم واجهات حديث",
    dur: "٤ س",
    level: "متوسط",
    topic: "تصميم",
    icon: PlayCircle,
  },
  { type: "book", t: "العمل العميق", dur: "٣١٠ ص", level: "—", topic: "إنتاجية", icon: BookOpen },
];
const paths = [
  { t: "مطوّر واجهات", c: "React · TypeScript · Tailwind", n: 12 },
  { t: "عالم بيانات", c: "Python · SQL · ML", n: 18 },
  { t: "مصمّم منتجات", c: "Figma · بحث · بروتوتايب", n: 9 },
];

function Hub() {
  const [activeFilter, setActiveFilter] = useState("الكل");
  const [activeLevel, setActiveLevel] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const filtered = useMemo(() => {
    return ALL_ITEMS.filter((item) => {
      const typeMatch = activeFilter === "الكل" || item.type === TYPE_MAP[activeFilter];
      const levelMatch = !activeLevel || activeLevel === "الكل" || item.level === activeLevel;
      const searchMatch = !searchQuery || item.t.toLowerCase().includes(searchQuery.toLowerCase());
      return typeMatch && levelMatch && searchMatch;
    });
  }, [activeFilter, activeLevel, searchQuery]);

  return (
    <AppShell title="مركز التعلّم" subtitle="كورسات، كتب، ومقالات مختارة لك.">
      <Card className="mb-6 p-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="ابحث عن موضوع..."
              className="ps-9 pe-3"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              id="learning-search"
            />
          </div>

          {/* Type filters */}
          <div className="flex flex-wrap gap-2">
            {FILTERS.map((f) => (
              <Badge
                key={f}
                variant={activeFilter === f ? "default" : "outline"}
                className="cursor-pointer select-none transition-all hover:shadow-sm"
                onClick={() => setActiveFilter(f)}
              >
                {f}
              </Badge>
            ))}
          </div>

          {/* Level filters */}
          <div className="flex flex-wrap gap-2">
            {LEVELS.map((l) => (
              <Badge
                key={l}
                variant={activeLevel === l ? "default" : "secondary"}
                className="cursor-pointer select-none transition-all"
                onClick={() => setActiveLevel(activeLevel === l ? null : l)}
              >
                {l}
              </Badge>
            ))}
          </div>
        </div>
      </Card>

      <div className="grid gap-6 xl:grid-cols-[1fr_300px]">
        <div>
          {/* Results count badge */}
          <div className="mb-4 flex items-center gap-2">
            <span className="text-sm text-muted-foreground">النتائج</span>
            <Badge variant="secondary" className="transition-all duration-300">
              {filtered.length} {filtered.length === 1 ? "مورد" : "موارد"}
            </Badge>
          </div>

          {filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed py-20 text-center">
              <Search className="mb-3 h-10 w-10 text-muted-foreground/40" />
              <p className="font-semibold text-muted-foreground">لا توجد نتائج</p>
              <p className="mt-1 text-sm text-muted-foreground/70">جرّب تغيير البحث أو الفلاتر</p>
              <Button
                variant="outline"
                size="sm"
                className="mt-4"
                onClick={() => {
                  setActiveFilter("الكل");
                  setActiveLevel(null);
                  setSearchQuery("");
                }}
              >
                إعادة ضبط الفلاتر
              </Button>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filtered.map((i) => {
                const Icon = i.icon;
                return (
                  <Card
                    key={i.t}
                    className="group flex flex-col p-5 transition-all hover:shadow-glow"
                  >
                    <div className="mb-3 flex items-start justify-between">
                      <div className="gradient-warm flex h-10 w-10 items-center justify-center rounded-xl text-primary">
                        <Icon className="h-5 w-5" />
                      </div>
                      <button className="text-muted-foreground transition hover:text-primary">
                        <Bookmark className="h-4 w-4" />
                      </button>
                    </div>
                    <h3 className="font-bold leading-snug">{i.t}</h3>
                    <div className="mt-2 flex items-center gap-3 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3.5 w-3.5" /> {i.dur}
                      </span>
                      <Badge variant="secondary" className="text-xs">
                        {i.topic}
                      </Badge>
                    </div>
                    <Button variant="outline" size="sm" className="mt-4">
                      ابدأ
                    </Button>
                  </Card>
                );
              })}
            </div>
          )}
        </div>

        <div className="space-y-4">
          <Card className="p-5">
            <div className="mb-3 flex items-center gap-2">
              <Briefcase className="h-5 w-5 text-primary" />
              <h3 className="font-bold">المسارات المهنيّة</h3>
            </div>
            <div className="space-y-3">
              {paths.map((p) => (
                <div key={p.t} className="rounded-xl border bg-muted/30 p-3">
                  <div className="font-semibold">{p.t}</div>
                  <div className="mt-0.5 text-xs text-muted-foreground">{p.c}</div>
                  <div className="mt-2 flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">{p.n} مورد</span>
                    <Button size="sm" variant="ghost" className="px-2 text-primary">
                      استكشف
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
