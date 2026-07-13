import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Loader2, Shield, Users, AlertTriangle, BookOpen, Plus, Pencil, Trash2, PackageOpen } from "lucide-react";
import {
  apiAdminGetUsers,
  apiAdminGetUserCount,
  apiAdminDeactivateUser,
  apiAdminGetContent,
  apiAdminCreateContent,
  apiAdminUpdateContent,
  apiAdminDeleteContent,
  apiAdminSeedContent,
  type AdminContentData,
  type AdminContentPayload,
} from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { useT } from "@/i18n/use-t";
import { toast } from "sonner";
import { useEffect } from "react";

export const Route = createFileRoute("/admin")({
  head: () => ({ meta: [{ title: "لوحة الإدارة | بصمة+" }] }),
  component: Admin,
});

const CONTENT_TYPES = ["COURSE", "ARTICLE", "VIDEO", "BOOK"] as const;
const DIFFICULTY_LEVELS = ["BEGINNER", "INTERMEDIATE", "ADVANCED"] as const;

const defaultContentForm: AdminContentPayload = {
  title: "",
  description: "",
  content_type: "COURSE",
  url: "",
  category: "",
  difficulty: "BEGINNER",
  estimated_minutes: undefined,
  tags: [],
};

function Admin() {
  const { t, currentLanguage } = useT();
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<"users" | "content">("users");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState<AdminContentPayload>({ ...defaultContentForm });

  useEffect(() => {
    if (user && user.role !== "ADMIN") {
      navigate({ to: "/dashboard" });
    }
  }, [user, navigate]);

  const { data: users, isLoading: usersLoading } = useQuery({
    queryKey: ["admin", "users"],
    queryFn: apiAdminGetUsers,
    enabled: user?.role === "ADMIN",
  });

  const { data: countData } = useQuery({
    queryKey: ["admin", "count"],
    queryFn: apiAdminGetUserCount,
    enabled: user?.role === "ADMIN",
  });

  const { data: content, isLoading: contentLoading } = useQuery({
    queryKey: ["admin", "content"],
    queryFn: apiAdminGetContent,
    enabled: user?.role === "ADMIN",
  });

  const deactivateMutation = useMutation({
    mutationFn: (userId: string) => apiAdminDeactivateUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      toast.success(currentLanguage === "ar" ? "تم تعطيل المستخدم" : "User deactivated");
    },
    onError: () => {
      toast.error(currentLanguage === "ar" ? "فشل تعطيل المستخدم" : "Failed to deactivate user");
    },
  });

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (editId) {
        return apiAdminUpdateContent(editId, form);
      }
      return apiAdminCreateContent(form);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "content"] });
      toast.success(t("admin.saved"));
      setDialogOpen(false);
      setForm({ ...defaultContentForm });
      setEditId(null);
    },
    onError: () => {
      toast.error(currentLanguage === "ar" ? "فشل حفظ المحتوى" : "Failed to save content");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiAdminDeleteContent(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "content"] });
      toast.success(t("admin.deleted"));
    },
    onError: () => {
      toast.error(currentLanguage === "ar" ? "فشل حذف المحتوى" : "Failed to delete content");
    },
  });

  const seedMutation = useMutation({
    mutationFn: () => apiAdminSeedContent(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["admin", "content"] });
      toast.success(data.message.includes("exists") ? t("admin.seedExists") : t("admin.seedSuccess"));
    },
    onError: () => {
      toast.error(currentLanguage === "ar" ? "فشل بذر المحتوى" : "Failed to seed content");
    },
  });

  function openAdd() {
    setEditId(null);
    setForm({ ...defaultContentForm });
    setDialogOpen(true);
  }

  function openEdit(item: AdminContentData) {
    setEditId(item.id);
    setForm({
      title: item.title,
      description: item.description ?? "",
      content_type: item.content_type,
      url: item.url ?? "",
      category: item.category ?? "",
      difficulty: item.difficulty ?? "BEGINNER",
      estimated_minutes: item.estimated_minutes ?? undefined,
      tags: [],
    });
    setDialogOpen(true);
  }

  function confirmDelete(id: string, title: string) {
    if (confirm(`${t("admin.deleteConfirm")}\n\n"${title}"`)) {
      deleteMutation.mutate(id);
    }
  }

  if (user?.role !== "ADMIN") return null;

  const activeUsers = users?.filter((u) => u.is_active) ?? [];
  const inactiveUsers = users?.filter((u) => !u.is_active) ?? [];

  const typeLabel: Record<string, string> = {
    COURSE: t("admin.course"),
    ARTICLE: t("admin.article"),
    VIDEO: t("admin.video"),
    BOOK: t("admin.book"),
  };

  const diffLabel: Record<string, string> = {
    BEGINNER: t("admin.beginner"),
    INTERMEDIATE: t("admin.intermediate"),
    ADVANCED: t("admin.advanced"),
  };

  return (
    <AppShell title={t("admin.title")} subtitle={t("admin.adminPanel")}>
      <div className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-3">
          <Card className="p-4 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
              <Users className="h-5 w-5 text-primary" />
            </div>
            <div>
              <div className="text-2xl font-bold">{countData?.total_users ?? "—"}</div>
              <div className="text-xs text-muted-foreground">{t("admin.totalUsers")}</div>
            </div>
          </Card>
          <Card className="p-4 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-500/10">
              <Shield className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">{activeUsers.length}</div>
              <div className="text-xs text-muted-foreground">{t("admin.active")}</div>
            </div>
          </Card>
          <Card className="p-4 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-500/10">
              <BookOpen className="h-5 w-5 text-amber-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">{content?.length ?? "—"}</div>
              <div className="text-xs text-muted-foreground">{t("admin.contentTab")}</div>
            </div>
          </Card>
        </div>

        <div className="flex gap-1 border-b">
          <button
            onClick={() => setTab("users")}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === "users" ? "border-primary text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {t("admin.usersTab")}
          </button>
          <button
            onClick={() => setTab("content")}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === "content" ? "border-primary text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {t("admin.contentTab")}
          </button>
        </div>

        {tab === "users" && (
          <Card>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-muted-foreground">
                    <th className="p-3 text-right font-medium">{t("admin.email")}</th>
                    <th className="p-3 text-right font-medium">{t("admin.role")}</th>
                    <th className="p-3 text-right font-medium">{t("admin.status")}</th>
                    <th className="p-3 text-right font-medium">{t("admin.actions")}</th>
                  </tr>
                </thead>
                <tbody>
                  {usersLoading ? (
                    <tr>
                      <td colSpan={4} className="p-8 text-center">
                        <Loader2 className="mx-auto h-5 w-5 animate-spin text-muted-foreground" />
                      </td>
                    </tr>
                  ) : !users?.length ? (
                    <tr>
                      <td colSpan={4} className="p-8 text-center text-muted-foreground">
                        {currentLanguage === "ar" ? "لا يوجد مستخدمون" : "No users found"}
                      </td>
                    </tr>
                  ) : (
                    users.map((u) => (
                      <tr key={u.id} className="border-b last:border-0 hover:bg-muted/50">
                        <td className="p-3">{u.email}</td>
                        <td className="p-3">
                          <Badge variant={u.role === "ADMIN" ? "default" : "secondary"}>{u.role}</Badge>
                        </td>
                        <td className="p-3">
                          <Badge variant={u.is_active ? "success" : "destructive"}>
                            {u.is_active ? t("admin.active") : t("admin.inactive")}
                          </Badge>
                        </td>
                        <td className="p-3">
                          {u.is_active && u.role !== "ADMIN" && (
                            <Button
                              variant="outline"
                              size="sm"
                              className="text-destructive border-destructive/30 hover:bg-destructive/10"
                              onClick={() => deactivateMutation.mutate(u.id)}
                              disabled={deactivateMutation.isPending}
                            >
                              {t("admin.deactivate")}
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {tab === "content" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex gap-2">
                <Button onClick={openAdd} size="sm">
                  <Plus className="h-4 w-4 ms-1" />
                  {t("admin.createContent")}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => seedMutation.mutate()}
                  disabled={seedMutation.isPending}
                >
                  <PackageOpen className="h-4 w-4 ms-1" />
                  {t("admin.seed")}
                </Button>
              </div>
            </div>

            <Card>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-muted-foreground">
                      <th className="p-3 text-right font-medium">{t("admin.titleField")}</th>
                      <th className="p-3 text-right font-medium">{t("admin.type")}</th>
                      <th className="p-3 text-right font-medium">{t("admin.category")}</th>
                      <th className="p-3 text-right font-medium">{t("admin.difficulty")}</th>
                      <th className="p-3 text-right font-medium">{t("admin.actions")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {contentLoading ? (
                      <tr>
                        <td colSpan={5} className="p-8 text-center">
                          <Loader2 className="mx-auto h-5 w-5 animate-spin text-muted-foreground" />
                        </td>
                      </tr>
                    ) : !content?.length ? (
                      <tr>
                        <td colSpan={5} className="p-8 text-center text-muted-foreground">
                          {t("admin.noContent")}
                        </td>
                      </tr>
                    ) : (
                      content.map((c) => (
                        <tr key={c.id} className="border-b last:border-0 hover:bg-muted/50">
                          <td className="p-3 font-medium max-w-[200px] truncate">{c.title}</td>
                          <td className="p-3">
                            <Badge variant="outline">{typeLabel[c.content_type] ?? c.content_type}</Badge>
                          </td>
                          <td className="p-3 text-muted-foreground">{c.category ?? "—"}</td>
                          <td className="p-3">
                            {c.difficulty && (
                              <Badge variant="secondary">{diffLabel[c.difficulty] ?? c.difficulty}</Badge>
                            )}
                          </td>
                          <td className="p-3">
                            <div className="flex gap-1">
                              <Button variant="ghost" size="sm" onClick={() => openEdit(c)}>
                                <Pencil className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-destructive hover:bg-destructive/10"
                                onClick={() => confirmDelete(c.id, c.title)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        )}
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{editId ? t("admin.editTitle") : t("admin.addTitle")}</DialogTitle>
            <DialogDescription>
              {currentLanguage === "ar"
                ? "أدخل بيانات المحتوى التعليمي"
                : "Enter learning content details"}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>{t("admin.titleField")}</Label>
              <Input
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label>{t("admin.description")}</Label>
              <Textarea
                value={form.description ?? ""}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{t("admin.type")}</Label>
                <Select
                  value={form.content_type}
                  onValueChange={(v) => setForm({ ...form, content_type: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {CONTENT_TYPES.map((ct) => (
                      <SelectItem key={ct} value={ct}>
                        {typeLabel[ct]}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>{t("admin.category")}</Label>
                <Input
                  value={form.category ?? ""}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{t("admin.difficulty")}</Label>
                <Select
                  value={form.difficulty ?? "BEGINNER"}
                  onValueChange={(v) => setForm({ ...form, difficulty: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {DIFFICULTY_LEVELS.map((d) => (
                      <SelectItem key={d} value={d}>
                        {diffLabel[d]}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>{t("admin.estimatedMinutes")}</Label>
                <Input
                  type="number"
                  value={form.estimated_minutes ?? ""}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      estimated_minutes: e.target.value ? parseInt(e.target.value) : undefined,
                    })
                  }
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>{t("admin.url")}</Label>
              <Input
                dir="ltr"
                value={form.url ?? ""}
                onChange={(e) => setForm({ ...form, url: e.target.value })}
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                {t("common.cancel")}
              </Button>
              <Button onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending || !form.title}>
                {saveMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin ms-1" />
                ) : null}
                {t("admin.save")}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
