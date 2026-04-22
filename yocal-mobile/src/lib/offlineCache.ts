import AsyncStorage from "@react-native-async-storage/async-storage";
import { formatDateKey } from "./date";
import { fetchDailyData, type DatePayload } from "./api";

const OFFLINE_CACHE_KEY = "yocal.offline-cache.v1";
const OFFLINE_CACHE_MAX_AGE_MS = 45 * 24 * 60 * 60 * 1000;

type CacheEntry = {
  cachedAt: number;
  payload: DatePayload;
};

type CacheMap = Record<string, CacheEntry>;

async function loadCacheMap(): Promise<CacheMap> {
  const raw = await AsyncStorage.getItem(OFFLINE_CACHE_KEY);
  if (!raw) {
    return {};
  }

  try {
    return JSON.parse(raw) as CacheMap;
  } catch {
    return {};
  }
}

async function saveCacheMap(cacheMap: CacheMap): Promise<void> {
  await AsyncStorage.setItem(OFFLINE_CACHE_KEY, JSON.stringify(cacheMap));
}

async function writeCacheEntry(dateKey: string, payload: DatePayload): Promise<void> {
  const cacheMap = await loadCacheMap();
  cacheMap[dateKey] = {
    cachedAt: Date.now(),
    payload,
  };
  await saveCacheMap(cacheMap);
}

export async function getCachedDailyData(dateKey: string): Promise<DatePayload | null> {
  const cacheMap = await loadCacheMap();
  const entry = cacheMap[dateKey];
  if (!entry) {
    return null;
  }
  if (Date.now() - entry.cachedAt > OFFLINE_CACHE_MAX_AGE_MS) {
    delete cacheMap[dateKey];
    await saveCacheMap(cacheMap);
    return null;
  }
  return entry.payload;
}

export async function fetchDailyDataWithOfflineCache(
  dateKey: string,
  offlineMode: boolean,
  fetchImpl: typeof fetch = fetch,
): Promise<DatePayload> {
  if (!offlineMode) {
    return fetchDailyData(dateKey, fetchImpl);
  }

  try {
    const payload = await fetchDailyData(dateKey, fetchImpl);
    await writeCacheEntry(dateKey, payload);
    return payload;
  } catch (error) {
    const cached = await getCachedDailyData(dateKey);
    if (cached) {
      return cached;
    }
    throw error;
  }
}

function addDays(date: Date, daysToAdd: number): Date {
  const next = new Date(date);
  next.setDate(next.getDate() + daysToAdd);
  return next;
}

export async function prefetchOfflineDateRange(
  startDate: Date,
  numberOfDays = 30,
  fetchImpl: typeof fetch = fetch,
): Promise<{ cachedCount: number; failedDates: string[] }> {
  let cachedCount = 0;
  const failedDates: string[] = [];

  for (let dayOffset = 0; dayOffset < numberOfDays; dayOffset += 1) {
    const dateKey = formatDateKey(addDays(startDate, dayOffset));
    try {
      const payload = await fetchDailyData(dateKey, fetchImpl);
      await writeCacheEntry(dateKey, payload);
      cachedCount += 1;
    } catch {
      failedDates.push(dateKey);
    }
  }

  return { cachedCount, failedDates };
}

export async function clearOfflineCache(): Promise<void> {
  await AsyncStorage.removeItem(OFFLINE_CACHE_KEY);
}
