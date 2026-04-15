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

## Automated Regression Tests

Run:

```bash
npm run typecheck
npm run test:ci
```

Coverage is generated automatically by `test:ci`.
