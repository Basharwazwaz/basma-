import { createFileRoute, Link } from "@tanstack/react-router";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";

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
          <Button variant="outline" className="mt-6 w-full">
            <span className="ms-2">المتابعة عبر Google</span>
          </Button>
          <div className="my-5 flex items-center gap-3 text-xs text-muted-foreground">
            <div className="h-px flex-1 bg-border" />
            <span>أو</span>
            <div className="h-px flex-1 bg-border" />
          </div>
          <form className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">البريد الإلكتروني</Label>
              <Input id="email" type="email" placeholder="you@example.com" dir="ltr" />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="pass">كلمة المرور</Label>
                <a href="#" className="text-xs text-primary hover:underline">
                  نسيت كلمة المرور؟
                </a>
              </div>
              <Input id="pass" type="password" placeholder="••••••••" />
            </div>
            <div className="flex items-center gap-2">
              <Checkbox id="remember" />
              <Label htmlFor="remember" className="text-sm font-normal">
                تذكّرني
              </Label>
            </div>
            <Button asChild className="gradient-primary w-full shadow-soft">
              <Link to="/dashboard">تسجيل الدخول</Link>
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
