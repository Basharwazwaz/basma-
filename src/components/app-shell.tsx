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
  Lightbulb,
  Zap,
  Info,
  Clock,
  CheckCheck,
  Sun,
  Moon,
  FileBarChart,
} from "lucide-react";
import { useTheme } from "@/hooks/use-theme";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useNotifications, type NotificationType } from "@/hooks/use-notifications";
import { formatDistanceToNow } from "date-fns";
import { ar } from "date-fns/locale";

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
  { to: "/weekly-report", label: "التقرير الأسبوعي", icon: FileBarChart },
  { to: "/profile", label: "الملف الشخصي", icon: UserCircle },
] as const;

const TYPE_ICON: Record<NotificationType, typeof Bell> = {
  reminder: Clock,
  insight: Lightbulb,
  challenge: Zap,
  system: Info,
};

const TYPE_COLOR: Record<NotificationType, string> = {
  reminder: "text-blue-500 bg-blue-500/10",
  insight: "text-amber-500 bg-amber-500/10",
  challenge: "text-primary bg-primary/10",
  system: "text-muted-foreground bg-muted",
};

function NotificationBell() {
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotifications();

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative" id="notifications-btn">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute top-1.5 left-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[9px] font-bold text-destructive-foreground leading-none animate-pulse">
              {unreadCount > 9 ? "٩+" : unreadCount}
            </span>
          )}
        </Button>
      </PopoverTrigger>

      <PopoverContent className="w-80 p-0" align="end" sideOffset={8}>
        {/* Header */}
        <div className="flex items-center justify-between border-b px-4 py-3">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold">الإشعارات</h3>
            {unreadCount > 0 && (
              <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-bold text-primary">
                {unreadCount} جديد
              </span>
            )}
          </div>
          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              <CheckCheck className="h-3.5 w-3.5" />
              تعيين الكل كمقروء
            </button>
          )}
        </div>

        {/* Notification list */}
        <ScrollArea className="max-h-[380px]">
          {notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Bell className="mb-3 h-12 w-12 text-muted-foreground/20" />
              <p className="font-semibold text-muted-foreground">لا توجد إشعارات حالياً</p>
              <p className="mt-1 text-xs text-muted-foreground/70">سيتم إعلامك بكل جديد هنا</p>
            </div>
          ) : (
            <div className="divide-y">
              {notifications.map((n) => {
                const Icon = TYPE_ICON[n.type];
                const colorClass = TYPE_COLOR[n.type];
                const timeAgo = formatDistanceToNow(new Date(n.createdAt), {
                  addSuffix: true,
                  locale: ar,
                });
                return (
                  <button
                    key={n.id}
                    onClick={() => markAsRead(n.id)}
                    className={cn(
                      "flex w-full gap-3 px-4 py-3 text-right transition-colors hover:bg-muted/50",
                      n.isRead && "opacity-50",
                    )}
                  >
                    {/* Type icon */}
                    <div
                      className={cn(
                        "mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                        colorClass,
                      )}
                    >
                      <Icon className="h-3.5 w-3.5" />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <p
                          className={cn(
                            "text-xs font-semibold leading-snug",
                            !n.isRead && "text-foreground",
                          )}
                        >
                          {n.title}
                        </p>
                        {!n.isRead && (
                          <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                        )}
                      </div>
                      <p className="mt-0.5 text-xs text-muted-foreground leading-relaxed line-clamp-2">
                        {n.message}
                      </p>
                      <p className="mt-1 text-[10px] text-muted-foreground/70">{timeAgo}</p>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </ScrollArea>

        {/* Footer */}
        <div className="border-t px-4 py-2.5">
          <p className="text-center text-[10px] text-muted-foreground">
            {notifications.filter((n) => n.isRead).length} من {notifications.length} مقروءة
          </p>
        </div>
      </PopoverContent>
    </Popover>
  );
}

function ThemeToggle() {
  const { isDark, toggle } = useTheme();
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggle}
      title={isDark ? "التبديل للوضع الفاتح" : "التبديل للوضع الداكن"}
      className="relative overflow-hidden"
      id="theme-toggle-btn"
    >
      <Sun
        className={`h-5 w-5 transition-all duration-300 ${isDark ? "scale-100 opacity-100" : "scale-0 opacity-0 absolute"}`}
      />
      <Moon
        className={`h-5 w-5 transition-all duration-300 ${isDark ? "scale-0 opacity-0 absolute" : "scale-100 opacity-100"}`}
      />
    </Button>
  );
}

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
                "group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all overflow-hidden",
                active
                  ? "text-primary-foreground shadow-soft"
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
              )}
            >
              {active && (
                <div className="absolute inset-0 bg-primary/90 active-nav-indicator -z-10 rounded-lg" />
              )}
              <Icon className="h-4.5 w-4.5 z-10" />
              <span className="z-10">{item.label}</span>
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
            <ThemeToggle />
            <NotificationBell />
          </div>
        </header>
        <main className="px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
