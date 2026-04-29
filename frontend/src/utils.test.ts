import { describe, expect, it } from "vitest";
import { escapeHtml } from "./utils";

describe("escapeHtml", () => {
  it("escapes script tags so they cannot execute when set as innerHTML", () => {
    expect(escapeHtml("<script>alert(1)</script>")).toBe(
      "&lt;script&gt;alert(1)&lt;/script&gt;",
    );
  });

  it("escapes ampersands", () => {
    expect(escapeHtml("a & b")).toBe("a &amp; b");
  });

  it("returns the empty string unchanged", () => {
    expect(escapeHtml("")).toBe("");
  });

  it("preserves plain text without HTML metacharacters", () => {
    expect(escapeHtml("hello world 123")).toBe("hello world 123");
  });
});
