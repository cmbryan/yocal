import AsyncStorage from "@react-native-async-storage/async-storage";
import { fetchDailyData } from "../src/lib/api";
import {
  fetchDailyDataWithOfflineCache,
  getCachedDailyData,
  prefetchOfflineDateRange,
} from "../src/lib/offlineCache";

jest.mock("../src/lib/api", () => ({
  fetchDailyData: jest.fn(),
}));

const mockedFetchDailyData = fetchDailyData as jest.MockedFunction<typeof fetchDailyData>;

const samplePayload = {
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

describe("offline cache", () => {
  beforeEach(async () => {
    jest.clearAllMocks();
    await AsyncStorage.clear();
  });

  test("fetchDailyDataWithOfflineCache stores network payload and can read it", async () => {
    mockedFetchDailyData.mockResolvedValue(samplePayload);

    const payload = await fetchDailyDataWithOfflineCache("2025-06-02", true);
    const cached = await getCachedDailyData("2025-06-02");

    expect(payload).toEqual(samplePayload);
    expect(cached).toEqual(samplePayload);
  });

  test("fetchDailyDataWithOfflineCache falls back to cached payload", async () => {
    mockedFetchDailyData.mockResolvedValueOnce(samplePayload);
    await fetchDailyDataWithOfflineCache("2025-06-02", true);

    mockedFetchDailyData.mockRejectedValueOnce(new Error("Failed to fetch"));
    const payload = await fetchDailyDataWithOfflineCache("2025-06-02", true);

    expect(payload).toEqual(samplePayload);
  });

  test("prefetchOfflineDateRange attempts all dates and reports failures", async () => {
    mockedFetchDailyData.mockImplementation(async (dateKey) => {
      if (dateKey === "2025-06-03") {
        throw new Error("no data");
      }
      return samplePayload;
    });

    const result = await prefetchOfflineDateRange(new Date(2025, 5, 2), 3);

    expect(result.cachedCount).toBe(2);
    expect(result.failedDates).toEqual(["2025-06-03"]);
    expect(mockedFetchDailyData).toHaveBeenCalledTimes(3);
  });
});
