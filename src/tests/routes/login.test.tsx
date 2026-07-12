import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeAll } from "vitest";

global.ResizeObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
};

vi.mock("@tanstack/react-router", () => ({
  createFileRoute: () => (config: { component: React.FC }) => ({
    options: config,
  }),
  Link: ({ children, ...props }: Record<string, unknown>) => (
    <a {...(props as Record<string, string>)}>{children as React.ReactNode}</a>
  ),
  useNavigate: () => vi.fn(),
}));

vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    user: null,
    isLoading: false,
    login: { mutateAsync: vi.fn() },
    register: { mutateAsync: vi.fn() },
  }),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

describe("Login Page Form Structure", () => {
  it("renders email and password inputs", async () => {
    const mod = await import("@/routes/auth.login");
    const Login = mod.Route.options.component;
    render(<Login />);
    expect(screen.getByPlaceholderText(/you@example/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/كلمة المرور/i)).toBeInTheDocument();
  });
});
