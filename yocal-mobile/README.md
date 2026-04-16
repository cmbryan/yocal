# YOCal Mobile App (Expo)

Cross-platform Saints and Readings app built with Expo React Native.

## Platforms

- Android
- iOS
- Web

## Data Source

- Live API: `https://yorkorthodox.org/api-php`
- Date endpoint: `https://yorkorthodox.org/api-php/date?year=YYYY&month=M&day=D`

## Features

- Displays daily Saints and Readings data from YOCal.
- Select date with:
  - Previous / Today / Next quick navigation
  - Direct date input (`YYYY-MM-DD`)
- Pull-to-refresh support.
- Structured sections for:
  - Day header and liturgical details
  - Designations and commemorations
  - Saints (global + British/Irish)
  - Reading references (including commemoration readings)
  - Full reading texts
- Handles API errors and invalid date entry.

## Run

From the `yocal-mobile` folder:

```bash
npm install
npm run start
```

Then choose:

- `a` for Android
- `i` for iOS
- `w` for Web

## Building for Production

Use EAS Build to create signed Android App Bundles (AAB) for Google Play Store submission.

### Local Build

Build locally on your machine:

```bash
npx eas-cli build --platform android --local
```

This creates a signed AAB in the `dist` folder.

### Remote Build

Build in the cloud (recommended for consistency):

```bash
npx eas-cli build --platform android
```

The build will be uploaded to EAS servers and you'll receive a download link when complete.

## Automated Regression Tests

Run:

```bash
npm run typecheck
npm run test:ci
```

Coverage is generated automatically by `test:ci`.
