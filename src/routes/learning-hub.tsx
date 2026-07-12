import { createFileRoute } from "@tanstack/react-router";
import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Bookmark, Clock, Search, PlayCircle, BookOpen, FileText, Briefcase, Loader2 } from "lucide-react";
import { apiGetLearningContent } from "@/lib/api";

export const Route = createFileRoute("/learning-hub")({
  head: () => ({ meta: [{ title: "مركز التعلّم | بصمة+" }] }),
  component: Hub,
});

const TYPE_MAP: Record<string, string> = {
  الكل: "",
  كورسات: "COURSE",
  فيديوهات: "VIDEO",
  كتب: "BOOK",
  مقالات: "ARTICLE",
};

const FILTERS = ["الكل", "كورسات", "فيديوهات", "كتب", "مقالات"];

const ICON_MAP: Record<string, any> = {
  COURSE: PlayCircle,
  VIDEO: PlayCircle,
  BOOK: BookOpen,
  ARTICLE: FileText,
};

const paths = [
  { t: "مطوّر واجهات", c: "React · TypeScript · Tailwind", n: 12, q: "React" },
  { t: "عالم بيانات", c: "Python · SQL · ML", n: 18, q: "Python" },
  { t: "مصمّم منتجات", c: "Figma · بحث · بروتوتايب", n: 9, q: "تصميم" },
];

function Hub() {
  const [activeFilter, setActiveFilter] = useState("الكل");
  const [searchQuery, setSearchQuery] = useState("");
  const [bookmarkedIds, setBookmarkedIds] = useState<Set<string>>(() => {
    try {
      const stored = localStorage.getItem("basma_bookmarks");
      return stored ? new Set(JSON.parse(stored)) : new Set();
    } catch {
      return new Set();
    }
  });

  const { data: allItems, isLoading, isError } = useQuery({
    queryKey: ["learning-content"],
    queryFn: () => apiGetLearningContent(),
  });

  const toggleBookmark = (id: string) => {
    setBookmarkedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      localStorage.setItem("basma_bookmarks", JSON.stringify([...next]));
      return next;
    });
  };

  const filtered = useMemo(() => {
    if (!allItems) return [];
    return allItems.filter((item) => {
      const typeMatch = activeFilter === "الكل" || item.content_type === TYPE_MAP[activeFilter];
      const searchMatch = !searchQuery || item.title.toLowerCase().includes(searchQuery.toLowerCase()) || (item.description && item.description.toLowerCase().includes(searchQuery.toLowerCase()));
      return typeMatch && searchMatch;
    });
  }, [allItems, activeFilter, searchQuery]);

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

          {isLoading ? (
            <div className="flex justify-center py-20">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : isError ? (
            <div className="py-10 text-center text-sm text-destructive">
              فшибка في تحميل المحتوى. حاول لاحقاً.
            </div>
          ) : filtered.length === 0 ? (
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
                  setSearchQuery("");
                }}
              >
                إعادة ضبط الفلاتر
              </Button>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filtered.map((i) => {
                const Icon = ICON_MAP[i.content_type] || FileText;
                return (
                  <Card
                    key={i.id}
                    className="group flex flex-col p-5 transition-all hover:shadow-glow"
                  >
                    <div className="mb-3 flex items-start justify-between">
                      <div className="gradient-warm flex h-10 w-10 items-center justify-center rounded-xl text-primary">
                        <Icon className="h-5 w-5" />
                      </div>
                      <button
                        className={`transition ${bookmarkedIds.has(i.id) ? "text-primary" : "text-muted-foreground hover:text-primary"}`}
                        onClick={() => toggleBookmark(i.id)}
                        title={bookmarkedIds.has(i.id) ? "إزالة من المحفوظات" : "حفظ"}
                      >
                        <Bookmark className={`h-4 w-4 ${bookmarkedIds.has(i.id) ? "fill-primary" : ""}`} />
                      </button>
                    </div>
                    <h3 className="font-bold leading-snug">{i.title}</h3>
                    <div className="mt-2 flex items-center gap-3 text-xs text-muted-foreground">
                      {i.estimated_minutes && (
                        <span className="flex items-center gap-1">
                          <Clock className="h-3.5 w-3.5" /> {i.estimated_minutes} د
                        </span>
                      )}
                      {i.category && (
                        <Badge variant="secondary" className="text-xs">
                          {i.category}
                        </Badge>
                      )}
                    </div>
                    {i.description && (
                      <p className="mt-2 text-xs text-muted-foreground line-clamp-2">{i.description}</p>
                    )}
                    <Button variant="outline" size="sm" className="mt-auto pt-4" asChild>
                      <a href={i.url || "#"} target="_blank" rel="noopener noreferrer">
                        ابدأ
                      </a>
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
                    <Button size="sm" variant="ghost" className="px-2 text-primary" onClick={() => setSearchQuery(p.q)}>
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
