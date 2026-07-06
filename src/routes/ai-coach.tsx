import { createFileRoute } from "@tanstack/react-router";
import { useState, useRef, useEffect } from "react";
import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Send, Bot, User, Sparkles, Trash2, Mic, Copy, CheckCheck } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/ai-coach")({
  head: () => ({ meta: [{ title: "المدرّب الذكي | بصمة+" }] }),
  component: Coach,
});

type Message = {
  id: string;
  r: "user" | "ai";
  t: string;
  time: string;
};

const initialMessages: Message[] = [
  { id: "1", r: "ai", t: "أهلاً بك! أنا مدرّبك الذكي. كيف يمكنني مساعدتك اليوم؟", time: "٠٩:٠٠ ص" },
];

const PREDEFINED_SUGGESTIONS = [
  "كيف أنظّم وقتي خلال الامتحانات؟",
  "أشعر بالتوتر، ما الحل؟",
  "كيف أبدأ في تعلّم البرمجة؟",
];

function getCurrentTime() {
  const now = new Date();
  return now.toLocaleTimeString("ar-EG", { hour: "2-digit", minute: "2-digit" });
}

function getMockResponse(msg: string): string {
  const text = msg.toLowerCase();
  if (text.includes("توتر") || text.includes("ضغط") || text.includes("قلق")) {
    return "أفهم تماماً شعورك بالضغط. من الطبيعي المرور بفترات توتر. جرب تقنية تنفس ٤-٧-٨ لمدة دقيقتين، أو خذ استراحة قصيرة للمشي بعيداً عن الشاشات. هل تود أن أذكرك بتمارين الاسترخاء يومياً؟";
  }
  if (text.includes("امتحان") || text.includes("دراسة") || text.includes("مذاكرة")) {
    return "الدراسة الفعالة تبدأ بالتنظيم! أنصحك بتقسيم المادة باستخدام تقنية بومودورو (٢٥ دقيقة دراسة، ٥ دقائق راحة). هل ترغب أن أضيف جلسة بومودورو إلى مخططك اليوم؟";
  }
  if (text.includes("بايثون") || text.includes("برمجة") || text.includes("كود")) {
    return "البرمجة مجال ممتع جداً! بايثون لغة ممتازة للبدء. أنصحك بالبدء بأساسيات المتغيرات والشروط، ثم التدرب على حل مسائل بسيطة. لقد أضفت كورس «بايثون للمبتدئين» في مركز التعلّم الخاص بك.";
  }
  if (text.includes("نوم") || text.includes("تعب")) {
    return "جودة النوم تؤثر مباشرة على طاقتك. حاول إبعاد هاتفك عن السرير وتجنب الشاشات قبل النوم بساعة. لقد لاحظت أن وقت استخدام هاتفك مرتفع نسبياً ليلاً.";
  }
  return "أنا هنا لدعمك! خطوة بخطوة سنصل إلى أهدافك. هل هناك شيء محدد تود التركيز عليه اليوم، كتحسين عاداتك أو ترتيب مهامك؟";
}

