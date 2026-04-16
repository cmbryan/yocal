import { StatusBar } from "expo-status-bar";
import { useState } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import HomeScreen from "./src/screens/HomeScreen";
import CommemorateScreen from "./src/screens/CommemorateScreen";
import ReadingsScreen from "./src/screens/ReadingsScreen";

const Tab = createBottomTabNavigator();

export default function App() {
  const [activeDate, setActiveDate] = useState(() => new Date());

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
      </Tab.Navigator>
    </NavigationContainer>
  );
}
