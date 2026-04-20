import { useMemo, useState } from "react";
import {
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import {
  EVENING_PRAYER_SOURCE_URL,
  EVENING_PRAYER_TEXT,
  getMorningPrayerTextForDate,
  MORNING_PRAYER_SOURCE_URL,
} from "../lib/prayers";
import {
  getTypikaSections,
  TYPIKA_SOURCE_URL,
} from "../lib/typika";

interface PrayersScreenProps {
  activeDate: Date;
  fontFamily?: string;
  navigation?: {
    navigate?: (screen: string, params?: { selectedTab?: "home" | "liturgy" }) => void;
  };
}

type PrayerSection = {
  key: "morning" | "evening" | "typika";
  title: string;
  open: boolean;
  text: string;
  onToggle: () => void;
  sourceUrl: string;
  beforeReadings?: string;
  afterReadings?: string;
};

export default function PrayersScreen({ activeDate, fontFamily, navigation }: PrayersScreenProps) {
  const [showMorning, setShowMorning] = useState(false);
  const [showEvening, setShowEvening] = useState(false);
  const isSunday = activeDate.getDay() === 0;
  const textFontStyle = fontFamily ? { fontFamily } : null;

  const morningPrayerText = useMemo(() => getMorningPrayerTextForDate(activeDate), [activeDate]);
  const typikaSections = useMemo(() => getTypikaSections(), []);

  const openLiturgyReadings = () => {
    navigation?.navigate?.("Readings", { selectedTab: "liturgy" });
  };

  const sections: PrayerSection[] = useMemo(
    () => [
      {
        key: isSunday ? "typika" : "morning",
        title: isSunday ? "Typika" : "Morning Prayer",
        open: showMorning,
        text: isSunday ? "" : morningPrayerText,
        beforeReadings: isSunday ? typikaSections.beforeReadings : "",
        afterReadings: isSunday ? typikaSections.afterReadings : "",
        onToggle: () => setShowMorning((prev) => !prev),
        sourceUrl: isSunday ? TYPIKA_SOURCE_URL : MORNING_PRAYER_SOURCE_URL,
      },
      {
        key: "evening",
        title: "Evening Prayer",
        open: showEvening,
        text: EVENING_PRAYER_TEXT,
        onToggle: () => setShowEvening((prev) => !prev),
        sourceUrl: EVENING_PRAYER_SOURCE_URL,
      },
    ],
    [isSunday, morningPrayerText, showMorning, showEvening, typikaSections],
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
        {sections.map((section) => (
          <View key={section.key} style={styles.sectionCard}>
            <Pressable onPress={section.onToggle} style={styles.sectionHeader}>
              <Text style={[styles.sectionTitle, textFontStyle]}>{section.title}</Text>
              <Text style={[styles.chevron, textFontStyle]}>{section.open ? "Hide" : "Show"}</Text>
            </Pressable>

            {section.open && section.key === "typika" ? (
              <>
                <Text style={[styles.sectionBody, textFontStyle]}>{section.beforeReadings}</Text>
                <Pressable onPress={openLiturgyReadings}>
                  <Text style={[styles.linkText, textFontStyle]}>Readings</Text>
                </Pressable>
                <Text style={[styles.sectionBody, textFontStyle]}>{section.afterReadings}</Text>
                <Text style={[styles.sourceText, textFontStyle]}>Source: {section.sourceUrl}</Text>
              </>
            ) : section.open && section.text.length > 0 ? (
              <>
                <Text style={[styles.sectionBody, textFontStyle]}>{section.text}</Text>
                <Text style={[styles.sourceText, textFontStyle]}>Source: {section.sourceUrl}</Text>
              </>
            ) : null}
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#f3f4f6",
  },
  scroll: {
    flex: 1,
  },
  content: {
    padding: 16,
    gap: 12,
    paddingBottom: 42,
  },
  sectionCard: {
    backgroundColor: "#ffffff",
    borderRadius: 10,
    borderColor: "#e5e7eb",
    borderWidth: 1,
    padding: 14,
    gap: 10,
  },
  sectionHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#111827",
  },
  chevron: {
    fontSize: 14,
    fontWeight: "600",
    color: "#1d4ed8",
  },
  sectionBody: {
    color: "#1f2937",
    fontSize: 15,
    lineHeight: 22,
  },
  sourceText: {
    color: "#6b7280",
    fontSize: 12,
  },
  linkText: {
    color: "#1d4ed8",
    textDecorationLine: "underline",
    fontSize: 15,
    lineHeight: 22,
    fontWeight: "600",
  },
});