function Coach() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isTyping]);

  const send = (text: string) => {
    if (!text.trim()) return;
    const userMsg: Message = {
      id: Date.now().toString(),
      r: "user",
      t: text.trim(),
      time: getCurrentTime(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    // Simulate AI thinking delay
    setTimeout(() => {
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        r: "ai",
        t: getMockResponse(text),
        time: getCurrentTime(),
      };
      setMessages((prev) => [...prev, aiMsg]);
      setIsTyping(false);
    }, 1500);
  };

  const clear = () => {
    setMessages(initialMessages);
    toast.success("تم مسح المحادثة بنجاح.");
  };

  const copyText = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("تم نسخ النص");
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      toast("جاري التسجيل...", { icon: "🎙️" });
    }
  };

  return (
    <AppShell
      title="المدرّب الذكي"
      subtitle="محادثة ذكية لمساعدتك في تحقيق أهدافك."
      actions={
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="text-muted-foreground hover:text-destructive"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent className="font-sans" dir="rtl">
            <AlertDialogHeader>
              <AlertDialogTitle>هل أنت متأكد من مسح المحادثة؟</AlertDialogTitle>
              <AlertDialogDescription>
                هذا الإجراء سيقوم بمسح كافة الرسائل السابقة ولا يمكن التراجع عنه.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter className="flex-row gap-2 justify-end sm:justify-start">
              <AlertDialogCancel className="mt-0">إلغاء</AlertDialogCancel>
              <AlertDialogAction
                onClick={clear}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                مسح
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      }
    >
      <div className="grid gap-6 lg:grid-cols-4">
        {/* Chat Area */}
        <Card className="flex h-[calc(100vh-14rem)] flex-col p-0 shadow-soft lg:col-span-3">
          <ScrollArea className="flex-1 p-6">
            <div className="space-y-6 pb-4">
              {messages.map((m) => {
                const isAi = m.r === "ai";
                return (
                  <div key={m.id} className={`flex gap-3 ${isAi ? "" : "flex-row-reverse"}`}>
                    <div
                      className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${isAi ? "gradient-warm text-primary" : "gradient-primary text-primary-foreground"}`}
                    >
                      {isAi ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                    </div>
                    <div
                      className={`group relative max-w-[80%] rounded-2xl px-4 py-3 text-sm ${isAi ? "rounded-tr-sm bg-muted/50" : "rounded-tl-sm gradient-primary text-primary-foreground shadow-soft"}`}
                    >
                      <div className="leading-relaxed">{m.t}</div>
                      <div
                        className={`mt-1.5 flex items-center gap-2 text-[10px] ${isAi ? "text-muted-foreground" : "text-primary-foreground/70 justify-end"}`}
                      >
                        <span>{m.time}</span>
                        {!isAi && <CheckCheck className="h-3 w-3" />}
                      </div>

                      {/* Copy button for AI messages */}
                      {isAi && (
                        <button
                          onClick={() => copyText(m.t)}
                          className="absolute -left-10 top-2 p-1.5 rounded-md text-muted-foreground opacity-0 hover:bg-muted transition-opacity group-hover:opacity-100"
                          title="نسخ النص"
                        >
                          <Copy className="h-3.5 w-3.5" />
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}

              {/* Typing indicator */}
              {isTyping && (
                <div className="flex gap-3">
                  <div className="gradient-warm flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-primary">
                    <Bot className="h-4 w-4" />
                  </div>
                  <div className="rounded-2xl rounded-tr-sm bg-muted/50 px-5 py-4">
                    <div className="flex items-center gap-1">
                      <div className="h-2 w-2 rounded-full bg-primary/60 animate-typing-dot" />
                      <div className="h-2 w-2 rounded-full bg-primary/60 animate-typing-dot" />
                      <div className="h-2 w-2 rounded-full bg-primary/60 animate-typing-dot" />
                    </div>
                  </div>
                </div>
              )}
              <div ref={scrollRef} />
            </div>
          </ScrollArea>

          {/* Input Area */}
          <div className="border-t p-4">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                send(input);
              }}
              className="flex items-center gap-2"
            >
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={toggleRecording}
                className={`transition-colors ${isRecording ? "text-destructive bg-destructive/10 animate-pulse" : "text-muted-foreground hover:text-foreground"}`}
              >
                <Mic className="h-5 w-5" />
              </Button>
              <div className="relative flex-1">
                <Input
                  placeholder="اسأل عن دراستك، أهدافك، أو تتبع مزاجك..."
                  value={input}
                  onChange={(e) => setInput(e.target.value.slice(0, 500))}
                  className="rounded-full bg-muted/30 ps-4 pe-12"
                  disabled={isTyping || isRecording}
                />
                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-[10px] text-muted-foreground">
                  {input.length}/500
                </div>
              </div>
              <Button
                type="submit"
                size="icon"
                disabled={!input.trim() || isTyping || isRecording}
                className="gradient-primary shrink-0 rounded-full shadow-soft"
              >
                <Send className="h-4 w-4 rtl:-scale-x-100" />
              </Button>
            </form>
          </div>
        </Card>

        {/* Sidebar */}
        <div className="space-y-6">
          <Card className="p-5">
            <div className="mb-4 flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-warning-foreground" />
              <h3 className="font-bold">جرّب أن تسأل</h3>
            </div>
            <div className="space-y-2">
              {PREDEFINED_SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  disabled={isTyping}
                  className="w-full rounded-lg border bg-muted/30 p-3 text-start text-sm transition hover:bg-muted"
                >
                  {s}
                </button>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
