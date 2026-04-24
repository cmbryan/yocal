import React from "react";
import { fireEvent, render, screen } from "@testing-library/react-native";
import PrayersScreen from "../src/screens/PrayersScreen";

jest.mock("../src/lib/prayers", () => ({
  MORNING_PRAYER_SOURCE_URL: "https://example.com/morning",
  EVENING_PRAYER_SOURCE_URL: "https://example.com/evening",
  THIRD_SIXTH_SOURCE_URL: "https://example.com/third-sixth",
  EVENING_PRAYER_TEXT: "Evening prayer text",
  THIRD_HOUR_PRAYER_TEXT: "## Psalm 116\n\nThird hour prayer text",
  SIXTH_HOUR_PRAYER_TEXT: "## Psalm 53\n\nSixth hour prayer text",
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

  test("keeps Third Hour and Sixth Hour collapsed by default", () => {
    render(<PrayersScreen activeDate={new Date(2026, 3, 20)} />);

    expect(screen.queryByText("Psalm 116")).toBeNull();
    expect(screen.queryByText("Third hour prayer text")).toBeNull();
    expect(screen.queryByText("Psalm 53")).toBeNull();
    expect(screen.queryByText("Sixth hour prayer text")).toBeNull();
    expect(screen.queryByText("Source: https://example.com/third-sixth")).toBeNull();
  });

  test("shows Third Hour content and source when expanded", () => {
    render(<PrayersScreen activeDate={new Date(2026, 3, 20)} />);

    fireEvent.press(screen.getByText("Third Hour"));

    expect(screen.getByText("Psalm 116")).toBeTruthy();
    expect(screen.getByText("Third hour prayer text")).toBeTruthy();
    expect(screen.getByText("Source: https://example.com/third-sixth")).toBeTruthy();
  });

  test("shows Sixth Hour content and source when expanded", () => {
    render(<PrayersScreen activeDate={new Date(2026, 3, 20)} />);

    fireEvent.press(screen.getByText("Sixth Hour"));

    expect(screen.getByText("Psalm 53")).toBeTruthy();
    expect(screen.getByText("Sixth hour prayer text")).toBeTruthy();
    expect(screen.getByText("Source: https://example.com/third-sixth")).toBeTruthy();
  });

  test("on Sunday, Typika replaces Morning Prayer and Third Hour still works", () => {
    render(<PrayersScreen activeDate={new Date(2026, 3, 19)} />);

    expect(screen.getByText("Typika")).toBeTruthy();
    expect(screen.queryByText("Morning Prayer")).toBeNull();

    fireEvent.press(screen.getByText("Third Hour"));

    expect(screen.getByText("Psalm 116")).toBeTruthy();
    expect(screen.getByText("Third hour prayer text")).toBeTruthy();
  });
});
