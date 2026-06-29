import { createFileRoute, Link } from "@tanstack/react-router";

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
          <form className="mt-6 space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">الاسم الكامل</Label>
              <Input id="name" placeholder="بشّار العلي" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">البريد الإلكتروني</Label>
              <Input id="email" type="email" placeholder="you@example.com" dir="ltr" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="pass">كلمة المرور</Label>
              <Input id="pass" type="password" placeholder="٨ أحرف على الأقل" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="age">العمر</Label>
                <Input id="age" type="number" placeholder="٢٠" />
              </div>
              <div className="space-y-2">
                <Label>الجنس</Label>
                <Select>
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
            </div>
            <div className="space-y-2">
              <Label>المستوى التعليمي</Label>
              <Select>
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
            <Button asChild className="gradient-primary w-full shadow-soft">
              <Link to="/onboarding">إنشاء الحساب</Link>
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
