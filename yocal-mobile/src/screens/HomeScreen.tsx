import { type ReactNode } from "react";
import {
  ActivityIndicator,
  Image,
  RefreshControl,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { formatDateKey, joinList } from "../lib/date";

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

interface HomeScreenProps {
  activeDate: Date;
  offlineMode?: boolean;
  fontFamily?: string;
}

export default function HomeScreen({ activeDate, offlineMode = false, fontFamily }: HomeScreenProps) {
  const activeDateKey = formatDateKey(activeDate);
  const { data, loading, refreshing, error, reload } = useDailyData(activeDateKey, offlineMode);
  const textFontStyle = fontFamily ? { fontFamily } : null;

  const dayTitle = data
    ? `${data.day_name} ${data.day_ord} ${data.month} ${data.year}`
    : activeDateKey;

  const details = data
    ? joinList([data.fast, data.tone && data.eothinon ? `${data.tone} - ${data.eothinon}` : data.tone, data.liturgy])
    : [];

  const commemoration = data
    ? joinList([data.desig, data.commem, data.fore_after])
    : [];

  const saints = data
    ? joinList([
        data.global_saints,
        data.british_saints ? `British Isles and Ireland:\n${data.british_saints}` : "",
      ])
    : [];

  const allCommemorations = joinList([...commemoration, ...saints]);

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => void reload(true)} />
        }
      >
        <SectionCard title={dayTitle} textStyle={textFontStyle}>
          {loading ? (
            <ActivityIndicator />
          ) : error ? (
            <Text style={[styles.errorText, textFontStyle]}>{error}</Text>
          ) : (
            <>
              {details.map((line) => (
                <Text key={line} style={[styles.lineItem, textFontStyle]}>
                  {line}
                </Text>
              ))}
            </>
          )}
        </SectionCard>

        {!loading && !error && (
          <SectionCard title="Designations and Commemorations" textStyle={textFontStyle}>
            {allCommemorations.map((line) => (
              <Text key={line} style={[styles.lineItem, textFontStyle]}>
                {line}
              </Text>
            ))}
          </SectionCard>
        )}
        <View style={styles.imageContainer}>
          <Image
            source={require("../../assets/antioch_uk.png")}
            style={styles.bottomImage}
          />
        </View>
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
  errorText: {
    color: "#b91c1c",
    fontSize: 15,
    lineHeight: 22,
  },
  imageContainer: {
    alignItems: "center",
    paddingVertical: 24,
  },
  bottomImage: {
    width: 140,
    height: 140,
    resizeMode: "contain",
  },
});