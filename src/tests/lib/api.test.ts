import { describe, it, expect } from "vitest";
import { tokenStore } from "@/lib/api";

describe("tokenStore", () => {
  it("starts with null token", () => {
    tokenStore.clear();
    expect(tokenStore.get()).toBeNull();
  });

  it("stores and retrieves a token", () => {
    tokenStore.set("abc123");
    expect(tokenStore.get()).toBe("abc123");
  });

  it("clears the token", () => {
    tokenStore.set("abc123");
    tokenStore.clear();
    expect(tokenStore.get()).toBeNull();
  });
});
