import { describe, expect, it } from "vitest";
import { createFormatPicker } from "./format-picker";

describe("createFormatPicker accessibility", () => {
  it("connects each select to its visible label via for/id", () => {
    const view = createFormatPicker(() => undefined);

    const formatLabel = view.querySelector<HTMLLabelElement>(
      'label[for="format-select"]',
    );
    const formatSelect = view.querySelector<HTMLSelectElement>("#format-select");
    const qualityLabel = view.querySelector<HTMLLabelElement>(
      'label[for="quality-select"]',
    );
    const qualitySelect = view.querySelector<HTMLSelectElement>("#quality-select");

    expect(formatLabel).not.toBeNull();
    expect(formatSelect).not.toBeNull();
    expect(qualityLabel).not.toBeNull();
    expect(qualitySelect).not.toBeNull();
  });
});
