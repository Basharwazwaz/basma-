import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError } from "@/lib/api";
import { toast } from "sonner";
import { Mail, ArrowRight, CheckCircle2, Loader2 } from "lucide-react";

export const Route = createFileRoute("/auth/forgot-password")({
  head: () => ({
    meta: [
      { title: "نسيت كلمة المرور | بصمة+" },
      { name: "description", content: "استعيد كلمة المرور الخاصة بك في بصمة+." },
    ],
  }),
  component: ForgotPassword,
});

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email) {
      setError("يرجى إدخال البريد الإلكتروني.");
      return;
    }

    setLoading(true);
    try {
      const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
      const response = await fetch(`${BASE_URL}/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        const err = await response.json().catch(() => null);
        throw new ApiError(response.status, err?.detail ?? "حدث خطأ");
      }

      setSent(true);
      toast.success("تم إرسال رابط إعادة التعيين على بريدك الإلكتروني");
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
          {sent ? (
            <div className="text-center">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-success/10">
                <CheckCircle2 className="h-8 w-8 text-success" />
              </div>
              <h1 className="mt-4 text-2xl font-bold">تم الإرسال!</h1>
              <p className="mt-2 text-sm text-muted-foreground">
                إذا كان البريد الإلكتروني {email} مسجّلًا في نظامنا، ستتلقى رسالة تحتوي على رابط
                لإعادة تعيين كلمة المرور.
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                تحقق من صندوق الوارد أو مجلد الرسائل غير المرغوب فيها.
              </p>
              <Button asChild className="mt-6 gradient-primary shadow-soft">
                <Link to="/auth/login">
                  <ArrowRight className="ms-2 h-4 w-4" />
                  العودة لتسجيل الدخول
                </Link>
              </Button>
            </div>
          ) : (
            <>
              <div className="mb-6 flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10">
                  <Mail className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold">نسيت كلمة المرور؟</h1>
                  <p className="mt-0.5 text-sm text-muted-foreground">
                    أدخل بريدك الإلكتروني وسنرسل لك رابط إعادة التعيين.
                  </p>
                </div>
              </div>

              <form className="space-y-4" onSubmit={handleSubmit} noValidate>
                <div className="space-y-2">
                  <Label htmlFor="fp-email">البريد الإلكتروني</Label>
                  <Input
                    id="fp-email"
                    type="email"
                    placeholder="you@example.com"
                    dir="ltr"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    autoFocus
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
                    <ArrowRight className="ms-2 h-4 w-4" />
                  )}
                  {loading ? "جارٍ الإرسال…" : "إرسال رابط إعادة التعيين"}
                </Button>
              </form>
            </>
          )}

          <p className="mt-5 text-center text-sm text-muted-foreground">
            تذكّرت كلمة المرور؟{" "}
            <Link to="/auth/login" className="font-semibold text-primary hover:underline">
              سجّل الدخول
            </Link>
          </p>
        </Card>
      </div>
    </div>
  );
}
