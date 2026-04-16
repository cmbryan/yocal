import React from "react";
import { render, screen } from "@testing-library/react-native";
import CommemorateScreen from "../src/screens/CommemorateScreen";
import { useDailyData } from "../src/lib/hooks";

jest.mock("../src/lib/hooks", () => ({
  useDailyData: jest.fn(),
}));

const mockedUseDailyData = useDailyData as jest.MockedFunction<typeof useDailyData>;

describe("CommemorateScreen", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders saints data", () => {
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

    render(<CommemorateScreen activeDate={new Date(2025, 5, 2)} />);

    expect(screen.getByText("Saint A")).toBeTruthy();
    expect(screen.getByText("British Isles and Ireland:\nSaint B")).toBeTruthy();
  });
});