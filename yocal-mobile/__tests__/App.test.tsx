import React from "react";
import { render, screen, waitFor } from "@testing-library/react-native";
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

  test("renders fetched liturgical data", async () => {
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
      expect(screen.getByText("Romans 1:1")).toBeTruthy();
      expect(screen.getByText("Readings for the Liturgy: Romans 1:1")).toBeTruthy();
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
