import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { useAuth } from "@/hooks/use-auth";
import { ApiError } from "@/lib/api";
import { toast } from "sonner";

export const Route = createFileRoute("/auth/login")({
  head: () => ({
    meta: [
      { title: "تسجيل الدخول | بصمة+" },
      { name: "description", content: "ادخل إلى حسابك في بصمة+ وتابع رحلتك." },
    ],
  }),
  component: Login,
});

function Login() {
  const { login } = useAuth();
  const [email, setEmail] = useState(() => localStorage.getItem("basma_remember_email") ?? "");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(() => !!localStorage.getItem("basma_remember_email"));
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email || !password) {
      setError("يرجى تعبئة البريد الإلكتروني وكلمة المرور.");
      return;
    }

    try {
      await login.mutateAsync({ email, password });
      if (remember) {
        localStorage.setItem("basma_remember_email", email);
      } else {
        localStorage.removeItem("basma_remember_email");
      }
      // Navigation is handled inside useAuth on success
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          setError("البريد الإلكتروني أو كلمة المرور غير صحيحة.");
        } else {
          setError(err.message);
        }
      } else {
        setError("حدث خطأ غير متوقع. حاول مرة أخرى.");
      }
      toast.error("فشل تسجيل الدخول", { description: error ?? undefined });
    }
  };

  const handleGoogleLogin = () => {
    // Redirect to backend Google OAuth flow
    window.location.href = `${import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1"}/auth/google`;
  };

  return (
    <div className="gradient-warm flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <Link to="/" className="mb-6 flex items-center justify-center gap-2.5">
          <img src="/logo-icon.png" alt="بصمة+" className="h-10 w-10 object-contain" />
          <span className="text-xl font-extrabold">بصمة+</span>
        </Link>
        <Card className="p-8 shadow-glow">
          <h1 className="text-2xl font-bold">أهلًا بعودتك</h1>
          <p className="mt-1 text-sm text-muted-foreground">تابع من حيث توقّفت.</p>

          <Button
            variant="outline"
            className="mt-6 w-full"
            type="button"
            onClick={handleGoogleLogin}
          >
            <span className="ms-2">المتابعة عبر Google</span>
          </Button>

          <div className="my-5 flex items-center gap-3 text-xs text-muted-foreground">
            <div className="h-px flex-1 bg-border" />
            <span>أو</span>
            <div className="h-px flex-1 bg-border" />
          </div>

          <form className="space-y-4" onSubmit={handleSubmit} noValidate>
            <div className="space-y-2">
              <Label htmlFor="login-email">البريد الإلكتروني</Label>
              <Input
                id="login-email"
                type="email"
                placeholder="you@example.com"
                dir="ltr"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                disabled={login.isPending}
              />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="login-pass">كلمة المرور</Label>
                <Link to="/auth/forgot-password" className="text-xs text-primary hover:underline">
                  نسيت كلمة المرور؟
                </Link>
              </div>
              <Input
                id="login-pass"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                disabled={login.isPending}
              />
            </div>
            <div className="flex items-center gap-2">
              <Checkbox id="remember" checked={remember} onCheckedChange={(v) => setRemember(v === true)} />
              <Label htmlFor="remember" className="text-sm font-normal">
                تذكّرني
              </Label>
            </div>

            {error && (
              <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {error}
              </p>
            )}

            <Button
              type="submit"
              className="gradient-primary w-full shadow-soft"
              disabled={login.isPending}
            >
              {login.isPending ? "جارٍ الدخول…" : "تسجيل الدخول"}
            </Button>
          </form>

          <p className="mt-5 text-center text-sm text-muted-foreground">
            جديد على بصمة+؟{" "}
            <Link to="/auth/register" className="font-semibold text-primary hover:underline">
              أنشئ حسابًا
            </Link>
          </p>
        </Card>
      </div>
    </div>
  );
}
