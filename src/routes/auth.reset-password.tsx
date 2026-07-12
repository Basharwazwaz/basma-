import { createFileRoute, Link, useSearch } from "@tanstack/react-router";
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError } from "@/lib/api";
import { toast } from "sonner";
import { Lock, ArrowRight, CheckCircle2, Loader2 } from "lucide-react";

export const Route = createFileRoute("/auth/reset-password")({
  head: () => ({
    meta: [
      { title: "إعادة تعيين كلمة المرور | بصمة+" },
    ],
  }),
  validateSearch: (search: Record<string, unknown>) => ({
    token: (search.token as string) ?? "",
  }),
  component: ResetPassword,
});

function ResetPassword() {
  const { token } = Route.useSearch();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!token) {
    return (
      <div className="gradient-warm flex min-h-screen items-center justify-center px-4 py-12">
        <Card className="p-8 text-center shadow-glow">
          <h1 className="text-xl font-bold">رابط غير صالح</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            يبدو أن رابط إعادة التعيين غير صحيح أو منتهي الصلاحية.
          </p>
          <Button asChild className="mt-4 gradient-primary shadow-soft">
            <Link to="/auth/forgot-password">طلب رابط جديد</Link>
          </Button>
        </Card>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!password) {
      setError("يرجى إدخال كلمة المرور الجديدة.");
      return;
    }
    if (password.length < 8) {
      setError("كلمة المرور يجب أن تكون ٨ أحرف على الأقل.");
      return;
    }
    if (!/[A-Z]/.test(password)) {
      setError("يجب أن تحتوي كلمة المرور على حرف كبير على الأقل.");
      return;
    }
    if (!/[0-9]/.test(password)) {
      setError("يجب أن تحتوي كلمة المرور على رقم على الأقل.");
      return;
    }
    if (password !== confirm) {
      setError("كلمتا المرور غير متطابقتين.");
      return;
    }

    setLoading(true);
    try {
      const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
      const response = await fetch(`${BASE_URL}/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: password }),
      });

      if (!response.ok) {
        const err = await response.json().catch(() => null);
        throw new ApiError(response.status, err?.detail ?? "حدث خطأ");
      }

      setDone(true);
      toast.success("تم إعادة تعيين كلمة المرور بنجاح!");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("حدث خطأ غير متوقع. حاول مرة أخرى.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="gradient-warm flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <Link to="/" className="mb-6 flex items-center justify-center gap-2.5">
          <img src="/logo-icon.png" alt="بصمة+" className="h-10 w-10 object-contain" />
          <span className="text-xl font-extrabold">بصمة+</span>
        </Link>
        <Card className="p-8 shadow-glow">
          {done ? (
            <div className="text-center">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-success/10">
                <CheckCircle2 className="h-8 w-8 text-success" />
              </div>
              <h1 className="mt-4 text-2xl font-bold">تم بنجاح!</h1>
              <p className="mt-2 text-sm text-muted-foreground">
                يمكنك الآن تسجيل الدخول بكلمة المرور الجديدة.
              </p>
              <Button asChild className="mt-6 gradient-primary shadow-soft">
                <Link to="/auth/login">
                  <ArrowRight className="ms-2 h-4 w-4" />
                  تسجيل الدخول
                </Link>
              </Button>
            </div>
          ) : (
            <>
              <div className="mb-6 flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10">
                  <Lock className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold">كلمة مرور جديدة</h1>
                  <p className="mt-0.5 text-sm text-muted-foreground">
                    أدخل كلمة المرور الجديدة لحسابك.
                  </p>
                </div>
              </div>

              <form className="space-y-4" onSubmit={handleSubmit} noValidate>
                <div className="space-y-2">
                  <Label htmlFor="rp-pass">كلمة المرور الجديدة</Label>
                  <Input
                    id="rp-pass"
                    type="password"
                    placeholder="6 أحرف على الأقل"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoFocus
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="rp-confirm">تأكيد كلمة المرور</Label>
                  <Input
                    id="rp-confirm"
                    type="password"
                    placeholder="أعد إدخال كلمة المرور"
                    value={confirm}
                    onChange={(e) => setConfirm(e.target.value)}
                  />
                </div>

                {error && (
                  <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
                    {error}
                  </p>
                )}

                <Button
                  type="submit"
                  className="gradient-primary w-full shadow-soft"
                  disabled={loading}
                >
                  {loading ? (
                    <Loader2 className="ms-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Lock className="ms-2 h-4 w-4" />
                  )}
                  {loading ? "جارٍ الحفظ…" : "إعادة تعيين كلمة المرور"}
                </Button>
              </form>
            </>
          )}
        </Card>
      </div>
    </div>
  );
}
