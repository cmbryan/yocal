import React from "react";
import { render, screen } from "@testing-library/react-native";
import HomeScreen from "../src/screens/HomeScreen";
import { useDailyData } from "../src/lib/hooks";

jest.mock("@react-native-community/datetimepicker", () => "DateTimePicker");
jest.mock("../src/lib/hooks", () => ({
  useDailyData: jest.fn(),
}));

const mockedUseDailyData = useDailyData as jest.MockedFunction<typeof useDailyData>;

describe("HomeScreen", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders loading state initially", () => {
    mockedUseDailyData.mockReturnValue({
      data: null,
      loading: true,
      refreshing: false,
      error: null,
      reload: jest.fn(),
    });

    render(<HomeScreen activeDate={new Date(2025, 5, 2)} setActiveDate={() => {}} />);

    expect(screen.getByText("Home")).toBeTruthy();
    expect(screen.getAllByText("2025-06-02")[0]).toBeTruthy();
  });

  test("renders data after loading", () => {
    mockedUseDailyData.mockReturnValue({
      data: {
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
      },
      loading: false,
      refreshing: false,
      error: null,
      reload: jest.fn(),
    });

    render(<HomeScreen activeDate={new Date(2025, 5, 2)} setActiveDate={() => {}} />);

    expect(screen.getByText("Monday 2nd June 2025")).toBeTruthy();
    expect(screen.getByText("Fast free")).toBeTruthy();
    expect(screen.getByText("Liturgy of St John Chrysostom")).toBeTruthy();
    expect(screen.getByText("Afterfeast")).toBeTruthy();
    expect(screen.getByText("Some Commemoration")).toBeTruthy();
    expect(screen.getByText("Forefeast")).toBeTruthy();
  });

  test("renders error state", () => {
    mockedUseDailyData.mockReturnValue({
      data: null,
      loading: false,
      refreshing: false,
      error: "Network error",
      reload: jest.fn(),
    });

    render(<HomeScreen activeDate={new Date(2025, 5, 2)} setActiveDate={() => {}} />);

    expect(screen.getByText("Network error")).toBeTruthy();
  });
});