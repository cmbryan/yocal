import AsyncStorage from "@react-native-async-storage/async-storage";
import { type AppFontId } from "./font";

const KEYS = {
  font: "settings.font",
} as const;

export interface AppSettings {
  font: AppFontId;
}

const DEFAULTS: AppSettings = {
  font: "system-sans",
};

export async function loadSettings(): Promise<AppSettings> {
  const font = await AsyncStorage.getItem(KEYS.font);
  return {
    font: (font as AppFontId) ?? DEFAULTS.font,
  };
}

export async function saveFont(font: AppFontId): Promise<void> {
  await AsyncStorage.setItem(KEYS.font, font);
}
