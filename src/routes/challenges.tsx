import { createFileRoute } from "@tanstack/react-router";
import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Trophy, Search, Loader2, Star } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  apiGetAllChallenges,
  apiGetUserChallenges,
  apiEnrollChallenge,
  apiCheckinChallenge,
} from "@/lib/api";
import { toast } from "sonner";

export const Route = createFileRoute("/challenges")({
  head: () => ({ meta: [{ title: "التحديات | بصمة+" }] }),
  component: Challenges,
});

const ALL_TAGS = ["الكل", "صحة", "تعلّم", "رفاه", "إنجاز"];

function Section({
  items,
  searchQuery,
  activeTag,
  onEnroll,
  isEnrolling,
}: {
  items: import("@/lib/api").ChallengeData[];
  searchQuery: string;
  activeTag: string;
  onEnroll: (id: string) => void;
  isEnrolling: boolean;
}) {
  const filtered = useMemo(() => {
    return items.filter((c) => {
      const tagMatch = activeTag === "الكل" || c.category === activeTag;
      const searchMatch =
        !searchQuery ||
        c.title.includes(searchQuery) ||
        (c.description && c.description.includes(searchQuery));
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
        return (
          <Card key={c.id} className="group flex flex-col p-5 transition-all hover:shadow-glow">
            <div className="mb-3 flex items-start justify-between">
              <div className="gradient-warm flex h-11 w-11 items-center justify-center rounded-xl text-primary">
                <Star className="h-5 w-5" />
              </div>
              {c.category && <Badge variant="secondary">{c.category}</Badge>}
            </div>
            <h3 className="font-bold">{c.title}</h3>
            <p className="mt-1 flex-1 text-sm text-muted-foreground">{c.description}</p>
            <div className="mt-4 flex items-center justify-between text-xs">
              <span className="text-muted-foreground">{c.duration_days} يوم</span>
              <span className="font-semibold text-warning-foreground">+{c.points_reward} نقطة</span>
            </div>
            <Button
              className="mt-4 gradient-primary shadow-soft transition-transform hover:-translate-y-1"
              onClick={() => onEnroll(c.id)}
              disabled={isEnrolling}
            >
              انضمّ
            </Button>
          </Card>
        );
      })}
    </div>
  );
}

