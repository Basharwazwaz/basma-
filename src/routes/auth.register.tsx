import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { z } from "zod";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/hooks/use-auth";
import { ApiError } from "@/lib/api";
import { toast } from "sonner";

const registerSchema = z.object({
  firstName: z.string().optional(),
  lastName: z.string().optional(),
  email: z.string().email("صيغة البريد الإلكتروني غير صحيحة."),
  password: z
    .string()
    .min(8, "كلمة المرور يجب أن تكون ٨ أحرف على الأقل.")
    .regex(/[A-Z]/, "يجب أن تحتوي كلمة المرور على حرف كبير على الأقل.")
    .regex(/[0-9]/, "يجب أن تحتوي كلمة المرور على رقم على الأقل."),
  gender: z.string().optional(),
  level: z.string().optional(),
});

type RegisterForm = z.infer<typeof registerSchema>;

export const Route = createFileRoute("/auth/register")({
  head: () => ({
    meta: [
      { title: "إنشاء حساب | بصمة+" },
      { name: "description", content: "أنشئ حسابك في بصمة+ وابدأ رحلة التطوير الذاتي." },
    ],
  }),
  component: Register,
});

function Register() {
  const { register } = useAuth();

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [gender, setGender] = useState("");
  const [level, setLevel] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const parsed = registerSchema.safeParse({
      email,
      password,
      firstName: firstName || undefined,
      lastName: lastName || undefined,
    });

    if (!parsed.success) {
      setError(parsed.error.issues[0].message);
      return;
    }

    try {
      await register.mutateAsync({
        email,
        password,
        first_name: firstName || undefined,
        last_name: lastName || undefined,
      });
      toast.success("تم إنشاء الحساب! 🎉", {
        description: "سجّل دخولك للمتابعة.",
      });
      // Navigation to /auth/login is handled inside useAuth on success
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 409) {
          setError("هذا البريد الإلكتروني مسجّل بالفعل. جرّب تسجيل الدخول.");
        } else {
          setError(err.message);
        }
      } else {
        setError("حدث خطأ غير متوقع. حاول مرة أخرى.");
      }
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
          <h1 className="text-2xl font-bold">أنشئ حسابك</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            انضمّ إلى مجتمع بصمة+ خلال أقل من دقيقة.
          </p>

          <form className="mt-6 space-y-4" onSubmit={handleSubmit} noValidate>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="reg-first-name">الاسم الأول</Label>
                <Input
                  id="reg-first-name"
                  placeholder="بشّار"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  disabled={register.isPending}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="reg-last-name">اسم العائلة</Label>
                <Input
                  id="reg-last-name"
                  placeholder="العلي"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  disabled={register.isPending}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="reg-email">البريد الإلكتروني</Label>
              <Input
                id="reg-email"
                type="email"
                placeholder="you@example.com"
                dir="ltr"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                disabled={register.isPending}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="reg-pass">كلمة المرور</Label>
              <Input
                id="reg-pass"
                type="password"
                placeholder="٨ أحرف على الأقل"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="new-password"
                disabled={register.isPending}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label>الجنس</Label>
                <Select onValueChange={setGender} disabled={register.isPending}>
                  <SelectTrigger>
                    <SelectValue placeholder="اختر" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="m">ذكر</SelectItem>
                    <SelectItem value="f">أنثى</SelectItem>
                    <SelectItem value="o">آخر</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>المستوى التعليمي</Label>
                <Select onValueChange={setLevel} disabled={register.isPending}>
                  <SelectTrigger>
                    <SelectValue placeholder="اختر مستواك" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="hs">ثانوي</SelectItem>
                    <SelectItem value="uni">جامعي</SelectItem>
                    <SelectItem value="grad">دراسات عليا</SelectItem>
                    <SelectItem value="work">خرّيج/عامل</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {error && (
              <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {error}
              </p>
            )}

            <Button
              type="submit"
              className="gradient-primary w-full shadow-soft"
              disabled={register.isPending}
            >
              {register.isPending ? "جارٍ الإنشاء…" : "إنشاء الحساب"}
            </Button>
          </form>

          <p className="mt-5 text-center text-sm text-muted-foreground">
            لديك حساب بالفعل؟{" "}
            <Link to="/auth/login" className="font-semibold text-primary hover:underline">
              سجّل دخولك
            </Link>
          </p>
        </Card>
      </div>
    </div>
  );
}
