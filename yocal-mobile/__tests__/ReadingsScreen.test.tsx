import React from "react";
import { render, screen, fireEvent } from "@testing-library/react-native";
import ReadingsScreen from "../src/screens/ReadingsScreen";
import { useDailyData } from "../src/lib/hooks";

jest.mock("../src/lib/hooks", () => ({
  useDailyData: jest.fn(),
}));

const mockedUseDailyData = useDailyData as jest.MockedFunction<typeof useDailyData>;

describe("ReadingsScreen", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders readings data", () => {
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
          basic: ["Romans 1:1", "Romans 1:2"],
          commem: ["Psalm 1"],
          liturgy: ["Romans 1:1"],
        },
        texts: {
          basic: ["<em>Romans 1:1</em><br>Some text", "<em>Romans 1:2</em><br>More text"],
          commem: ["<b>Psalm 1</b><br>Text"],
        },
      },
      loading: false,
      refreshing: false,
      error: null,
      reload: jest.fn(),
    });

    render(<ReadingsScreen activeDate={new Date(2025, 5, 2)} />);

    // Default to home tab with liturgy subtraction
    expect(screen.queryByText("Romans 1:1")).toBeNull();
    expect(screen.getByText("Romans 1:2")).toBeTruthy();
    expect(screen.getByText("For the Commemoration:")).toBeTruthy();
    expect(screen.getByText("Psalm 1")).toBeTruthy();
    expect(screen.getByText("Romans 1:2\nMore text")).toBeTruthy();
    expect(screen.getByText("Psalm 1\nText")).toBeTruthy();
  });

  test("separates bolded and non-bolded readings for home and liturgy tabs on 28 Dec 2025", () => {
    mockedUseDailyData.mockReturnValue({
      data: {
        day_name: "Sunday",
        day_ord: "28th",
        month: "December",
        year: 2025,
        fast: null,
        tone: "Tone 4",
        eothinon: "Eothinon 7",
        liturgy: "Liturgy of St John Chrysostom",
        desig: "Sunday After the Nativity of our Lord and Saviour Jesus Christ",
        commem: "Twenty Thousand Holy Martyrs of Nicomedia",
        fore_after: "Afterfeast of The Nativity of Christ",
        global_saints: "St. Joseph the Betrothed. St. David the Psalmist. St. James the brother of the Lord. Among the 20,000 Martyrs of Nicomedia: Glycerius the presbyter, Zeno, Theophilus, Dorotheus, Mardonius, Migdonius, Indes, Gorgonius, Peter, Euthymius, and the virgins Agape, Domna, Theophila and others (302). St. Nicanor the deacon, Apostle of the Seventy (38). St. Simon the Myrhh-streaming, founder of Simonopetra monastery on Mt Athos (14th C).",
        british_saints: "",
        lections: {
          basic: ["Galatians 1:11-19", "Matthew 2:13-23"],
          commem: ["Hebrews 10:35-11:7", "Luke 14:25-35"],
          liturgy: ["Galatians 1:11-19", "Matthew 2:13-23"],
        },
        texts: {
          basic: [
            "<em>Galatians 1:11-19</em><br>Text",
            "<em>Matthew 2:13-23</em><br>Text",
          ],
          commem: [
            "<em>Hebrews 10:35-11:7</em><br>Text",
            "<em>Luke 14:25-35</em><br>Text",
          ],
        },
      },
      loading: false,
      refreshing: false,
      error: null,
      reload: jest.fn(),
    });

    render(<ReadingsScreen activeDate={new Date(2025, 11, 28)} />);

    // Default to home tab, shows basic and commem
    expect(screen.queryByText("Galatians 1:11-19")).toBeNull();
    expect(screen.queryByText("Matthew 2:13-23")).toBeNull();
    expect(screen.getByText("Hebrews 10:35-11:7")).toBeTruthy();
    expect(screen.getByText("Luke 14:25-35")).toBeTruthy();
    expect(screen.getByText("Hebrews 10:35-11:7\nText")).toBeTruthy();
    expect(screen.getByText("Luke 14:25-35\nText")).toBeTruthy();

    // Switch to liturgy tab, since no separate liturgy readings exist, shows same as home
    fireEvent.press(screen.getByText("Liturgy"));
    expect(screen.getByText("At Church")).toBeTruthy();
    expect(screen.getByText("Galatians 1:11-19")).toBeTruthy();
    expect(screen.getByText("Matthew 2:13-23")).toBeTruthy();
    expect(screen.queryByText("Hebrews 10:35-11:7")).toBeNull();
    expect(screen.queryByText("Luke 14:25-35")).toBeNull();
    expect(screen.getByText("Galatians 1:11-19\nText")).toBeTruthy();
    expect(screen.getByText("Matthew 2:13-23\nText")).toBeTruthy();
  });
});