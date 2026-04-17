import { type ReactNode } from "react";
import { Image, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from "react-native";
import * as WebBrowser from "expo-web-browser";

const DONATION_URL = "https://pay.sumup.com/b2c/QLQWLULC";

function LinkText({ children, url }: { children: string; url: string }) {
  return (
    <Text style={styles.link} onPress={() => void WebBrowser.openBrowserAsync(url)}>
      {children}
    </Text>
  );
}

export default function DonationScreen(_props: any) {
  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>

        <View style={styles.firstParagraphRow}>
          <Text style={styles.firstParagraphText}>
            The Antiochian Orthodox Parish of St Constantine the Great, based in the city of York, has been serving the North of England since ____ through worship, fellowship, and evangelism. We are part of the
            {" "}
            <LinkText url="https://www.antiochian-orthodox.com/">Antiochian Orthodox Church in the UK</LinkText>, and you can find more about our parish at our
            {" "}
            <LinkText url="https://yorkorthodox.org">website</LinkText>.
            {"\n\n"}
            Thanks to God, and with your support, we hope to purchase our first building,
            {" "}
            <LinkText url="https://en.wikipedia.org/wiki/St_Martin-cum-Gregory%27s_Church,_Micklegate,_York">St Martin-cum-Gregory's</LinkText>, to expand our ministry to York and the surrounding area.
          </Text>
          <Image
            source={require("../../assets/antioch_uk.avif")}
            style={styles.firstParagraphImage}
          />
        </View>

        <Text style={styles.paragraph}>
          If you enjoy using this app, please consider making a donation to help us achieve this milestone!
        </Text>

        <View style={styles.buttonWrapper}>
          <Pressable style={styles.buttonPrimary} onPress={() => void WebBrowser.openBrowserAsync(DONATION_URL)}>
            <Text style={styles.buttonPrimaryText}>Donate</Text>
          </Pressable>
        </View>

        <Text style={styles.note}>
          <Text style={{ fontWeight: "600" }}>Troparion to St Constantine</Text>
          {"\n"}
          Constantine, who is Your apostle among kings, O Lord,{"\n"}
          Having beheld with his own eyes the sign of Your Cross in heaven,{"\n"}
          And, like Paul, having accepted Your call not from man,{"\n"}
          Entrusted the reigning city into Your hands,{"\n"}
          Having delivered it with safety for all time{"\n"}
          Through the intercessions of the Theotokos,{"\n"}
          O only lover of mankind.
        </Text>
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
    gap: 16,
    paddingBottom: 42,
  },
  header: {
    fontSize: 28,
    fontWeight: "700",
    color: "#111827",
  },
  paragraph: {
    fontSize: 16,
    lineHeight: 24,
    color: "#111827",
  },
  firstParagraphRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 12,
  },
  firstParagraphText: {
    flex: 1,
    flexShrink: 1,
    fontSize: 16,
    lineHeight: 24,
    color: "#111827",
  },
  firstParagraphImage: {
    width: 150,
    height: 150,
    resizeMode: "contain",
    marginTop: 4,
  },
  note: {
    fontSize: 16,
    lineHeight: 24,
    color: "#374151",
    fontStyle: "italic",
    textAlign: "center",
  },
  link: {
    color: "#1d4ed8",
    textDecorationLine: "underline",
  },
  buttonWrapper: {
    marginTop: 24,
    alignItems: "center",
  },
  buttonPrimary: {
    backgroundColor: "#1d4ed8",
    borderRadius: 8,
    paddingVertical: 14,
    paddingHorizontal: 24,
  },
  buttonPrimaryText: {
    color: "#ffffff",
    fontWeight: "600",
    fontSize: 16,
  },
});