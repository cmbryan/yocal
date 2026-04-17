import { StatusBar } from "expo-status-bar";
import { useState } from "react";
import { Platform, Pressable, StyleSheet, Text, View } from "react-native";
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import DateTimePicker, { type DateTimePickerEvent } from "@react-native-community/datetimepicker";
import HomeScreen from "./src/screens/HomeScreen";
import CommemorateScreen from "./src/screens/CommemorateScreen";
import ReadingsScreen from "./src/screens/ReadingsScreen";
import DonationScreen from "./src/screens/DonationScreen";
import { formatDateKey, parseDateFromKey } from "./src/lib/date";

const Tab = createBottomTabNavigator();

export default function App() {
  const [activeDate, setActiveDate] = useState(() => new Date());
  const [showPicker, setShowPicker] = useState(false);
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

  return (
    <NavigationContainer>
      <StatusBar style="dark" />
      <Tab.Navigator
        screenOptions={{
          tabBarActiveTintColor: "#1d4ed8",
          tabBarInactiveTintColor: "#6b7280",
          tabBarStyle: {
            backgroundColor: "#ffffff",
            borderTopColor: "#e5e7eb",
            borderTopWidth: 1,
          },
          headerStyle: {
            backgroundColor: "#f3f4f6",
          },
          headerTintColor: "#111827",
          headerTitleStyle: {
            fontWeight: "bold",
          },
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
                  style={styles.webDatePicker as unknown as Record<string, string | number>}
                />
              ) : (
                <>
                  <Pressable
                    style={styles.buttonPrimary}
                    onPress={() => setShowPicker(true)}
                  >
                    <Text style={styles.buttonPrimaryText}>Select Date</Text>
                  </Pressable>
                  <Text style={styles.headerDateLabel}>{activeDateKey}</Text>
                </>
              )}
            </View>
          ),
        }}
      >
        <Tab.Screen
          name="Home"
          options={{ title: "Home" }}
        >
          {(props) => <HomeScreen {...props} activeDate={activeDate} setActiveDate={setActiveDate} />}
        </Tab.Screen>
        <Tab.Screen
          name="Commemorate"
          options={{ title: "Commemorations" }}
        >
          {(props) => <CommemorateScreen {...props} activeDate={activeDate} />}
        </Tab.Screen>
        <Tab.Screen
          name="Readings"
          options={{ title: "Readings" }}
        >
          {(props) => <ReadingsScreen {...props} activeDate={activeDate} />}
        </Tab.Screen>
        <Tab.Screen
          name="Donation"
          options={{ title: "Donate" }}
        >
          {(props) => <DonationScreen {...props} />}
        </Tab.Screen>
      </Tab.Navigator>
        {Platform.OS !== "web" && showPicker ? (
          <DateTimePicker
            mode="date"
            value={activeDate}
            display={Platform.OS === "ios" ? "inline" : "default"}
            onChange={onNativeDateChange}
          />
        ) : null}
      </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  headerDatePickerRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingRight: 12,
  },
  webDatePicker: {
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
});
