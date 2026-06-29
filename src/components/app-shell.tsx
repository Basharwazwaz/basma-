import { Link, useRouterState } from "@tanstack/react-router";
import { type ReactNode } from "react";
import {
  LayoutDashboard,
  Bot,
  CalendarDays,
  Trophy,
  GraduationCap,
  Activity,
  Smile,
  Target,
  Award,
  UserCircle,
  Bell,
  Menu,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const nav = [
  { to: "/dashboard", label: "لوحة التحكم", icon: LayoutDashboard },
  { to: "/ai-coach", label: "المدرّب الذكي", icon: Bot },
  { to: "/planner", label: "المخطط الأسبوعي", icon: CalendarDays },
  { to: "/challenges", label: "التحديات", icon: Trophy },
  { to: "/learning-hub", label: "مركز التعلّم", icon: GraduationCap },
  { to: "/digital-health", label: "الصحة الرقمية", icon: Activity },
  { to: "/mood", label: "تتبّع المزاج", icon: Smile },
  { to: "/goals", label: "الأهداف", icon: Target },
  { to: "/achievements", label: "الإنجازات", icon: Award },
  { to: "/profile", label: "الملف الشخصي", icon: UserCircle },
] as const;

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  return (
    <div className="flex h-full flex-col">
      <Link to="/dashboard" className="flex items-center gap-3 px-6 py-6">
        <img src="/logo-icon.png" alt="بصمة+" className="h-10 w-10 object-contain" />
        <div>
          <div className="text-lg font-bold text-foreground">بصمة+</div>
          <div className="text-xs text-muted-foreground">رفيقك الذكي</div>
        </div>
      </Link>
      <nav className="flex-1 space-y-1 px-3">
        {nav.map((item) => {
          const active = pathname === item.to;
          const Icon = item.icon;
          return (
            <Link
              key={item.to}
              to={item.to}
              onClick={onNavigate}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all",
                active
                  ? "gradient-primary text-primary-foreground shadow-soft"
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
              )}
            >
              <Icon className="h-4.5 w-4.5" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="border-t p-4">
        <div className="flex items-center gap-3 rounded-lg bg-muted/50 p-3">
          <Avatar className="h-9 w-9">
            <AvatarFallback className="bg-primary text-primary-foreground">ب</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <div className="truncate text-sm font-semibold">بشّار العلي</div>
            <div className="truncate text-xs text-muted-foreground">طالب · المستوى ٧</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function AppShell({
  title,
  subtitle,
  actions,
  children,
}: {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      {/* Desktop sidebar (right side in RTL) */}
      <aside className="fixed inset-y-0 right-0 hidden w-64 border-l bg-sidebar lg:block">
        <SidebarContent />
      </aside>

      <div className="lg:mr-64">
        <header className="sticky top-0 z-30 flex items-center justify-between gap-4 border-b bg-background/85 px-4 py-4 backdrop-blur-md sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="lg:hidden">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-72 p-0">
                <SheetHeader className="sr-only">
                  <SheetTitle>القائمة</SheetTitle>
                </SheetHeader>
                <SidebarContent />
              </SheetContent>
            </Sheet>
            <div>
              <h1 className="text-xl font-bold sm:text-2xl">{title}</h1>
              {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {actions}
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              <span className="absolute top-2 left-2 h-2 w-2 rounded-full bg-destructive" />
            </Button>
          </div>
        </header>
        <main className="px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
