import { type ReactNode, useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  RefreshControl,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { fetchDailyData, type DatePayload } from "../lib/api";
import { formatDateKey, joinList } from "../lib/date";

import { useDailyData } from "../lib/hooks";

function SectionCard({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>{title}</Text>
      {children}
    </View>
  );
}

interface CommemorateScreenProps {
  activeDate: Date;
}

export default function CommemorateScreen({ activeDate }: CommemorateScreenProps) {
  const activeDateKey = formatDateKey(activeDate);
  const { data, loading, refreshing, error, reload } = useDailyData(activeDateKey);

  const saints = data
    ? joinList([
        data.global_saints,
        data.british_saints ? `British Isles and Ireland:\n${data.british_saints}` : "",
      ])
    : [];

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => void reload(true)} />
        }
      >
        <Text style={styles.header}>Commemorations</Text>

        <SectionCard title="Today We Commemorate">
          {loading ? (
            <ActivityIndicator />
          ) : error ? (
            <Text style={styles.errorText}>{error}</Text>
          ) : (
            saints.map((line) => (
              <Text key={line} style={styles.multiLineItem}>
                {line}
              </Text>
            ))
          )}
        </SectionCard>
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
  multiLineItem: {
    color: "#1f2937",
    fontSize: 15,
    lineHeight: 22,
  },
  errorText: {
    color: "#b91c1c",
    fontSize: 15,
    lineHeight: 22,
  },
});