import React from "react";
import { render, screen, waitFor, act } from "@testing-library/react-native";
import ReadingsScreen from "../src/screens/ReadingsScreen";
import { fetchDailyData } from "../src/lib/api";

jest.mock("../src/lib/api", () => ({
  fetchDailyData: jest.fn(),
}));

const mockedFetchDailyData = fetchDailyData as jest.MockedFunction<typeof fetchDailyData>;

describe("ReadingsScreen", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders readings data", async () => {
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
        basic: ["Romans 1:1", "Romans 1:2"],
        commem: ["Psalm 1"],
        liturgy: ["Romans 1:1"],
      },
      texts: {
        basic: ["<em>Romans 1:1</em><br>Some text", "<em>Romans 1:2</em><br>More text"],
        commem: ["<b>Psalm 1</b><br>Text"],
      },
    });

    render(<ReadingsScreen activeDate={new Date(2025, 5, 2)} />);

    await waitFor(() => {
      expect(screen.getByText("Romans 1:1")).toBeTruthy();
      expect(screen.getByText("Romans 1:2")).toBeTruthy();
      expect(screen.getByText("For the Commemoration:")).toBeTruthy();
      expect(screen.getByText("Psalm 1")).toBeTruthy();
      expect(screen.getByText("Readings for the Liturgy: Romans 1:1")).toBeTruthy();
      expect(screen.getByText("Romans 1:1\nSome text")).toBeTruthy();
      expect(screen.getByText("Romans 1:2\nMore text")).toBeTruthy();
      expect(screen.getByText("Psalm 1\nText")).toBeTruthy();
    });
  });
});