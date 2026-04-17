import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react-native";
import App from "../App";
import { fetchDailyData } from "../src/lib/api";

jest.mock("@react-native-community/datetimepicker", () => "DateTimePicker");
jest.mock("../src/lib/api", () => ({
  fetchDailyData: jest.fn(),
}));

const mockedFetchDailyData = fetchDailyData as jest.MockedFunction<typeof fetchDailyData>;

describe("App", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders fetched liturgical data on Home screen", async () => {
    mockedFetchDailyData.mockResolvedValue({
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
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Monday 2nd June 2025")).toBeTruthy();
      expect(screen.getByText("Fast free")).toBeTruthy();
    });
  });

  test("renders fetched liturgical data on Commemorate screen", async () => {
    mockedFetchDailyData.mockResolvedValue({
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
    });

    render(<App />);

    // Navigate to Commemorate tab
    const commemorateTab = screen.getByText("Commemorations");
    fireEvent.press(commemorateTab);

    await waitFor(() => {
      expect(screen.getByText("Saint A")).toBeTruthy();
      expect(screen.getByText("British Isles and Ireland:\nSaint B")).toBeTruthy();
    });
  });

  test("renders fetched liturgical data on Readings screen", async () => {
    mockedFetchDailyData.mockResolvedValue({
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
    });

    render(<App />);

    // Navigate to Readings tab
    const readingsTab = screen.getByText("Readings");
    fireEvent.press(readingsTab);

    await waitFor(() => {
      expect(screen.getByText("Liturgy")).toBeTruthy();
    });

    // Switch to Liturgy tab
    const liturgyTab = screen.getByText("Liturgy");
    fireEvent.press(liturgyTab);

    await waitFor(() => {
      expect(screen.getByText("Romans 1:1")).toBeTruthy();
      expect(screen.getByText("At Church")).toBeTruthy();
    });
  });

  test("shows donate tab and donation button", async () => {
    mockedFetchDailyData.mockResolvedValue({
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
    });

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
});
