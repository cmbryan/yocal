import { useCallback, useEffect, useState } from "react";
import { type DatePayload } from "./api";
import { fetchDailyDataWithOfflineCache } from "./offlineCache";

export function useDailyData(dateKey: string, offlineMode = false) {
  const [data, setData] = useState<DatePayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(
    async (isRefresh = false) => {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);
      try {
        const payload = await fetchDailyDataWithOfflineCache(dateKey, offlineMode);
        setData(payload);
      } catch (err) {
        const rawMessage =
          err instanceof Error ? err.message : "Unexpected error.";
        const message =
          rawMessage === "Failed to fetch"
            ? "Failed to fetch data from the API. If you are on web, this is usually a CORS issue until the API deploy includes CORS headers."
            : rawMessage;
        setError(message);
        setData(null);
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [dateKey, offlineMode]
  );

  useEffect(() => {
    void load();
  }, [load]);

  return { data, loading, refreshing, error, reload: load };
}