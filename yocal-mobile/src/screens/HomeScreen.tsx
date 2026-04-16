import { type ReactNode, useCallback, useEffect, useState } from "react";
import DateTimePicker, {
  type DateTimePickerEvent,
} from "@react-native-community/datetimepicker";
import {
  ActivityIndicator,
  Platform,
  Pressable,
  RefreshControl,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { fetchDailyData, type DatePayload } from "../lib/api";
import { formatDateKey, htmlToText, joinList, parseDateFromKey } from "../lib/date";

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

interface HomeScreenProps {
  activeDate: Date;
  setActiveDate: (date: Date) => void;
}

export default function HomeScreen({ activeDate, setActiveDate }: HomeScreenProps) {
  const [showPicker, setShowPicker] = useState(false);
  const activeDateKey = formatDateKey(activeDate);
  const { data, loading, refreshing, error, reload } = useDailyData(activeDateKey);

  const dayTitle = data
    ? `${data.day_name} ${data.day_ord} ${data.month} ${data.year}`
    : activeDateKey;

  const details = data
    ? joinList([data.fast, data.tone && data.eothinon ? `${data.tone} - ${data.eothinon}` : data.tone, data.liturgy])
    : [];

  const commemoration = data
    ? joinList([data.desig, data.commem, data.fore_after])
    : [];

  const onNativeDateChange = (event: DateTimePickerEvent, selectedDate?: Date) => {
    if (Platform.OS === "android") {
      setShowPicker(false);
    }
    if (event.type === "dismissed" || !selectedDate) {
      return;
    }
    setActiveDate(selectedDate);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => void reload(true)} />
        }
      >
        <Text style={styles.header}>Home</Text>

        {Platform.OS === "web" ? (
          <View style={styles.datePickerRow}>
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
          </View>
        ) : (
          <View style={styles.datePickerRow}>
            <Pressable style={styles.buttonPrimary} onPress={() => setShowPicker(true)}>
              <Text style={styles.buttonPrimaryText}>Select Date</Text>
            </Pressable>
            <Text style={styles.dateLabel}>{activeDateKey}</Text>
          </View>
        )}
        {Platform.OS !== "web" && showPicker ? (
          <DateTimePicker
            mode="date"
            value={activeDate}
            display={Platform.OS === "ios" ? "inline" : "default"}
            onChange={onNativeDateChange}
          />
        ) : null}

        <SectionCard title={dayTitle}>
          {loading ? (
            <ActivityIndicator />
          ) : error ? (
            <Text style={styles.errorText}>{error}</Text>
          ) : (
            <>
              {details.map((line) => (
                <Text key={line} style={styles.lineItem}>
                  {line}
                </Text>
              ))}
            </>
          )}
        </SectionCard>

        {!loading && !error && (
          <SectionCard title="Designations and Commemorations">
            {commemoration.map((line) => (
              <Text key={line} style={styles.lineItem}>
                {line}
              </Text>
            ))}
          </SectionCard>
        )}
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
  datePickerRow: {
    flexDirection: "row",
    gap: 8,
    alignItems: "center",
  },
  webDatePicker: {
    height: 44,
    borderWidth: 1,
    borderColor: "#d1d5db",
    borderRadius: 8,
    paddingLeft: 12,
    paddingRight: 12,
    fontSize: 16,
    backgroundColor: "#ffffff",
    color: "#111827",
    minWidth: 220,
  },
  buttonPrimary: {
    backgroundColor: "#1d4ed8",
    height: 44,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 16,
  },
  buttonPrimaryText: {
    color: "#ffffff",
    fontWeight: "600",
  },
  dateLabel: {
    color: "#111827",
    fontSize: 15,
    fontWeight: "600",
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
});