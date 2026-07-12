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
}));

vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    user: null,
    isLoading: false,
    register: { mutateAsync: vi.fn() },
  }),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

describe("Register Page Form Structure", () => {
  it("renders registration form with name fields", async () => {
    const mod = await import("@/routes/auth.register");
    const Register = mod.Route.options.component;
    render(<Register />);
    expect(screen.getByLabelText(/الاسم الأول/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/اسم العائلة/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/you@example/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/٨ أحرف/i)).toBeInTheDocument();
  });
});
