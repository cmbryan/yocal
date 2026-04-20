import { Platform } from "react-native";

export type AppFontId = "system-sans" | "georgia-serif" | "times-serif" | "arial-sans";

export type AppFontOption = {
  id: AppFontId;
  label: string;
};

export const APP_FONT_OPTIONS: AppFontOption[] = [
  { id: "system-sans", label: "System Sans" },
  { id: "georgia-serif", label: "Georgia Serif" },
  { id: "times-serif", label: "Times Serif" },
  { id: "arial-sans", label: "Arial Sans" },
];

export function getAppFontFamily(fontId: AppFontId): string | undefined {
  switch (fontId) {
    case "georgia-serif":
      return Platform.select({
        ios: "Georgia",
        android: "serif",
        web: "Georgia, 'Times New Roman', serif",
        default: "serif",
      });
    case "times-serif":
      return Platform.select({
        ios: "Times New Roman",
        android: "serif",
        web: "'Times New Roman', Times, serif",
        default: "serif",
      });
    case "arial-sans":
      return Platform.select({
        ios: "Arial",
        android: "sans-serif",
        web: "Arial, Helvetica, sans-serif",
        default: "sans-serif",
      });
    case "system-sans":
    default:
      return Platform.select({
        ios: "System",
        android: "sans-serif",
        web: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        default: undefined,
      });
  }
}
