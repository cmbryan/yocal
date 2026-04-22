import { type ReactElement, useMemo, useState } from "react";
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

type PrayerBlock = {
  key: string;
  text: string;
  style: "body" | "heading" | "subheading" | "italic";
};

function parsePrayerBlocks(rawText: string): PrayerBlock[] {
  const paragraphs = rawText
    .split(/\n\s*\n/)
    .map((part) => part.trim())
    .filter((part) => part.length > 0);

  return paragraphs.map((paragraph, index) => {
    if (paragraph.startsWith("## ")) {
      return { key: `p-${index}`, text: paragraph.slice(3).trim(), style: "heading" };
    }

    if (paragraph.startsWith("### ")) {
      return { key: `p-${index}`, text: paragraph.slice(4).trim(), style: "subheading" };
    }

    if (paragraph.startsWith("_") && paragraph.endsWith("_")) {
      return {
        key: `p-${index}`,
        text: paragraph.slice(1, paragraph.length - 1).trim(),
        style: "italic",
      };
    }

    return { key: `p-${index}`, text: paragraph, style: "body" };
  });
}

function renderPrayerBlocks(
  blocks: PrayerBlock[],
  textFontStyle: { fontFamily?: string } | null,
): ReactElement[] {
  return blocks.map((block) => {
    if (block.style === "heading") {
      return (
        <Text key={block.key} style={[styles.prayerHeading, textFontStyle]}>
          {block.text}
        </Text>
      );
    }

    if (block.style === "subheading") {
      return (
        <Text key={block.key} style={[styles.prayerSubheading, textFontStyle]}>
          {block.text}
        </Text>
      );
    }

    if (block.style === "italic") {
      return (
        <Text key={block.key} style={[styles.sectionBody, styles.italicIntro, textFontStyle]}>
          {block.text}
        </Text>
      );
    }

    return (
      <Text key={block.key} style={[styles.sectionBody, textFontStyle]}>
        {block.text}
      </Text>
    );
  });
}

export default function PrayersScreen({ activeDate, fontFamily, navigation }: PrayersScreenProps) {
  const [showMorning, setShowMorning] = useState(false);
  const [showEvening, setShowEvening] = useState(false);
  const isSunday = activeDate.getDay() === 0;
  const textFontStyle = fontFamily ? { fontFamily } : null;

  const morningPrayerText = useMemo(() => getMorningPrayerTextForDate(activeDate), [activeDate]);
  const morningPrayerBlocks = useMemo(() => parsePrayerBlocks(morningPrayerText), [morningPrayerText]);
  const eveningPrayerBlocks = useMemo(() => parsePrayerBlocks(EVENING_PRAYER_TEXT), []);
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
            ) : section.open && section.key === "morning" ? (
              <>
                {renderPrayerBlocks(morningPrayerBlocks, textFontStyle)}
                <Text style={[styles.sourceText, textFontStyle]}>Source: {section.sourceUrl}</Text>
              </>
            ) : section.open && section.key === "evening" ? (
              <>
                {renderPrayerBlocks(eveningPrayerBlocks, textFontStyle)}
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
  prayerHeading: {
    color: "#111827",
    fontSize: 17,
    lineHeight: 24,
    fontWeight: "700",
    marginTop: 4,
  },
  prayerSubheading: {
    color: "#1f2937",
    fontSize: 16,
    lineHeight: 23,
    fontWeight: "600",
    marginTop: 2,
  },
  italicIntro: {
    fontStyle: "italic",
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
