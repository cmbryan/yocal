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
import { formatDateKey, htmlToText } from "../lib/date";

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

interface ReadingsScreenProps {
  activeDate: Date;
}

export default function ReadingsScreen({ activeDate }: ReadingsScreenProps) {
  const activeDateKey = formatDateKey(activeDate);
  const { data, loading, refreshing, error, reload } = useDailyData(activeDateKey);

  const readingRefs = data
    ? [
        ...data.lections.basic,
        ...(data.lections.commem.length > 0
          ? ["For the Commemoration:", ...data.lections.commem]
          : []),
      ]
    : [];

  const readingTexts = data
    ? [...data.texts.basic, ...data.texts.commem].map((item) => htmlToText(item))
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
        <Text style={styles.header}>Readings</Text>

        {!loading && !error && (
          <>
            <SectionCard title="Today's Readings">
              {readingRefs.map((reading) => (
                <Text key={reading} style={styles.lineItem}>
                  {reading}
                </Text>
              ))}
              {data && data.lections.liturgy.length > 0 ? (
                <Text style={styles.noteText}>
                  Readings for the Liturgy: {data.lections.liturgy.join("; ")}
                </Text>
              ) : null}
            </SectionCard>

            <SectionCard title="Reading Texts">
              {readingTexts.map((text, idx) => (
                <Text key={`${idx}-${text.slice(0, 32)}`} style={styles.readingText}>
                  {text}
                </Text>
              ))}
            </SectionCard>
          </>
        )}
        {loading && <ActivityIndicator />}
        {error && <Text style={styles.errorText}>{error}</Text>}
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
  errorText: {
    color: "#b91c1c",
    fontSize: 15,
    lineHeight: 22,
  },
});