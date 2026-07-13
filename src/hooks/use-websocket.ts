import { useEffect, useRef, useCallback } from "react";
import { tokenStore, apiRefreshToken } from "@/lib/api";

type WsMessage = {
  type: "notification";
  id: string;
  message: string;
  notif_type: string;
  is_read: boolean;
  created_at: string;
};

type Callback = (msg: WsMessage) => void;

export function useWebSocket(onMessage: Callback) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout>>();
  const mountedRef = useRef(true);

  const connect = useCallback(async () => {
    let token = tokenStore.get();
    if (!token) return;
    // Ensure we have a fresh token (avoid expired token rejection)
    const refreshed = await apiRefreshToken();
    if (refreshed) token = tokenStore.get();

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = import.meta.env.VITE_WS_URL || `${protocol}//localhost:8000`;
    const url = `${host}/api/v1/ws?token=${token}`;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        const pingInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) ws.send("ping");
        }, 30000);
        ws.addEventListener("close", () => clearInterval(pingInterval));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "notification") {
            onMessage(data as WsMessage);
          }
        } catch {
          // ignore non-JSON messages (pong, etc.)
        }
      };

      ws.onclose = () => {
        wsRef.current = null;
        if (mountedRef.current) {
          reconnectTimeout.current = setTimeout(connect, 5000);
        }
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      reconnectTimeout.current = setTimeout(connect, 5000);
    }
  }, [onMessage]);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      mountedRef.current = false;
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [connect]);

  return { disconnect: () => wsRef.current?.close() };
}
