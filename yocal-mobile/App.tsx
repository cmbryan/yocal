import { StatusBar } from "expo-status-bar";
import { useEffect, useState } from "react";
import {
  Alert,
  Image,
  Modal,
  Platform,
  Pressable,
  StyleSheet,
  Switch,
  Text,
  View,
} from "react-native";
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import DateTimePicker, { type DateTimePickerEvent } from "@react-native-community/datetimepicker";
import HomeScreen from "./src/screens/HomeScreen";
import ReadingsScreen from "./src/screens/ReadingsScreen";
import PrayersScreen from "./src/screens/PrayersScreen";
import DonationScreen from "./src/screens/DonationScreen";
import { formatDateKey, parseDateFromKey } from "./src/lib/date";
import { APP_FONT_OPTIONS, type AppFontId, getAppFontFamily } from "./src/lib/font";
import { prefetchOfflineDateRange } from "./src/lib/offlineCache";
import { loadSettings, saveFont } from "./src/lib/settings";

const Tab = createBottomTabNavigator();

const webDatePickerInputStyle: Record<string, string | number> = {
  height: 40,
  borderWidth: 1,
  borderColor: "#d1d5db",
  borderRadius: 8,
  paddingLeft: 10,
  paddingRight: 10,
  fontSize: 16,
  backgroundColor: "#ffffff",
  color: "#111827",
  minWidth: 180,
};