function Challenges() {
  const queryClient = useQueryClient();
  const [activeTag, setActiveTag] = useState("الكل");
  const [searchQuery, setSearchQuery] = useState("");

  const {
    data: allChallenges = [],
    isLoading: isLoadingAll,
    isError: isAllError,
  } = useQuery({
    queryKey: ["challenges"],
    queryFn: () => apiGetAllChallenges(),
  });

  const {
    data: userChallenges = [],
    isLoading: isLoadingUser,
    isError: isUserError,
  } = useQuery({
    queryKey: ["user_challenges"],
    queryFn: () => apiGetUserChallenges(),
  });

  const enrollMutation = useMutation({
    mutationFn: apiEnrollChallenge,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user_challenges"] });
      toast.success("تم الانضمام للتحدي بنجاح! 💪");
    },
    onError: () => {
      toast.error("حدث خطأ أثناء الانضمام للتحدي.");
    },
  });

  const checkinMutation = useMutation({
    mutationFn: apiCheckinChallenge,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["user_challenges"] });
      if (data.status === "COMPLETED") {
        toast.success("تهانينا! أكملت التحدي 🎉");
      } else {
        toast.success("تم تسجيل حضور اليوم ✓");
      }
    },
    onError: (err: any) => {
      const msg = err?.message?.includes("Already checked in")
        ? "تم تسجيل الحضور اليوم مسبقاً"
        : "حدث خطأ أثناء التسجيل.";
      toast.error(msg);
    },
  });

  // Filter out challenges user is already enrolled in
  const enrolledIds = new Set(userChallenges.map((uc) => uc.challenge_id));
  const availableChallenges = allChallenges.filter((c) => !enrolledIds.has(c.id));

  // For demonstration, we just divide available into tabs by duration since we don't have exactly daily/weekly tags
  const daily = availableChallenges.filter((c) => c.duration_days <= 3);
  const weekly = availableChallenges.filter((c) => c.duration_days > 3 && c.duration_days <= 14);
  const monthly = availableChallenges.filter((c) => c.duration_days > 14);

  const activeEnrolled = userChallenges.filter((uc) => uc.status === "ACTIVE");

  return (
    <AppShell title="التحديات" subtitle="ابنِ عاداتك من خلال تحديات قصيرة وملموسة.">
      {/* Active challenges */}
      {isLoadingUser ? (
        <div className="flex justify-center py-4">
          <Loader2 className="animate-spin text-muted-foreground" />
        </div>
      ) : isUserError ? (
        <div className="py-4 text-center text-sm text-destructive">
          فشل في تحميل تحدياتك. حاول لاحقاً.
        </div>
      ) : (
        activeEnrolled.length > 0 && (
          <Card className="mb-6 p-5">
            <div className="mb-4 flex items-center gap-2">
              <Trophy className="h-5 w-5 text-warning-foreground" />
              <h3 className="text-lg font-bold">تحدياتك النشطة</h3>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              {activeEnrolled.map((a) => {
                const c = a.challenge;
                if (!c) return null;
                const progressPct = Math.round((a.progress_days / c.duration_days) * 100);

                return (
                  <div key={a.id} className="rounded-xl border bg-muted/30 p-4">
                    <div className="mb-2 flex items-center gap-3">
                      <div className="gradient-warm inline-flex h-9 w-9 items-center justify-center rounded-lg text-primary">
                        <Star className="h-4 w-4" />
                      </div>
                      <div className="font-semibold">{c.title}</div>
                    </div>
                    <Progress value={progressPct} className="h-2" />
                    <div className="mt-2 flex justify-between text-xs text-muted-foreground">
                      <span>
                        {a.progress_days} / {c.duration_days} يوم
                      </span>
                      <span>{progressPct}٪</span>
                    </div>
                    {a.status === "ACTIVE" && (
                      <Button
                        size="sm"
                        className="mt-3 w-full gradient-primary shadow-soft"
                        onClick={() => checkinMutation.mutate(a.id)}
                        disabled={checkinMutation.isPending}
                      >
                        {checkinMutation.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          "✓ سجّل حضور اليوم"
                        )}
                      </Button>
                    )}
                  </div>
                );
              })}
            </div>
          </Card>
        )
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
      {isLoadingAll ? (
        <div className="flex justify-center py-10">
          <Loader2 className="animate-spin text-muted-foreground" />
        </div>
      ) : isAllError ? (
        <div className="py-10 text-center text-sm text-destructive">
          فشل في تحميل التحديات. حاول لاحقاً.
        </div>
      ) : (
        <Tabs defaultValue="all">
          <TabsList>
            <TabsTrigger value="all">الكل</TabsTrigger>
            <TabsTrigger value="daily">قصير (١-٣ أيام)</TabsTrigger>
            <TabsTrigger value="weekly">متوسط (أسبوع)</TabsTrigger>
            <TabsTrigger value="monthly">طويل (شهر)</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-6">
            <Section
              items={availableChallenges}
              searchQuery={searchQuery}
              activeTag={activeTag}
              onEnroll={(id) => enrollMutation.mutate(id)}
              isEnrolling={enrollMutation.isPending}
            />
          </TabsContent>
          <TabsContent value="daily" className="mt-6">
            <Section
              items={daily}
              searchQuery={searchQuery}
              activeTag={activeTag}
              onEnroll={(id) => enrollMutation.mutate(id)}
              isEnrolling={enrollMutation.isPending}
            />
          </TabsContent>
          <TabsContent value="weekly" className="mt-6">
            <Section
              items={weekly}
              searchQuery={searchQuery}
              activeTag={activeTag}
              onEnroll={(id) => enrollMutation.mutate(id)}
              isEnrolling={enrollMutation.isPending}
            />
          </TabsContent>
          <TabsContent value="monthly" className="mt-6">
            <Section
              items={monthly}
              searchQuery={searchQuery}
              activeTag={activeTag}
              onEnroll={(id) => enrollMutation.mutate(id)}
              isEnrolling={enrollMutation.isPending}
            />
          </TabsContent>
        </Tabs>
      )}
    </AppShell>
  );
}
