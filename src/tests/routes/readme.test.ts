import { describe, it, expect } from "vitest";

describe("README Structure", () => {
  it("contains architecture diagram", async () => {
    const fs = await import("fs");
    const path = await import("path");
    const readme = fs.readFileSync(path.resolve(__dirname, "../../../README.md"), "utf-8");
    expect(readme).toContain("System Architecture");
    expect(readme).toContain("FastAPI Backend");
    expect(readme).toContain("PostgreSQL");
  });

  it("contains ERD diagram", async () => {
    const fs = await import("fs");
    const path = await import("path");
    const readme = fs.readFileSync(path.resolve(__dirname, "../../../README.md"), "utf-8");
    expect(readme).toContain("Entity-Relationship Diagram");
    expect(readme).toContain("users");
    expect(readme).toContain("profiles");
    expect(readme).toContain("goals");
  });

  it("contains all API modules", async () => {
    const fs = await import("fs");
    const path = await import("path");
    const readme = fs.readFileSync(path.resolve(__dirname, "../../../README.md"), "utf-8");
    expect(readme).toContain("Auth");
    expect(readme).toContain("Profile");
    expect(readme).toContain("Mood");
    expect(readme).toContain("Gamification");
    expect(readme).toContain("AI Coach");
  });
});
