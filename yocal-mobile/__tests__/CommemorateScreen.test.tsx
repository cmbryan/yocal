import React from "react";
import { render, screen, waitFor, act } from "@testing-library/react-native";
import CommemorateScreen from "../src/screens/CommemorateScreen";
import { fetchDailyData } from "../src/lib/api";

jest.mock("../src/lib/api", () => ({
  fetchDailyData: jest.fn(),
}));

const mockedFetchDailyData = fetchDailyData as jest.MockedFunction<typeof fetchDailyData>;

describe("CommemorateScreen", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders saints data", async () => {
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

    render(<CommemorateScreen activeDate={new Date(2025, 5, 2)} />);

    await waitFor(() => {
      expect(screen.getByText("Saint A")).toBeTruthy();
      expect(screen.getByText("British Isles and Ireland:\nSaint B")).toBeTruthy();
    });
  });
});