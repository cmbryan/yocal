import { formatDateKey, htmlToText, joinList, parseDateFromKey } from "../src/lib/date";

describe("date utilities", () => {
  test("formatDateKey outputs YYYY-MM-DD", () => {
    const date = new Date(2025, 5, 2);
    expect(formatDateKey(date)).toBe("2025-06-02");
  });

  test("parseDateFromKey parses valid date", () => {
    const parsed = parseDateFromKey("2025-06-02");
    expect(parsed).not.toBeNull();
    expect(parsed?.getFullYear()).toBe(2025);
    expect(parsed?.getMonth()).toBe(5);
    expect(parsed?.getDate()).toBe(2);
  });

  test("parseDateFromKey rejects impossible date", () => {
    expect(parseDateFromKey("2025-02-31")).toBeNull();
  });

  test("htmlToText strips and normalizes basic markup", () => {
    const html = "<em>Romans 1:1</em><br>Text &amp; more&#39;s";
    expect(htmlToText(html)).toBe("Romans 1:1\nText & more's");
  });

  test("joinList removes blank entries", () => {
    expect(joinList(["fast", "", null, undefined, "tone"])).toEqual(["fast", "tone"]);
  });
});
