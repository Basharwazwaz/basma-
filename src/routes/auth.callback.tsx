import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useRef } from "react";
import { tokenStore } from "@/lib/api";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

export const Route = createFileRoute("/auth/callback")({
  component: AuthCallback,
});

function AuthCallback() {
  const navigate = useNavigate();
  const handled = useRef(false);

  useEffect(() => {
    if (handled.current) return;
    handled.current = true;

    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get("access_token");
    const error = params.get("error");

    // Remove token from URL immediately to prevent leakage via address bar / history
    if (accessToken || error) {
      window.history.replaceState({}, "", window.location.pathname);
    }

    if (error) {
      toast.error("فشل تسجيل الدخول عبر Google", { description: error });
      navigate({ to: "/auth/login" });
      return;
    }

    if (accessToken) {
      tokenStore.set(accessToken);
      toast.success("تم تسجيل الدخول بنجاح!");
      navigate({ to: "/dashboard" });
    } else {
      toast.error("لم يتم العثور على رمز الدخول");
      navigate({ to: "/auth/login" });
    }
  }, [navigate]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
        <p className="mt-4 text-sm text-muted-foreground">جارٍ تسجيل الدخول...</p>
      </div>
    </div>
  );
}
