import { createFileRoute } from "@tanstack/react-router";
import { useState, useRef, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { X, Loader2 } from "lucide-react";
import { useTheme } from "@/hooks/use-theme";
import {
  apiUpdateProfile,
  apiUpdateSettings,
  apiDeleteAccount,
  apiExportData,
  type ProfileUpdatePayload,
  type SettingsPayload,
} from "@/lib/api";
import { useAuth, PROFILE_QUERY_KEY } from "@/hooks/use-auth";
import { useNavigate } from "@tanstack/react-router";
import { toast } from "sonner";

export const Route = createFileRoute("/profile")({
  head: () => ({ meta: [{ title: "الملف الشخصي | بصمة+" }] }),
  component: Profile,
});

function ProfileSkeleton() {
  return (
    <AppShell title="الملف الشخصي" subtitle="إدارة بياناتك وتفضيلاتك.">
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="p-6 lg:col-span-2 space-y-4">
          <div className="flex items-center gap-4">
            <Skeleton className="h-20 w-20 rounded-full" />
            <div className="space-y-2">
              <Skeleton className="h-5 w-32" />
              <Skeleton className="h-4 w-48" />
            </div>
          </div>
          <Skeleton className="h-px w-full" />
          <div className="grid gap-4 sm:grid-cols-2">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full rounded-md" />
            ))}
          </div>
        </Card>
        <div className="space-y-6">
          <Card className="p-5 space-y-3">
            <Skeleton className="h-5 w-24" />
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-4 w-full" />
            ))}
          </Card>
        </div>
      </div>
    </AppShell>
  );
}

const ALL_INTERESTS = ["رياضة", "ألعاب", "تقنية", "موسيقى", "تصميم", "أعمال", "قراءة", "سفر"];

