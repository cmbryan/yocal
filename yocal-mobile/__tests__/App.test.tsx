import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react-native";
import { Alert, Platform } from "react-native";
import App from "../App";
import {
  fetchDailyDataWithOfflineCache,
  prefetchOfflineDateRange,
} from "../src/lib/offlineCache";

jest.mock("@react-native-community/datetimepicker", () => "DateTimePicker");
jest.mock("../src/lib/offlineCache", () => ({
  fetchDailyDataWithOfflineCache: jest.fn(),
  prefetchOfflineDateRange: jest.fn(),
}));
jest.mock("../src/lib/settings", () => ({
  loadSettings: jest.fn().mockResolvedValue({ font: "system-sans" }),
  saveFont: jest.fn(),
}));

import { loadSettings, saveFont } from "../src/lib/settings";
const mockedLoadSettings = loadSettings as jest.MockedFunction<typeof loadSettings>;
const mockedSaveFont = saveFont as jest.MockedFunction<typeof saveFont>;

const mockedFetchDailyData = fetchDailyDataWithOfflineCache as jest.MockedFunction<typeof fetchDailyDataWithOfflineCache>;
const mockedPrefetchOfflineDateRange = prefetchOfflineDateRange as jest.MockedFunction<typeof prefetchOfflineDateRange>;

const samplePayload = {
  day_name: "Monday",
  day_ord: "2nd",
  month: "June",
  year: 2025,
  fast: "Fast free",
  tone: null,
  eothinon: null,
  liturgy: "Liturgy of St John Chrysostom",
  desig: "Afterfeast",
  commem: "Some Commemoration",
  fore_after: "Forefeast",
  global_saints: "Saint A",
  british_saints: "Saint B",
  lections: {
    basic: ["Romans 1:1"],
    commem: [],
    liturgy: ["Romans 1:1"],
  },
  texts: {
    basic: ["<em>Romans 1:1</em><br>Some text"],
    commem: [],
  },
};

describe("App", () => {
  let originalPlatform: string;

  beforeEach(() => {
    jest.clearAllMocks();
    originalPlatform = Platform.OS;
    (Platform as { OS: string }).OS = "ios";
    mockedFetchDailyData.mockResolvedValue(samplePayload);
    mockedPrefetchOfflineDateRange.mockResolvedValue({ cachedCount: 30, failedDates: [] });
  });

  afterEach(() => {
    (Platform as { OS: string }).OS = originalPlatform;
  });

  test("renders fetched liturgical data on Home screen", async () => {
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Monday 2nd June 2025")).toBeTruthy();
      expect(screen.getByText("Fast free")).toBeTruthy();
      expect(screen.getByText("Saint A")).toBeTruthy();
      expect(screen.getByText("British Isles and Ireland:\nSaint B")).toBeTruthy();
    });
  });

  test("renders fetched liturgical data on Readings screen", async () => {
    render(<App />);

    // Navigate to Readings tab
    const readingsTab = screen.getByText("Readings");
    fireEvent.press(readingsTab);

    await waitFor(() => {
      expect(screen.getAllByText("At Home").length).toBeGreaterThan(0);
    });

    // Switch to At Church tab
    const liturgyTab = screen.getByText("At Church");
    fireEvent.press(liturgyTab);

    await waitFor(() => {
      expect(screen.getByText("Romans 1:1")).toBeTruthy();
      expect(screen.getAllByText("At Church").length).toBeGreaterThan(0);
    });
  });

  test("shows donate tab and donation button", async () => {
    render(<App />);

    const donateTab = screen.getByText("Donate");
    fireEvent.press(donateTab);

    await waitFor(() => {
      expect(screen.getAllByText("Donate").length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText(/The Antiochian Orthodox Parish of St Constantine the Great/i)).toBeTruthy();
    });
  });

  test("shows friendly CORS message for fetch failure", async () => {
    mockedFetchDailyData.mockRejectedValue(new Error("Failed to fetch"));

    render(<App />);

    await waitFor(() => {
      expect(
        screen.getByText(
          "Failed to fetch data from the API. If you are on web, this is usually a CORS issue until the API deploy includes CORS headers."
        )
      ).toBeTruthy();
    });
  });

  test("opens settings menu and allows font selection", async () => {
    render(<App />);

    fireEvent.press(screen.getByLabelText("Open settings"));

    expect(screen.getByText("Settings")).toBeTruthy();
    expect(screen.getByText("System Sans")).toBeTruthy();

    fireEvent.press(screen.getByLabelText("Select Georgia Serif"));

    expect(screen.getByText("Georgia Serif")).toBeTruthy();
  });

  test("shows offline mode only on mobile and confirms when caching completes", async () => {
    const alertSpy = jest.spyOn(Alert, "alert").mockImplementation(() => undefined);
    render(<App />);

    fireEvent.press(screen.getByLabelText("Open settings"));
    expect(screen.getByText("Offline mode")).toBeTruthy();

    fireEvent(screen.getByLabelText("Toggle Offline mode"), "valueChange", true);

    await waitFor(() => {
      expect(mockedPrefetchOfflineDateRange).toHaveBeenCalledTimes(1);
      expect(alertSpy).toHaveBeenCalledWith(
        "Offline cache complete",
        "Cached 30 days for offline use.",
      );
    });
  });

  test("hides offline mode on web", async () => {
    (Platform as { OS: string }).OS = "web";
    render(<App />);

    fireEvent.press(screen.getByLabelText("Open settings"));

    expect(screen.queryByText("Offline")).toBeNull();
    expect(screen.queryByText("Offline mode")).toBeNull();
  });

  test("saves font to storage when font is selected", async () => {
    render(<App />);

    fireEvent.press(screen.getByLabelText("Open settings"));
    fireEvent.press(screen.getByLabelText("Select Georgia Serif"));

    expect(mockedSaveFont).toHaveBeenCalledWith("georgia-serif");
  });

  test("loads and applies saved font on startup", async () => {
    mockedLoadSettings.mockResolvedValueOnce({ font: "georgia-serif" });

    render(<App />);

    await waitFor(() => {
      fireEvent.press(screen.getByLabelText("Open settings"));
      const georgiaOption = screen.getByLabelText("Select Georgia Serif");
      expect(georgiaOption.props.accessibilityState?.checked).toBe(true);
    });
  });
});
