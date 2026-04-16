import React from "react";
import { render, screen, waitFor, act } from "@testing-library/react-native";
import HomeScreen from "../src/screens/HomeScreen";
import { fetchDailyData } from "../src/lib/api";

jest.mock("@react-native-community/datetimepicker", () => "DateTimePicker");
jest.mock("../src/lib/api", () => ({
  fetchDailyData: jest.fn(),
}));

const mockedFetchDailyData = fetchDailyData as jest.MockedFunction<typeof fetchDailyData>;

describe("HomeScreen", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders loading state initially", () => {
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

    render(<HomeScreen activeDate={new Date(2025, 5, 2)} setActiveDate={() => {}} />);

    expect(screen.getByText("Home")).toBeTruthy();
    expect(screen.getByText("2025-06-02")).toBeTruthy();
  });

  test("renders data after loading", async () => {
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

    render(<HomeScreen activeDate={new Date(2025, 5, 2)} setActiveDate={() => {}} />);

    await waitFor(() => {
      expect(screen.getByText("Monday 2nd June 2025")).toBeTruthy();
      expect(screen.getByText("Fast free")).toBeTruthy();
      expect(screen.getByText("Liturgy of St John Chrysostom")).toBeTruthy();
      expect(screen.getByText("Afterfeast")).toBeTruthy();
      expect(screen.getByText("Some Commemoration")).toBeTruthy();
      expect(screen.getByText("Forefeast")).toBeTruthy();
    });
  });

  test("renders error state", async () => {
    mockedFetchDailyData.mockRejectedValue(new Error("Network error"));

    render(<HomeScreen activeDate={new Date(2025, 5, 2)} setActiveDate={() => {}} />);

    await waitFor(() => {
      expect(screen.getByText("Network error")).toBeTruthy();
    });
  });
});