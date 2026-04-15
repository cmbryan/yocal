import { parseDateFromKey } from "./date";

export const API_BASE = "https://yorkorthodox.org/api-php";

export type DatePayload = {
  day_name: string;
  day_ord: string;
  month: string;
  year: number;
  fast: string | null;
  tone: string | null;
  eothinon: string | null;
  liturgy: string | null;
  desig: string | null;
  commem: string | null;
  fore_after: string | null;
  global_saints: string | null;
  british_saints: string | null;
  lections: {
    basic: string[];
    commem: string[];
    liturgy: string[];
  };
  texts: {
    basic: string[];
    commem: string[];
  };
  error?: string;
};

export function buildDateUrl(dateKey: string, baseUrl = API_BASE): string {
  const date = parseDateFromKey(dateKey);
  if (!date) {
    throw new Error("Date must be in YYYY-MM-DD format.");
  }

  const url = new URL(`${baseUrl}/date`);
  url.searchParams.set("year", String(date.getFullYear()));
  url.searchParams.set("month", String(date.getMonth() + 1));
  url.searchParams.set("day", String(date.getDate()));
  return url.toString();
}

export async function fetchDailyData(
  dateKey: string,
  fetchImpl: typeof fetch = fetch
): Promise<DatePayload> {
  const response = await fetchImpl(buildDateUrl(dateKey));
  const payload = (await response.json()) as DatePayload;

  if (!response.ok || payload.error) {
    throw new Error(payload.error ?? "Failed to load data.");
  }
  return payload;
}