export default function App() {
  const [activeDate, setActiveDate] = useState(() => new Date());
  const [showPicker, setShowPicker] = useState(false);
  const [showSettingsMenu, setShowSettingsMenu] = useState(false);
  const [selectedFont, setSelectedFont] = useState<AppFontId>("system-sans");
  const [offlineMode, setOfflineMode] = useState(false);

  useEffect(() => {
    loadSettings().then((s) => setSelectedFont(s.font));
  }, []);

  const onSelectFont = (fontId: AppFontId) => {
    setSelectedFont(fontId);
    saveFont(fontId);
  };
  const [cacheInProgress, setCacheInProgress] = useState(false);

  const textFontStyle = { fontFamily: getAppFontFamily(selectedFont) };
  const activeDateKey = formatDateKey(activeDate);

  const onNativeDateChange = (
    event: DateTimePickerEvent,
    selectedDate?: Date,
  ) => {
    if (Platform.OS === "android") {
      setShowPicker(false);
    }
    if (event.type === "dismissed" || !selectedDate) {
      return;
    }
    setActiveDate(selectedDate);
  };

  const onToggleOfflineMode = () => {
    const nextMode = !offlineMode;
    setOfflineMode(nextMode);

    if (!nextMode || Platform.OS === "web") {
      return;
    }

    setCacheInProgress(true);
    void prefetchOfflineDateRange(activeDate, 30)
      .then(({ cachedCount, failedDates }) => {
        if (failedDates.length === 0) {
          Alert.alert(
            "Offline cache complete",
            `Cached ${cachedCount} days for offline use.`,
          );
          return;
        }

        Alert.alert(
          "Offline cache complete",
          `Cached ${cachedCount} days. ${failedDates.length} days could not be cached.`,
        );
      })
      .catch((error) => {
        const message = error instanceof Error ? error.message : "Unexpected error.";
        Alert.alert("Offline cache failed", message);
      })
      .finally(() => {
        setCacheInProgress(false);
      });
  };

  return (
    <NavigationContainer>
      <StatusBar style="dark" />
      <View style={styles.appContainer}>
        <View style={styles.appLayout}>
          <Tab.Navigator
            screenOptions={{
              tabBarActiveTintColor: "#1d4ed8",
              tabBarInactiveTintColor: "#6b7280",
              tabBarStyle: {
                backgroundColor: "#ffffff",
                borderTopColor: "#e5e7eb",
                borderTopWidth: 1,
              },
              tabBarLabelStyle: {
                fontFamily: textFontStyle.fontFamily,
              },
              headerStyle: {
                backgroundColor: "#f3f4f6",
              },
              headerTintColor: "#111827",
              headerTitleStyle: {
                fontWeight: "bold",
                fontSize: 24,
                fontFamily: textFontStyle.fontFamily,
              },
              headerLeftContainerStyle: {
                paddingLeft: 0,
              },
              headerLeft: () => (
                <Image
                  source={require("./assets/jerusalem_cross.gif")}
                  style={styles.headerLeftImage}
                />
              ),
              headerRight: () => (
                <View style={styles.headerDatePickerRow}>
                  {Platform.OS === "web" ? (
                    <input
                      type="date"
                      value={activeDateKey}
                      onChange={(event) => {
                        const selected = parseDateFromKey(event.target.value);
                        if (selected) {
                          setActiveDate(selected);
                        }
                      }}
                      style={webDatePickerInputStyle}
                    />
                  ) : (
                    <>
                      <Pressable
                        style={styles.buttonPrimary}
                        onPress={() => setShowPicker(true)}
                      >
                        <Text style={[styles.buttonPrimaryText, textFontStyle]}>Select Date</Text>
                      </Pressable>
                      <Text style={[styles.headerDateLabel, textFontStyle]}>{activeDateKey}</Text>
                    </>
                  )}
                  <Pressable
                    accessibilityRole="button"
                    accessibilityLabel="Open settings"
                    onPress={() => setShowSettingsMenu(true)}
                    style={styles.settingsButton}
                  >
                    <Text style={[styles.settingsButtonText, textFontStyle]}>☰</Text>
                  </Pressable>
                </View>
              ),
            }}
          >
            <Tab.Screen
              name="Home"
              options={{ title: "Home" }}
            >
              {(props) => (
                <HomeScreen
                  {...props}
                  activeDate={activeDate}
                  offlineMode={offlineMode}
                  fontFamily={textFontStyle.fontFamily}
                />
              )}
            </Tab.Screen>
            <Tab.Screen
              name="Readings"
              options={{ title: "Readings" }}
            >
              {(props) => (
                <ReadingsScreen
                  {...props}
                  activeDate={activeDate}
                  offlineMode={offlineMode}
                  fontFamily={textFontStyle.fontFamily}
                />
              )}
            </Tab.Screen>
            <Tab.Screen
              name="Prayers"
              options={{ title: "Prayers" }}
            >
              {(props) => <PrayersScreen {...props} activeDate={activeDate} fontFamily={textFontStyle.fontFamily} />}
            </Tab.Screen>
            <Tab.Screen
              name="Donation"
              options={{ title: "Donate" }}
            >
              {(props) => <DonationScreen {...props} fontFamily={textFontStyle.fontFamily} />}
            </Tab.Screen>
          </Tab.Navigator>
          <View pointerEvents="none" style={styles.copyrightContainer}>
            <Text style={styles.copyrightText}>Copyright 2026 cmbryan software</Text>
          </View>
          {Platform.OS !== "web" && showPicker ? (
            <DateTimePicker
              mode="date"
              value={activeDate}
              display={Platform.OS === "ios" ? "inline" : "default"}
              onChange={onNativeDateChange}
            />
          ) : null}

          <Modal
            animationType="fade"
            visible={showSettingsMenu}
            transparent
            onRequestClose={() => setShowSettingsMenu(false)}
          >
            <Pressable
              style={styles.settingsBackdrop}
              onPress={() => setShowSettingsMenu(false)}
              accessibilityRole="button"
              accessibilityLabel="Close settings"
            >
              <View style={styles.settingsCardWrapper}>
              <Pressable style={styles.settingsCard} onPress={() => {}}>
                <Text style={[styles.settingsTitle, textFontStyle]}>Settings</Text>

                <Text style={[styles.settingsSectionLabel, textFontStyle]}>Font</Text>
                {APP_FONT_OPTIONS.map((font) => {
                  const selected = font.id === selectedFont;
                  return (
                    <Pressable
                      key={font.id}
                      style={styles.settingsOption}
                      onPress={() => onSelectFont(font.id)}
                      accessibilityRole="radio"
                      accessibilityState={{ checked: selected }}
                      accessibilityLabel={`Select ${font.label}`}
                    >
                      <View style={styles.settingsOptionRow}>
                        <View style={styles.radioOuter}>
                          {selected && <View style={styles.radioInner} />}
                        </View>
                        <Text style={[styles.settingsOptionText, textFontStyle]}>{font.label}</Text>
                      </View>
                    </Pressable>
                  );
                })}

                {Platform.OS !== "web" ? (
                  <>
                    <Text style={[styles.settingsSectionLabel, textFontStyle]}>Offline</Text>
                    <View style={styles.settingsOption}>
                      <View style={styles.settingsOptionRow}>
                        <Switch
                          value={offlineMode}
                          onValueChange={onToggleOfflineMode}
                          disabled={cacheInProgress}
                          accessibilityLabel="Toggle Offline mode"
                        />
                        <Text style={[styles.settingsOptionText, textFontStyle]}>Offline mode</Text>
                      </View>
                    </View>
                    {cacheInProgress ? (
                      <Text style={[styles.settingsHint, textFontStyle]}>
                        Caching next 30 days in the background...
                      </Text>
                    ) : null}
                  </>
                ) : null}
              </Pressable>
              </View>
            </Pressable>
          </Modal>
        </View>
      </View>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  headerLeftImage: {
    width: 32,
    height: 32,
    marginLeft: 8,
  },
  headerDatePickerRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingRight: 12,
    gap: 8,
  },
  buttonPrimary: {
    backgroundColor: "#1d4ed8",
    height: 36,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 12,
    marginRight: 8,
  },
  buttonPrimaryText: {
    color: "#ffffff",
    fontWeight: "600",
    fontSize: 14,
  },
  headerDateLabel: {
    color: "#111827",
    fontSize: 15,
    fontWeight: "600",
  },
  settingsButton: {
    width: 36,
    height: 36,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#d1d5db",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#ffffff",
  },
  settingsButtonText: {
    color: "#111827",
    fontSize: 18,
    fontWeight: "700",
    marginTop: -2,
  },
  appContainer: {
    flex: 1,
    backgroundColor: "#f3f4f6",
  },
  appLayout: {
    flex: 1,
    width: "100%",
    maxWidth: 960,
    alignSelf: "center",
  },
  copyrightContainer: {
    position: "absolute",
    left: 0,
    right: 0,
    bottom: 54,
    alignItems: "center",
  },
  copyrightText: {
    color: "#6b7280",
    fontSize: 12,
  },
  settingsBackdrop: {
    flex: 1,
    backgroundColor: "rgba(17, 24, 39, 0.4)",
    justifyContent: "flex-start",
    paddingTop: 84,
  },
  settingsCardWrapper: {
    width: "100%",
    maxWidth: 960,
    alignSelf: "center",
    alignItems: "flex-end",
    paddingRight: 12,
  },
  settingsCard: {
    width: 280,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#d1d5db",
    backgroundColor: "#ffffff",
    padding: 14,
    gap: 8,
  },
  settingsTitle: {
    color: "#111827",
    fontSize: 18,
    fontWeight: "700",
  },
  settingsSectionLabel: {
    marginTop: 6,
    color: "#374151",
    fontSize: 14,
    fontWeight: "700",
  },
  settingsOption: {
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 10,
    backgroundColor: "#f9fafb",
  },
  settingsOptionRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  radioOuter: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: "#1d4ed8",
    alignItems: "center",
    justifyContent: "center",
  },
  radioInner: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: "#1d4ed8",
  },
  settingsOptionText: {
    color: "#111827",
    fontSize: 15,
    lineHeight: 20,
  },
  settingsHint: {
    color: "#6b7280",
    fontSize: 13,
    lineHeight: 18,
  },
});
