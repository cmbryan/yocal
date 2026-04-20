import { type ReactNode, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  RefreshControl,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { formatDateKey, htmlToText } from "../lib/date";

import { useDailyData } from "../lib/hooks";

function SectionCard({
  title,
  children,
  textStyle,
}: {
  title: string;
  children: ReactNode;
  textStyle?: { fontFamily?: string } | null;
}) {
  return (
    <View style={styles.card}>
      <Text style={[styles.cardTitle, textStyle]}>{title}</Text>
      {children}
    </View>
  );
}

function subtractRefs(readings: string[], toRemove: string[]): string[] {
  return readings.filter((reading) => !toRemove.includes(reading));
}

function intersectRefs(readings: string[], source: string[]): string[] {
  return readings.filter((reading) => source.includes(reading));
}

interface ReadingsScreenProps {
  activeDate: Date;
  offlineMode?: boolean;
  fontFamily?: string;
  route?: {
    params?: {
      selectedTab?: ReadingTab;
    };
  };
  navigation?: {
    setParams?: (params: { selectedTab?: ReadingTab }) => void;
  };
}

type ReadingTab = "home" | "liturgy";

export default function ReadingsScreen({ activeDate, offlineMode = false, fontFamily, route, navigation }: ReadingsScreenProps) {
  const [selectedTab, setSelectedTab] = useState<ReadingTab>("home");
  const requestedTab = route?.params?.selectedTab;

  useEffect(() => {
    if (requestedTab === "home" || requestedTab === "liturgy") {
      setSelectedTab(requestedTab);
      navigation?.setParams?.({ selectedTab: undefined });
    }
  }, [requestedTab, navigation]);

  const activeDateKey = formatDateKey(activeDate);
  const { data, loading, refreshing, error, reload } = useDailyData(activeDateKey, offlineMode);
  const textFontStyle = fontFamily ? { fontFamily } : null;

  const basicLections = data ? data.lections.basic : [];
  const commemLections = data ? data.lections.commem : [];
  const liturgyLections = data ? data.lections.liturgy : [];

  const homeBasicRefs = commemLections.length === 0
    ? basicLections
    : subtractRefs(basicLections, liturgyLections);
  const homeCommemRefs = subtractRefs(commemLections, liturgyLections);

  const liturgyBasicRefs = intersectRefs(liturgyLections, basicLections);
  const liturgyCommemRefs = intersectRefs(liturgyLections, commemLections);

  const homeReadingRefs = [
    ...homeBasicRefs,
    ...(homeCommemRefs.length > 0 ? ["For the Commemoration:", ...homeCommemRefs] : []),
  ];

  const liturgyReadingRefs = [
    ...liturgyBasicRefs,
    ...(liturgyCommemRefs.length > 0 ? ["For the Commemoration:", ...liturgyCommemRefs] : []),
  ];

  const readingRefs = selectedTab === "liturgy" ? liturgyReadingRefs : homeReadingRefs;

  const homeTexts = data ? [
    ...data.texts.basic.filter((_, i) => homeBasicRefs.includes(data.lections.basic[i])),
    ...data.texts.commem.filter((_, i) => homeCommemRefs.includes(data.lections.commem[i])),
  ].map((item) => htmlToText(item)) : [];

  const liturgyTexts = data ? [
    ...data.texts.basic.filter((_, i) => liturgyBasicRefs.includes(data.lections.basic[i])),
    ...data.texts.commem.filter((_, i) => liturgyCommemRefs.includes(data.lections.commem[i])),
  ].map((item) => htmlToText(item)) : [];

  const readingTexts = selectedTab === "liturgy" ? liturgyTexts : homeTexts;

  const readingsTitle = selectedTab === "liturgy" ? "At Church" : "At Home";

  const noLiturgy = selectedTab === "liturgy" && data && !data.liturgy;

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => void reload(true)} />
        }
      >
        {!loading && !error && (
          <>
            <View style={styles.tabRow}>
              <Pressable
                style={[
                  styles.tab,
                  selectedTab === "home" && styles.tabActive,
                ]}
                onPress={() => setSelectedTab("home")}
              >
                <Text
                  style={[
                    styles.tabText,
                    textFontStyle,
                    selectedTab === "home" && styles.tabTextActive,
                  ]}
                >
                  At Home
                </Text>
              </Pressable>
              <Pressable
                style={[
                  styles.tab,
                  selectedTab === "liturgy" && styles.tabActive,
                ]}
                onPress={() => setSelectedTab("liturgy")}
              >
                <Text
                  style={[
                    styles.tabText,
                    textFontStyle,
                    selectedTab === "liturgy" && styles.tabTextActive,
                  ]}
                >
                  At Church
                </Text>
              </Pressable>
            </View>

            <SectionCard title={readingsTitle} textStyle={textFontStyle}>
              {noLiturgy ? (
                <Text style={[styles.italicText, textFontStyle]} accessible={true}>There is no liturgy on this day.</Text>
              ) : (
                readingRefs.map((reading) => (
                  <Text key={reading} style={[styles.lineItem, textFontStyle]} accessible={true}>
                    {reading}
                  </Text>
                ))
              )}
            </SectionCard>

            {!noLiturgy && (
              <SectionCard title="Texts" textStyle={textFontStyle}>
                {readingTexts.map((text, idx) => (
                  <Text key={`${idx}-${text.slice(0, 32)}`} style={[styles.readingText, textFontStyle]} accessible={true}>
                    {text}
                  </Text>
                ))}
              </SectionCard>
            )}
          </>
        )}
        {loading && <ActivityIndicator />}
        {error && <Text style={[styles.errorText, textFontStyle]}>{error}</Text>}
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
  header: {
    fontSize: 28,
    fontWeight: "700",
    color: "#111827",
  },
  card: {
    backgroundColor: "#ffffff",
    borderRadius: 10,
    borderColor: "#e5e7eb",
    borderWidth: 1,
    padding: 14,
    gap: 8,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#111827",
  },
  lineItem: {
    color: "#1f2937",
    fontSize: 15,
    lineHeight: 22,
  },
  noteText: {
    marginTop: 4,
    color: "#374151",
    fontSize: 13,
    fontStyle: "italic",
  },
  readingText: {
    color: "#111827",
    fontSize: 15,
    lineHeight: 24,
    marginBottom: 10,
  },
  tabRow: {
    flexDirection: "row",
    gap: 8,
    marginBottom: 6,
  },
  tab: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#d1d5db",
    backgroundColor: "#f9fafb",
    alignItems: "center",
    justifyContent: "center",
  },
  tabActive: {
    backgroundColor: "#1d4ed8",
    borderColor: "#1d4ed8",
  },
  tabText: {
    color: "#374151",
    fontSize: 15,
    fontWeight: "600",
  },
  tabTextActive: {
    color: "#ffffff",
  },
  errorText: {
    color: "#b91c1c",
    fontSize: 15,
    lineHeight: 22,
  },
  italicText: {
    fontStyle: "italic",
    color: "#374151",
    fontSize: 15,
    lineHeight: 22,
  },
});