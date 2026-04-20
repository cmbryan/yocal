import React from "react";
import { render, screen, fireEvent } from "@testing-library/react-native";
import ReadingsScreen from "../src/screens/ReadingsScreen";
import { useDailyData } from "../src/lib/hooks";

jest.mock("../src/lib/hooks", () => ({
  useDailyData: jest.fn(),
}));

const mockedUseDailyData = useDailyData as jest.MockedFunction<typeof useDailyData>;

const combo0 = {
  lections: {
    basic: ["2 Timothy 4:9-22", "Matthew 23:29-39"],
    commem: ["Colossians 2:8-12", "Luke 2:20-21, 40-52"],
    liturgy: ["Colossians 2:8-12", "Luke 2:20-21, 40-52"]
  },
  texts: {
    basic: [
      "<em>2 Timothy 4:9-22</em><br>Timothy, my son, make an effort to come to me soon...",
      "<em>Matthew 23:29-39</em><br>The Lord said to the Jews who came to him..."
    ],
    commem: [
      "<em>Colossians 2:8-12</em><br>Brothers and sisters, see that no one carries you away...",
      "<em>Luke 2:20-21, 40-52</em><br>At that time the shepherds returned..."
    ]
  }
};

const combo1 = {
  lections: {
    basic: ["Titus 1:5-14", "Matthew 24:13-28"],
    commem: [],
    liturgy: ["Titus 1:5-14", "Matthew 24:13-28"]
  },
  texts: {
    basic: [
      "<em>Titus 1:5-14</em><br>Titus, my son, appoint presbyters in each city...",
      "<em>Matthew 24:13-28</em><br>The Lord said to his disciples..."
    ],
    commem: []
  }
};