function Profile() {
  const { isDark, toggle: toggleTheme } = useTheme();
  const { user, isLoading } = useAuth();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  // ── Derive initial form state from server data ─────────────────
  const profile = user?.profile;
  const fullName = [profile?.first_name, profile?.last_name].filter(Boolean).join(" ");
  const initials = profile?.first_name?.[0] ?? user?.email?.[0]?.toUpperCase() ?? "؟";

  const [firstName, setFirstName] = useState(profile?.first_name ?? "");
  const [lastName, setLastName] = useState(profile?.last_name ?? "");
  const [city, setCity] = useState(profile?.city ?? "");
  const [major, setMajor] = useState(profile?.major ?? "");
  const [age, setAge] = useState(profile?.age?.toString() ?? "");
  const [interests, setInterests] = useState<string[]>(profile?.interests ?? []);
  const [notifications, setNotifications] = useState(profile?.notifications_enabled ?? true);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Sync form when data arrives from server
  useEffect(() => {
    if (profile) {
      if (profile.first_name) setFirstName(profile.first_name);
      if (profile.last_name) setLastName(profile.last_name);
      if (profile.city) setCity(profile.city);
      if (profile.major) setMajor(profile.major);
      if (profile.age) setAge(String(profile.age));
    }
  }, [profile]);

  // ── Mutations ──────────────────────────────────────────────────
  const updateProfileMutation = useMutation({
    mutationFn: (payload: ProfileUpdatePayload) => apiUpdateProfile(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PROFILE_QUERY_KEY });
      toast.success("تم حفظ التغييرات ✓");
    },
    onError: () => {
      toast.error("فشل حفظ التغييرات. حاول مرة أخرى.");
    },
  });

  const updateSettingsMutation = useMutation({
    mutationFn: (payload: SettingsPayload) => apiUpdateSettings(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PROFILE_QUERY_KEY });
    },
    onError: () => toast.error("فشل تحديث الإعدادات. حاول مرة أخرى."),
  });

  const deleteAccountMutation = useMutation({
    mutationFn: apiDeleteAccount,
    onSuccess: () => {
      queryClient.clear();
      toast.success("تم حذف الحساب بنجاح");
      navigate({ to: "/" });
    },
    onError: () => {
      toast.error("فشل حذف الحساب. حاول مرة أخرى.");
    },
  });

  const exportDataMutation = useMutation({
    mutationFn: apiExportData,
    onSuccess: (data) => {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `basma-profile-${new Date().toISOString().split("T")[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("تم تصدير البيانات بنجاح");
    },
    onError: () => {
      toast.error("فشل تصدير البيانات.");
    },
  });

  const handleSaveProfile = () => {
    updateProfileMutation.mutate({
      first_name: firstName || undefined,
      last_name: lastName || undefined,
      age: age ? Number(age) : undefined,
      city: city || undefined,
      major: major || undefined,
      interests,
    });
  };

  const handleNotificationsToggle = (checked: boolean) => {
    setNotifications(checked);
    updateSettingsMutation.mutate({ notifications_enabled: checked });
  };

  const handleLanguageChange = (lang: string) => {
    updateSettingsMutation.mutate({ language: lang });
  };

  const removeInterest = (i: string) => {
    setInterests((prev) => prev.filter((x) => x !== i));
  };

  const addInterest = (i: string) => {
    if (!interests.includes(i)) setInterests((prev) => [...prev, i]);
  };

  if (isLoading) return <ProfileSkeleton />;

  return (
    <AppShell title="الملف الشخصي" subtitle="إدارة بياناتك وتفضيلاتك.">
      <div className="grid gap-6 lg:grid-cols-3">
        {/* ── Left / main card ─────────────────────────────────── */}
        <Card className="p-6 lg:col-span-2">
          <div className="mb-6 flex items-center gap-4">
            <div className="relative">
              <Avatar className="h-20 w-20">
                {avatarPreview ? (
                  <img
                    src={avatarPreview}
                    alt="الصورة الشخصية"
                    className="h-full w-full rounded-full object-cover"
                  />
                ) : null}
                <AvatarFallback className="gradient-primary text-2xl text-primary-foreground">
                  {initials}
                </AvatarFallback>
              </Avatar>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    if (file.size > 2 * 1024 * 1024) {
                      toast.error("الصورة يجب أن تكون أقل من 2 ميغابايت");
                      return;
                    }
                    const reader = new FileReader();
                    reader.onload = () => setAvatarPreview(reader.result as string);
                    reader.readAsDataURL(file);
                  }
                }}
              />
            </div>
            <div>
              <h2 className="text-xl font-bold">{fullName || user?.email}</h2>
              <p className="text-sm text-muted-foreground">
                {major ? `${major} · ` : ""}
                {profile?.points ?? 0} نقطة
              </p>
              <Button
                variant="outline"
                size="sm"
                className="mt-2"
                onClick={() => fileInputRef.current?.click()}
              >
                تغيير الصورة
              </Button>
            </div>
          </div>
          <Separator />
          <h3 className="mt-6 mb-4 font-bold">المعلومات الشخصيّة</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="p-first-name">الاسم الأول</Label>
              <Input
                id="p-first-name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="p-last-name">اسم العائلة</Label>
              <Input
                id="p-last-name"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="p-email">البريد</Label>
              <Input id="p-email" dir="ltr" value={user?.email ?? ""} readOnly disabled />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="p-city">المدينة</Label>
              <Input id="p-city" value={city} onChange={(e) => setCity(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="p-major">التخصص</Label>
              <Input id="p-major" value={major} onChange={(e) => setMajor(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="p-age">العمر</Label>
              <Input
                id="p-age"
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
              />
            </div>
          </div>

          {/* Interests */}
          <h3 className="mt-6 mb-3 font-bold">الاهتمامات</h3>
          <div className="flex flex-wrap gap-2">
            {interests.map((i) => (
              <Badge key={i} variant="secondary" className="gap-1 py-1.5 ps-3 pe-2">
                {i}
                <button
                  onClick={() => removeInterest(i)}
                  className="rounded-full p-0.5 transition hover:bg-foreground/10"
                  aria-label={`إزالة ${i}`}
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
          {/* Add interest picker */}
          <div className="mt-2 flex flex-wrap gap-1.5">
            {ALL_INTERESTS.filter((i) => !interests.includes(i)).map((i) => (
              <button
                key={i}
                onClick={() => addInterest(i)}
                className="rounded-full border px-3 py-1 text-xs hover:border-primary hover:bg-muted transition-all"
              >
                + {i}
              </button>
            ))}
          </div>

          <div className="mt-6 flex gap-3">
            <Button
              className="gradient-primary shadow-soft"
              onClick={handleSaveProfile}
              disabled={updateProfileMutation.isPending}
            >
              {updateProfileMutation.isPending ? (
                <>
                  <Loader2 className="me-1 h-4 w-4 animate-spin" />
                  جارٍ الحفظ…
                </>
              ) : (
                "حفظ التغييرات"
              )}
            </Button>
            <Button
              variant="ghost"
              onClick={() => {
                setFirstName(profile?.first_name ?? "");
                setLastName(profile?.last_name ?? "");
                setCity(profile?.city ?? "");
                setMajor(profile?.major ?? "");
                setAge(profile?.age?.toString() ?? "");
                setInterests(profile?.interests ?? []);
              }}
            >
              إلغاء
            </Button>
          </div>
        </Card>

        {/* ── Right sidebar ─────────────────────────────────────── */}
        <div className="space-y-6">
          {/* Settings card */}
          <Card className="p-5">
            <h3 className="mb-3 font-bold">الإعدادات</h3>
            <div className="space-y-4 text-sm">
              <div className="flex items-center justify-between">
                <span>الوضع الداكن</span>
                <Switch
                  id="dark-mode-switch"
                  checked={isDark}
                  onCheckedChange={(checked) => {
                    toggleTheme();
                    updateSettingsMutation.mutate({
                      theme: checked ? "dark" : "light",
                    });
                  }}
                />
              </div>
              <div className="flex items-center justify-between">
                <span>إشعارات يوميّة</span>
                <Switch
                  id="notifications-switch"
                  checked={notifications}
                  onCheckedChange={handleNotificationsToggle}
                />
              </div>
              <div className="space-y-1.5">
                <Label>اللغة</Label>
                <Select
                  defaultValue={profile?.language ?? "ar"}
                  onValueChange={handleLanguageChange}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ar">العربية</SelectItem>
                    <SelectItem value="en">English (قريبًا)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </Card>

          {/* Danger zone */}
          <Card className="border-destructive/30 bg-destructive/5 p-5">
            <h3 className="mb-2 font-bold text-destructive">منطقة حسّاسة</h3>
            <p className="mb-3 text-xs text-muted-foreground">
              يمكنك تصدير بياناتك أو حذف حسابك في أي وقت.
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => exportDataMutation.mutate()}
                disabled={exportDataMutation.isPending}
              >
                {exportDataMutation.isPending ? (
                  <Loader2 className="ms-1 h-3 w-3 animate-spin" />
                ) : null}
                تصدير البيانات
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => {
                  if (
                    window.confirm("هل أنت متأكد من حذف حسابك؟ هذا الإجراء لا يمكن التراجع عنه.")
                  ) {
                    deleteAccountMutation.mutate();
                  }
                }}
                disabled={deleteAccountMutation.isPending}
              >
                {deleteAccountMutation.isPending ? (
                  <Loader2 className="ms-1 h-3 w-3 animate-spin" />
                ) : null}
                حذف الحساب
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
