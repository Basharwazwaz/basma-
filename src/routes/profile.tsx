import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { X } from "lucide-react";

export const Route = createFileRoute("/profile")({
  head: () => ({ meta: [{ title: "الملف الشخصي | بصمة+" }] }),
  component: Profile,
});

const interests = ["تقنية", "تصميم", "قراءة", "رياضة", "موسيقى"];
const goals = [
  { t: "تعلّم البايثون", p: 45 },
  { t: "تقليل وقت الشاشة", p: 60 },
  { t: "تحسين المعدّل", p: 70 },
];

function Profile() {
  return (
    <AppShell title="الملف الشخصي" subtitle="إدارة بياناتك وتفضيلاتك.">
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="p-6 lg:col-span-2">
          <div className="mb-6 flex items-center gap-4">
            <Avatar className="h-20 w-20">
              <AvatarFallback className="gradient-primary text-2xl text-primary-foreground">
                ب
              </AvatarFallback>
            </Avatar>
            <div>
              <h2 className="text-xl font-bold">بشّار العلي</h2>
              <p className="text-sm text-muted-foreground">طالب هندسة برمجيات · المستوى ٧</p>
              <Button variant="outline" size="sm" className="mt-2">
                تغيير الصورة
              </Button>
            </div>
          </div>
          <Separator />
          <h3 className="mt-6 mb-4 font-bold">المعلومات الشخصيّة</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label>الاسم</Label>
              <Input defaultValue="بشّار العلي" />
            </div>
            <div className="space-y-1.5">
              <Label>البريد</Label>
              <Input dir="ltr" defaultValue="bashar@example.com" />
            </div>
            <div className="space-y-1.5">
              <Label>المدينة</Label>
              <Input defaultValue="عمّان" />
            </div>
            <div className="space-y-1.5">
              <Label>التعليم</Label>
              <Input defaultValue="جامعي" />
            </div>
            <div className="space-y-1.5">
              <Label>العمر</Label>
              <Input type="number" defaultValue={21} />
            </div>
            <div className="space-y-1.5">
              <Label>الجنس</Label>
              <Select defaultValue="m">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="m">ذكر</SelectItem>
                  <SelectItem value="f">أنثى</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <h3 className="mt-6 mb-3 font-bold">الاهتمامات</h3>
          <div className="flex flex-wrap gap-2">
            {interests.map((i) => (
              <Badge key={i} variant="secondary" className="gap-1 py-1.5 ps-3 pe-2">
                {i}
                <button className="rounded-full p-0.5 transition hover:bg-foreground/10">
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
            <Button variant="outline" size="sm">
              + إضافة
            </Button>
          </div>

          <div className="mt-6 flex gap-3">
            <Button className="gradient-primary shadow-soft">حفظ التغييرات</Button>
            <Button variant="ghost">إلغاء</Button>
          </div>
        </Card>

        <div className="space-y-6">
          <Card className="p-5">
            <h3 className="mb-3 font-bold">أهدافك النشطة</h3>
            <div className="space-y-3">
              {goals.map((g) => (
                <div key={g.t}>
                  <div className="mb-1 flex justify-between text-sm">
                    <span>{g.t}</span>
                    <span className="text-muted-foreground">{g.p}٪</span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-muted">
                    <div
                      className="gradient-primary h-full rounded-full"
                      style={{ width: `${g.p}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-5">
            <h3 className="mb-3 font-bold">الإعدادات</h3>
            <div className="space-y-4 text-sm">
              <div className="flex items-center justify-between">
                <span>الوضع الداكن</span>
                <Switch />
              </div>
              <div className="flex items-center justify-between">
                <span>إشعارات يوميّة</span>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <span>تذكير المخطط</span>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <span>ملخّص أسبوعي</span>
                <Switch defaultChecked />
              </div>
              <div className="space-y-1.5">
                <Label>اللغة</Label>
                <Select defaultValue="ar">
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

          <Card className="border-destructive/30 bg-destructive/5 p-5">
            <h3 className="mb-2 font-bold text-destructive">منطقة حسّاسة</h3>
            <p className="mb-3 text-xs text-muted-foreground">
              يمكنك تصدير بياناتك أو حذف حسابك في أي وقت.
            </p>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                تصدير البيانات
              </Button>
              <Button variant="destructive" size="sm">
                حذف الحساب
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
