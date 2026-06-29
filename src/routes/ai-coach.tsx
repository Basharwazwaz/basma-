import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Sparkles, Send, Mic, MessageSquare, Plus } from "lucide-react";

export const Route = createFileRoute("/ai-coach")({
  head: () => ({ meta: [{ title: "المدرّب الذكي | بصمة+" }] }),
  component: Coach,
});

const initial = [
  { role: "ai", text: "أهلًا بشّار! أنا مدرّبك الذكي. كيف أقدر أساعدك اليوم؟" },
  { role: "user", text: "كيف أنظّم وقتي للامتحانات القادمة؟" },
  {
    role: "ai",
    text: "رائع أنّك تخطّط مسبقًا! اقتراحي: ابدأ بقائمة المواد وعدد ساعات المراجعة المطلوبة لكل مادة. أستطيع بناء جدول بومودورو لك في المخطط الأسبوعي. هل تريد أن نبدأ؟",
  },
];
const chips = [
  "كيف أدرس للامتحانات؟",
  "أشعر بالتوتر",
  "كيف أتعلّم البايثون؟",
  "نصائح للنوم الجيد",
  "خطة لتقليل وقت الشاشة",
];
const conversations = [
  "خطة المراجعة لامتحانات يناير",
  "تقليل وقت إنستغرام",
  "تعلّم SQL في شهر",
  "إدارة التوتر قبل المقابلات",
];

function Coach() {
  const [msgs, setMsgs] = useState(initial);
  const [val, setVal] = useState("");
  const send = (text: string) => {
    if (!text.trim()) return;
    setMsgs((m) => [
      ...m,
      { role: "user", text },
      { role: "ai", text: "شكرًا لمشاركتك. دعني أحلّل وأعود إليك بخطة قريبًا..." },
    ]);
    setVal("");
  };
  return (
    <AppShell title="المدرّب الذكي" subtitle="مدرّبك الشخصي مدعوم بالذكاء الاصطناعي.">
      <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
        <Card className="flex h-[calc(100vh-220px)] flex-col p-0">
          <div className="flex items-center justify-between border-b p-4">
            <div className="flex items-center gap-2">
              <div className="gradient-primary flex h-9 w-9 items-center justify-center rounded-full">
                <Sparkles className="h-4 w-4 text-primary-foreground" />
              </div>
              <div>
                <div className="text-sm font-semibold">مدرّب بصمة+</div>
                <div className="text-xs text-success">متّصل</div>
              </div>
            </div>
            <Button variant="ghost" size="sm">
              مسح المحادثة
            </Button>
          </div>
          <div className="flex-1 space-y-4 overflow-y-auto p-4">
            {msgs.map((m, i) => (
              <div
                key={i}
                className={`flex ${m.role === "user" ? "justify-start" : "justify-end"}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${m.role === "user" ? "bg-muted" : "gradient-primary text-primary-foreground shadow-soft"}`}
                >
                  {m.text}
                </div>
              </div>
            ))}
            <div className="flex flex-wrap gap-2 pt-2">
              {chips.map((c) => (
                <button key={c} onClick={() => send(c)}>
                  <Badge variant="outline" className="cursor-pointer transition hover:bg-muted">
                    {c}
                  </Badge>
                </button>
              ))}
            </div>
          </div>
          <form
            className="flex items-center gap-2 border-t p-3"
            onSubmit={(e) => {
              e.preventDefault();
              send(val);
            }}
          >
            <Button type="button" variant="ghost" size="icon">
              <Mic className="h-5 w-5" />
            </Button>
            <Input
              value={val}
              onChange={(e) => setVal(e.target.value)}
              placeholder="اكتب سؤالك..."
              className="flex-1"
            />
            <Button type="submit" size="icon" className="gradient-primary">
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </Card>

        <div className="space-y-4">
          <Button className="w-full gradient-primary shadow-soft">
            <Plus className="ms-1 h-4 w-4" /> محادثة جديدة
          </Button>
          <Card className="p-4">
            <h3 className="mb-2 text-sm font-bold">محادثات سابقة</h3>
            <div className="space-y-1">
              {conversations.map((c) => (
                <button
                  key={c}
                  className="flex w-full items-center gap-2 rounded-md p-2 text-start text-sm transition hover:bg-muted"
                >
                  <MessageSquare className="h-4 w-4 shrink-0 text-muted-foreground" />
                  <span className="truncate">{c}</span>
                </button>
              ))}
            </div>
          </Card>
          <Card className="p-4 text-xs text-muted-foreground">
            <strong className="text-foreground">ملاحظة:</strong> المدرّب أداة مساعدة وليس بديلًا عن
            الاستشارة المتخصّصة. بياناتك خاصّة بك.
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
