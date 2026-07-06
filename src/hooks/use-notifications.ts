import { useState, useCallback, useEffect } from "react";

export type NotificationType = "reminder" | "insight" | "challenge" | "system";

export interface AppNotification {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  isRead: boolean;
  createdAt: string;
}

const STORAGE_KEY = "basma_notifications_read";

const INITIAL_NOTIFICATIONS: AppNotification[] = [
  {
    id: "n1",
    title: "تذكير بجلسة الدراسة",
    message: "لم تبدأ جلسة بومودورو اليوم. ابدأ الآن وحافظ على سلسلة إنجازاتك! 🔥",
    type: "reminder",
    isRead: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 15).toISOString(), // 15 min ago
  },
  {
    id: "n2",
    title: "تحدٍّ جديد متاح",
    message: 'تحدّي "اقرأ ١٠ صفحات يومياً" ينتهر خلال ٢٤ ساعة. انضمّ الآن واكسب ٥٠ نقطة.',
    type: "challenge",
    isRead: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 60).toISOString(), // 1 hour ago
  },
  {
    id: "n3",
    title: "رؤية أسبوعية 💡",
    message: "أنت في أفضل ٢٠٪ من المستخدمين هذا الأسبوع. معدّل نشاطك ارتفع ١٥٪ عن الأسبوع الماضي.",
    type: "insight",
    isRead: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(), // 3 hours ago
  },
  {
    id: "n4",
    title: "تحديث النظام",
    message: "تم إضافة ميزة تتبّع المزاج اليومي. جرّبها الآن من قسم تتبّع المزاج.",
    type: "system",
    isRead: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), // 1 day ago
  },
  {
    id: "n5",
    title: "أحسنت! 🎉",
    message: "أتممت ٤ جلسات بومودورو أمس. استمر وستصل إلى المستوى ٨ خلال ٣ أيام.",
    type: "insight",
    isRead: true,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 36).toISOString(), // 1.5 days ago
  },
];

export function useNotifications() {
  const [notifications, setNotifications] = useState<AppNotification[]>(() => {
    // Merge persisted read-state with initial notifications (client-side only)
    if (typeof window === "undefined") return INITIAL_NOTIFICATIONS;
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) return INITIAL_NOTIFICATIONS;
      const readIds: string[] = JSON.parse(stored);
      return INITIAL_NOTIFICATIONS.map((n) => ({
        ...n,
        isRead: readIds.includes(n.id) ? true : n.isRead,
      }));
    } catch {
      return INITIAL_NOTIFICATIONS;
    }
  });

  // Persist read state whenever it changes
  useEffect(() => {
    if (typeof window === "undefined") return;
    const readIds = notifications.filter((n) => n.isRead).map((n) => n.id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(readIds));
  }, [notifications]);

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  const markAsRead = useCallback((id: string) => {
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, isRead: true } : n)));
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, isRead: true })));
  }, []);

  return { notifications, unreadCount, markAsRead, markAllAsRead };
}
