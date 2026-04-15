import { StatusBar } from "expo-status-bar";
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
import { fetchDailyData, type DatePayload } from "./src/lib/api";
import { formatDateKey, htmlToText, joinList, parseDateFromKey } from "./src/lib/date";

function useDailyData(dateKey: string) {
  const [data, setData] = useState<DatePayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(
    async (isRefresh = false) => {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);
      try {
        const payload = await fetchDailyData(dateKey);
        setData(payload);
      } catch (err) {
        const rawMessage =
          err instanceof Error ? err.message : "Unexpected error.";
        const message =
          rawMessage === "Failed to fetch"
            ? "Failed to fetch data from the API. If you are on web, this is usually a CORS issue until the API deploy includes CORS headers."
            : rawMessage;
        setError(message);
        setData(null);
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [dateKey]
  );

  useEffect(() => {
    void load();
  }, [load]);

  return { data, loading, refreshing, error, reload: load };
}

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

export default function App() {
  const [activeDate, setActiveDate] = useState(() => new Date());
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

  const saints = data
    ? joinList([
        data.global_saints,
        data.british_saints ? `British Isles and Ireland:\n${data.british_saints}` : "",
      ])
    : [];

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
      <StatusBar style="dark" />
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => void reload(true)} />
        }
      >
        <Text style={styles.header}>Saints and Readings</Text>
        <Text style={styles.subheader}>YOCal Daily Viewer (Android, iOS, Web)</Text>

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
          <>
            <SectionCard title="Designations and Commemorations">
              {commemoration.map((line) => (
                <Text key={line} style={styles.lineItem}>
                  {line}
                </Text>
              ))}
            </SectionCard>

            <SectionCard title="Today We Commemorate">
              {saints.map((line) => (
                <Text key={line} style={styles.multiLineItem}>
                  {line}
                </Text>
              ))}
            </SectionCard>

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
  subheader: {
    fontSize: 14,
    color: "#4b5563",
    marginBottom: 8,
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
  multiLineItem: {
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
