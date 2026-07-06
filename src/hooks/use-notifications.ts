import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  apiGetNotifications,
  apiMarkNotificationRead,
  apiMarkAllNotificationsRead,
} from "@/lib/api";

export type NotificationType = "reminder" | "insight" | "challenge" | "system";

export interface AppNotification {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  isRead: boolean;
  createdAt: string;
}

const NOTIFICATIONS_QUERY_KEY = ["notifications"];

export function useNotifications() {
  const queryClient = useQueryClient();

  const { data: serverNotifications = [], isLoading } = useQuery({
    queryKey: NOTIFICATIONS_QUERY_KEY,
    queryFn: () => apiGetNotifications(),
    refetchInterval: 60000, // refresh every minute
  });

  // Map backend format to frontend format
  const notifications: AppNotification[] = serverNotifications.map(
    (n: import("@/lib/api").NotificationData) => ({
      id: n.id,
      title: n.title,
      message: n.message || "",
      type: (n.action_url && n.action_url.includes("challenge")
        ? "challenge"
        : "system") as NotificationType,
      isRead: n.is_read,
      createdAt: n.created_at,
    }),
  );

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  const markAsReadMutation = useMutation({
    mutationFn: apiMarkNotificationRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: NOTIFICATIONS_QUERY_KEY });
    },
  });

  const markAllAsReadMutation = useMutation({
    mutationFn: apiMarkAllNotificationsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: NOTIFICATIONS_QUERY_KEY });
    },
  });

  const markAsRead = (id: string) => {
    markAsReadMutation.mutate(id);
  };

  const markAllAsRead = () => {
    markAllAsReadMutation.mutate();
  };

  return { notifications, unreadCount, markAsRead, markAllAsRead, isLoading };
}