describe("ReadingsScreen", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("At Home shows only basic readings when liturgy contains only commemoration readings", () => {
    const combo = combo0;
    mockedUseDailyData.mockReturnValue({
      data: {
        ...combo,
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
      },
      loading: false,
      refreshing: false,
      error: null,
      reload: jest.fn(),
    });

    render(<ReadingsScreen activeDate={new Date(2025, 5, 2)} />);

    // Default to home tab: basic minus commem
    expect(screen.getByText("2 Timothy 4:9-22")).toBeTruthy();
    expect(screen.getByText("Matthew 23:29-39")).toBeTruthy();
    expect(screen.queryByText("For the Commemoration:")).toBeNull();
    expect(screen.queryByText("Colossians 2:8-12")).toBeNull();
    expect(screen.queryByText("Luke 2:20-21, 40-52")).toBeNull();
    // Texts: only basic
    expect(screen.getByText("2 Timothy 4:9-22\nTimothy, my son, make an effort to come to me soon...")).toBeTruthy();
    expect(screen.getByText("Matthew 23:29-39\nThe Lord said to the Jews who came to him...")).toBeTruthy();
  });

  test("Liturgy shows the same readings as At Home when there are no commemoration readings", () => {
    const combo = combo1;
    mockedUseDailyData.mockReturnValue({
      data: {
        ...combo,
        day_name: "Sunday",
        day_ord: "28th",
        month: "December",
        year: 2025,
        fast: null,
        tone: "Tone 4",
        eothinon: "Eothinon 7",
        liturgy: "Liturgy of St John Chrysostom",
        desig: "Sunday After the Nativity",
        commem: null,
        fore_after: "Afterfeast",
        global_saints: "Saint B",
        british_saints: "",
      },
      loading: false,
      refreshing: false,
      error: null,
      reload: jest.fn(),
    });

    render(<ReadingsScreen activeDate={new Date(2025, 11, 28)} />);

    // Home tab: basic
    expect(screen.getByText("Titus 1:5-14")).toBeTruthy();
    expect(screen.getByText("Matthew 24:13-28")).toBeTruthy();
    expect(screen.queryByText("For the Commemoration:")).toBeNull();

    // Switch to liturgy tab: same as basic
    fireEvent.press(screen.getByText("At Church"));
    expect(screen.getAllByText("At Church").length).toBeGreaterThan(0);
    expect(screen.getByText("Titus 1:5-14")).toBeTruthy();
    expect(screen.getByText("Matthew 24:13-28")).toBeTruthy();
    expect(screen.queryByText("For the Commemoration:")).toBeNull();
  });

  test("Liturgy shows only commemoration readings when liturgy excludes all basic readings", () => {
    const combo = combo0;
    mockedUseDailyData.mockReturnValue({
      data: {
        ...combo,
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
      },
      loading: false,
      refreshing: false,
      error: null,
      reload: jest.fn(),
    });

    render(<ReadingsScreen activeDate={new Date(2025, 0, 1)} />);

    // Switch to liturgy tab: shows commem
    fireEvent.press(screen.getByText("At Church"));
    expect(screen.getAllByText("At Church").length).toBeGreaterThan(0);
    expect(screen.getByText("For the Commemoration:")).toBeTruthy();
    expect(screen.getByText("Colossians 2:8-12")).toBeTruthy();
    expect(screen.getByText("Luke 2:20-21, 40-52")).toBeTruthy();
  });

  test("Liturgy shows the no-liturgy message and hides texts when there is no liturgy", () => {
    mockedUseDailyData.mockReturnValue({
      data: {
        lections: {
          basic: ["Isaiah 1:1-20", "Genesis 1:1-13"],
          commem: [],
          liturgy: [],
        },
        texts: {
          basic: [
            "<em>Isaiah 1:1-20</em><br>The vision of Isaiah...",
            "<em>Genesis 1:1-13</em><br>In the beginning..."
          ],
          commem: [],
        },
        day_name: "Monday",
        day_ord: "2nd",
        month: "March",
        year: 2025,
        fast: "Great Lent",
        tone: null,
        eothinon: null,
        liturgy: "",
        desig: "Great Lent",
        commem: null,
        fore_after: null,
        global_saints: "Saint A",
        british_saints: "Saint B",
      },
      loading: false,
      refreshing: false,
      error: null,
      reload: jest.fn(),
    });

    render(<ReadingsScreen activeDate={new Date(2025, 2, 3)} />);

    // Switch to liturgy tab
    fireEvent.press(screen.getByText("At Church"));
    expect(screen.getAllByText("At Church").length).toBeGreaterThan(0);
    expect(screen.getByText("There is no liturgy on this day.")).toBeTruthy();
    // Texts section should not be present
    expect(screen.queryByText("Texts")).toBeNull();
  });

  test("splits mixed liturgy readings between At Home and Liturgy using the real API combination", () => {
    mockedUseDailyData.mockReturnValue({
      data: {
        lections: {
          basic: ["Acts 4:13-22", "John 5:17-24"],
          commem: ["Acts 12:1-11", "Luke 9:1-6"],
          liturgy: ["Acts 12:1-11", "John 5:17-24"],
        },
        texts: {
          basic: [
            "<em>Acts 4:13-22</em><br>In those days when the Jews saw the assurance of Peter and John...",
            "<em>John 5:17-24</em><br>The Lord said to the Jews who came to him...",
          ],
          commem: [
            "<em>Acts 12:1-11</em><br>At that time Herod the king stretched out his hand to inflict evil...",
            "<em>Luke 9:1-6</em><br>At that time Jesus called together his twelve disciples...",
          ],
        },
        day_name: "Friday",
        day_ord: "25th",
        month: "April",
        year: 2025,
        fast: null,
        tone: null,
        eothinon: null,
        liturgy: "Liturgy of St John Chrysostom",
        desig: null,
        commem: "Saint Mark",
        fore_after: null,
        global_saints: "Saint C",
        british_saints: "",
      },
      loading: false,
      refreshing: false,
      error: null,
      reload: jest.fn(),
    });

    render(<ReadingsScreen activeDate={new Date(2025, 3, 25)} />);

    // At Home: remove liturgy readings but keep the remaining non-liturgy basic and commem
    expect(screen.getByText("Acts 4:13-22")).toBeTruthy();
    expect(screen.getByText("For the Commemoration:")).toBeTruthy();
    expect(screen.getByText("Luke 9:1-6")).toBeTruthy();
    expect(screen.queryByText("John 5:17-24")).toBeNull();
    expect(screen.queryByText("Acts 12:1-11")).toBeNull();

    // At Home texts: only non-liturgy basic and non-liturgy commem text remain
    expect(screen.getByText("Acts 4:13-22\nIn those days when the Jews saw the assurance of Peter and John...")).toBeTruthy();
    expect(screen.getByText("Luke 9:1-6\nAt that time Jesus called together his twelve disciples...")).toBeTruthy();
    expect(screen.queryByText("John 5:17-24\nThe Lord said to the Jews who came to him...")).toBeNull();
    expect(screen.queryByText("Acts 12:1-11\nAt that time Herod the king stretched out his hand to inflict evil...")).toBeNull();

    // Liturgy: include one basic and one commem, with commem heading
    fireEvent.press(screen.getByText("At Church"));
    expect(screen.getAllByText("At Church").length).toBeGreaterThan(0);
    expect(screen.getByText("John 5:17-24")).toBeTruthy();
    expect(screen.getByText("For the Commemoration:")).toBeTruthy();
    expect(screen.getByText("Acts 12:1-11")).toBeTruthy();
    expect(screen.queryByText("Acts 4:13-22")).toBeNull();
    expect(screen.queryByText("Luke 9:1-6")).toBeNull();
  });
});