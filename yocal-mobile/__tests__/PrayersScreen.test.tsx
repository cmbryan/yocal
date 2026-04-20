import React from "react";
import { fireEvent, render, screen } from "@testing-library/react-native";
import PrayersScreen from "../src/screens/PrayersScreen";

jest.mock("../src/lib/prayers", () => ({
  MORNING_PRAYER_SOURCE_URL: "https://example.com/morning",
  EVENING_PRAYER_SOURCE_URL: "https://example.com/evening",
  EVENING_PRAYER_TEXT: "Evening prayer text",
  getMorningPrayerTextForDate: jest.fn(() => "Morning prayer text"),
}));

jest.mock("../src/lib/typika", () => ({
  TYPIKA_SOURCE_URL: "https://example.com/typika",
  getTypikaSections: jest.fn(() => ({
    beforeReadings: "Typika content before readings",
    afterReadings: "Typika content after readings",
  })),
}));

describe("PrayersScreen", () => {
  test("on Sunday, tapping Readings link navigates to Readings with liturgy selected", () => {
    const navigate = jest.fn();

    render(
      <PrayersScreen
        activeDate={new Date(2026, 3, 19)}
        navigation={{ navigate }}
      />,
    );

    // Expand Typika section (starts collapsed)
    fireEvent.press(screen.getByText("Typika"));
    fireEvent.press(screen.getByText("Readings"));

    expect(navigate).toHaveBeenCalledWith("Readings", { selectedTab: "liturgy" });
  });

  test("on non-Sunday, Typika Readings link is not shown", () => {
    render(<PrayersScreen activeDate={new Date(2026, 3, 20)} />);

    expect(screen.queryByText("Readings")).toBeNull();
    expect(screen.getByText("Morning Prayer")).toBeTruthy();
  });
});
