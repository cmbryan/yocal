import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import DonationScreen from "../src/screens/DonationScreen";
import * as WebBrowser from "expo-web-browser";

jest.mock("expo-web-browser", () => ({
  openBrowserAsync: jest.fn(),
}));

const mockedOpenBrowserAsync = WebBrowser.openBrowserAsync as jest.MockedFunction<
  typeof WebBrowser.openBrowserAsync
>;

describe("DonationScreen", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders donation content and opens browser on donate press", async () => {
    render(<DonationScreen />);

    expect(
      screen.getByText(
        /The Antiochian Orthodox Parish of St Constantine the Great, based in the city of York/i
      )
    ).toBeTruthy();
    expect(screen.getByText("Donate")).toBeTruthy();

    fireEvent.press(screen.getByText("Donate"));

    await waitFor(() => {
      expect(mockedOpenBrowserAsync).toHaveBeenCalledWith(
        "https://pay.sumup.com/b2c/QLQWLULC"
      );
    });
  });
});