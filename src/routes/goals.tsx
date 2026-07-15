import { createFileRoute } from "@tanstack/react-router";
import { useState, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import {
  Plus,
  Target,
  CheckCircle2,
  Calendar,
  X,
  Pause,
  Play,
  AlertCircle,
  Loader2,
  Minus,
} from "lucide-react";
import { apiGetGoals, apiCreateGoal, apiUpdateGoal, apiDeleteGoal } from "@/lib/api";
import { toast } from "sonner";

export const Route = createFileRoute("/goals")({
  head: () => ({ meta: [{ title: "الأهداف | بصمة+" }] }),
  component: Goals,
});

const GOALS_QUERY_KEY = ["goals"];

function Goals() {
  const queryClient = useQueryClient();
  const { data: goals = [], isLoading } = useQuery({
    queryKey: GOALS_QUERY_KEY,
    queryFn: apiGetGoals,
  });

  const formRef = useRef<HTMLDivElement>(null);
  const [showForm, setShowForm] = useState(false);

  // Form state
  const [title, setTitle] = useState("");
  const [target, setTarget] = useState("");
  const [unit, setUnit] = useState(""); // We map unit to description for now or store it differently, but the schema has category and description.
  const [deadline, setDeadline] = useState("");
  const [formError, setFormError] = useState("");

  const createGoalMutation = useMutation({
    mutationFn: apiCreateGoal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GOALS_QUERY_KEY });
      setTitle("");
      setTarget("");
      setUnit("");
      setDeadline("");
      setFormError("");
      toast.success("تم إضافة الهدف بنجاح ✓");
    },
    onError: () => {
      setFormError("فشل حفظ الهدف، حاول مرة أخرى.");
    },
  });

  const updateGoalMutation = useMutation({
    mutationFn: ({
      id,
      ...payload
    }: {
      id: string;
      status?: "NOT_STARTED" | "IN_PROGRESS" | "COMPLETED" | "ABANDONED";
    }) => apiUpdateGoal(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: GOALS_QUERY_KEY }),
    onError: () => toast.error("فشل تحديث الهدف. حاول مرة أخرى."),
  });

  const deleteGoalMutation = useMutation({
    mutationFn: apiDeleteGoal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GOALS_QUERY_KEY });
      toast.success("تم حذف الهدف");
    },
    onError: () => toast.error("فشل حذف الهدف. حاول مرة أخرى."),
  });

  function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) {
      setFormError("أدخل عنوان الهدف");
      return;
    }
    // Note: Since DB doesn't have a 'unit' and 'target' scalar natively besides progress_percent,
    // we can encode the target info into description for the UI to parse later, or just save it in description.
    const descriptionStr = JSON.stringify({ tgt: Number(target) || 100, unit: unit.trim() || "٪" });

    createGoalMutation.mutate({
      title: title.trim(),
      description: descriptionStr,
      target_date: deadline || undefined,
      status: "IN_PROGRESS",
    });
  }

  function deleteGoal(id: string) {
    deleteGoalMutation.mutate(id);
  }

  function togglePause(id: string, currentStatus: string) {
    const newStatus = currentStatus === "IN_PROGRESS" ? "NOT_STARTED" : "IN_PROGRESS";
    updateGoalMutation.mutate({
      id,
      status: newStatus as "NOT_STARTED" | "IN_PROGRESS" | "COMPLETED" | "ABANDONED",
    });
  }

  function adjustProgress(id: string, current: number, delta: number) {
    const next = Math.max(0, Math.min(100, current + delta));
    updateGoalMutation.mutate({ id, progress_percent: next });
  }

  function completeGoal(id: string) {
    updateGoalMutation.mutate({ id, progress_percent: 100, status: "COMPLETED" });
  }

  // Derived state
  const activeGoals = goals.filter((g) => g.status !== "COMPLETED" && g.status !== "ABANDONED");
  const completedGoals = goals.filter((g) => g.status === "COMPLETED");

  const parseDescription = (desc: string | null) => {
    try {
      if (!desc) return { tgt: 100, unit: "٪" };
      return JSON.parse(desc);
    } catch {
      return { tgt: 100, unit: "٪" };
    }
  };

  return (
    <AppShell title="الأهداف" subtitle="حدّد أهدافك وتابع تقدّمك خطوة بخطوة.">
      <div className="grid gap-6 xl:grid-cols-[1fr_320px]">
        {/* Goals list */}
        <div className="space-y-4">
          {isLoading ? (
            <div className="flex justify-center py-10">
              <Loader2 className="animate-spin text-muted-foreground" />
            </div>
          ) : activeGoals.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed py-16 text-center">
              <Target className="mb-3 h-10 w-10 text-muted-foreground/40" />
              <p className="font-semibold text-muted-foreground">لا توجد أهداف نشطة</p>
              <p className="mt-1 text-sm text-muted-foreground/70">أضف هدفك الأول من النموذج</p>
            </div>
          ) : (
            activeGoals.map((g) => {
              const paused = g.status === "NOT_STARTED";
              const { tgt, unit } = parseDescription(g.description);

              return (
                <Card key={g.id} className={`p-5 transition-all ${paused ? "opacity-60" : ""}`}>
                  <div className="mb-3 flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <div className="gradient-warm flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-primary">
                        <Target className="h-5 w-5" />
                      </div>
                      <div>
                        <h3 className="font-bold leading-snug">{g.title}</h3>
                        <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                          <Calendar className="h-3.5 w-3.5" />
                          <span>الموعد: {g.target_date || "—"}</span>
                          {paused && (
                            <Badge variant="secondary" className="text-[10px]">
                              متوقف
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-1 shrink-0">
                      <Badge variant="secondary">{g.progress_percent}٪</Badge>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-muted-foreground hover:text-foreground"
                        title={paused ? "استئناف" : "إيقاف مؤقت"}
                        onClick={() => togglePause(g.id, g.status)}
                        disabled={updateGoalMutation.isPending}
                      >
                        {paused ? (
                          <Play className="h-3.5 w-3.5" />
                        ) : (
                          <Pause className="h-3.5 w-3.5" />
                        )}
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-muted-foreground hover:text-destructive"
                        title="حذف الهدف"
                        onClick={() => deleteGoal(g.id)}
                        disabled={deleteGoalMutation.isPending}
                      >
                        <X className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>

                  <Progress value={g.progress_percent} className="h-2" />
                  <div className="mt-2 flex items-center justify-between gap-2 text-sm">
                    <span className="text-muted-foreground">
                      الإنجاز: {Math.round((g.progress_percent / 100) * tgt)} {unit}
                    </span>
                    <div className="flex items-center gap-1">
                      {g.progress_percent < 100 && (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            className="h-7 px-2 text-xs"
                            onClick={() => adjustProgress(g.id, g.progress_percent, 10)}
                            disabled={updateGoalMutation.isPending}
                          >+10%</Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="h-7 px-2 text-xs"
                            onClick={() => adjustProgress(g.id, g.progress_percent, 25)}
                            disabled={updateGoalMutation.isPending}
                          >+25%</Button>
                          <Button
                            variant="default"
                            size="sm"
                            className="h-7 px-2 text-xs"
                            onClick={() => completeGoal(g.id)}
                            disabled={updateGoalMutation.isPending}
                          ><CheckCircle2 className="h-3 w-3 ml-1" />إكمال</Button>
                        </>
                      )}
                      {g.progress_percent > 0 && (
                        <Button
                          variant="outline"
                          size="sm"
                          className="h-7 w-7 p-0"
                          onClick={() => adjustProgress(g.id, g.progress_percent, -10)}
                          disabled={updateGoalMutation.isPending}
                        ><Minus className="h-3 w-3" /></Button>
                      )}
                    </div>
                  </div>
                </Card>
              );
            })
          )}

          {/* Completed */}
          {completedGoals.length > 0 && (
            <Card className="p-5">
              <h3 className="mb-4 flex items-center gap-2 font-bold">
                <CheckCircle2 className="h-5 w-5 text-success" /> أهداف مُحقّقة
              </h3>
              <div className="space-y-2">
                {completedGoals.map((g) => (
                  <div
                    key={g.id}
                    className="flex items-center justify-between rounded-lg border bg-muted/30 p-3 text-sm"
                  >
                    <span>{g.title}</span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(g.updated_at).toLocaleDateString("ar-SA")}
                    </span>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        {/* Add goal form */}
        <Card ref={formRef} className="h-fit p-5 shadow-soft scroll-mt-24">
          <button
            type="button"
            onClick={() => setShowForm(!showForm)}
            className="mb-4 flex w-full items-center justify-between gap-2 font-bold"
          >
            <span className="flex items-center gap-2">
              <Plus className="h-4 w-4" /> هدف جديد
            </span>
            <span className="text-xs text-muted-foreground lg:hidden">
              {showForm ? "إخفاء" : "إضافة"}
            </span>
          </button>
          <div className={`xl:block ${showForm ? "block" : "hidden"}`}>
          <form className="space-y-3" onSubmit={handleAdd}>
            <div className="space-y-1.5">
              <Label htmlFor="goal-title">العنوان</Label>
              <Input
                id="goal-title"
                placeholder="مثل: قراءة ٢٠ دقيقة يوميًا"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label htmlFor="goal-target">القيمة المستهدفة</Label>
                <Input
                  id="goal-target"
                  type="number"
                  placeholder="٢٠"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="goal-unit">الوحدة</Label>
                <Input
                  id="goal-unit"
                  placeholder="دقيقة"
                  value={unit}
                  onChange={(e) => setUnit(e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="goal-deadline">الموعد النهائي</Label>
              <Input
                id="goal-deadline"
                type="date"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
              />
            </div>

            {formError && (
              <div className="flex items-center gap-2 rounded-lg bg-destructive/10 px-3 py-2 text-xs text-destructive">
                <AlertCircle className="h-3.5 w-3.5 shrink-0" />
                {formError}
              </div>
            )}

            <Button
              type="submit"
              className="w-full gradient-primary shadow-soft"
              disabled={createGoalMutation.isPending}
            >
              {createGoalMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                "أضف الهدف"
              )}
            </Button>
          </form>
          </div>
        </Card>

        {/* Floating add button on mobile */}
        {!showForm && (
          <button
            onClick={() => { setShowForm(true); formRef.current?.scrollIntoView({ behavior: "smooth" }); }}
            className="fixed bottom-6 left-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-xl xl:hidden hover:bg-primary/90 transition-all"
            aria-label="إضافة هدف"
          >
            <Plus className="h-6 w-6" />
          </button>
        )}
      </div>
    </AppShell>
  );
}
