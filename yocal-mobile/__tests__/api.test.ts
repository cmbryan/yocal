import { buildDateUrl, fetchDailyData } from "../src/lib/api";

describe("api utilities", () => {
  test("buildDateUrl maps date key to query params", () => {
    const url = buildDateUrl("2025-06-02", "https://example.com/api-php");
    expect(url).toBe("https://example.com/api-php/date?year=2025&month=6&day=2");
  });

  test("buildDateUrl rejects invalid date keys", () => {
    expect(() => buildDateUrl("not-a-date")).toThrow("Date must be in YYYY-MM-DD format.");
    expect(() => buildDateUrl("2025-02-31")).toThrow("Date must be in YYYY-MM-DD format.");
  });

  test("fetchDailyData returns payload for successful responses", async () => {
    const fakePayload = {
      day_name: "Monday",
      day_ord: "2nd",
      month: "June",
      year: 2025,
      fast: "Fast free",
      tone: null,
      eothinon: null,
      liturgy: null,
      desig: null,
      commem: null,
      fore_after: null,
      global_saints: null,
      british_saints: null,
      lections: { basic: [], commem: [], liturgy: [] },
      texts: { basic: [], commem: [] },
    };

    const fetchImpl = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => fakePayload,
    });

    await expect(fetchDailyData("2025-06-02", fetchImpl)).resolves.toEqual(fakePayload);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });

  test("fetchDailyData throws API errors", async () => {
    const fetchImpl = jest.fn().mockResolvedValue({
      ok: false,
      json: async () => ({ error: "No data found" }),
    });

    await expect(fetchDailyData("2025-06-02", fetchImpl)).rejects.toThrow("No data found");
  });

  test("fetchDailyData throws payload errors", async () => {
    const fetchImpl = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ error: "Payload error" }),
    });

    await expect(fetchDailyData("2025-06-02", fetchImpl)).rejects.toThrow("Payload error");
  });
});
