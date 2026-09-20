# CyberShield Android Message + Call Sensor

This is the Android companion app for the CyberShield web/FastAPI project.

## What it does

### Message sensor
Uses Android `NotificationListenerService` to read posted notifications after the user explicitly enables Notification Access. It extracts notification title/text, sends the content to:

`POST /api/analyze`

When the backend returns `HIGH` or `CRITICAL`, CyberShield shows an Android security notification.

### Call sensor
Uses Android `CallScreeningService`. The user must choose CyberShield as the call-screening app. The service immediately tells Android to allow the call, then analyzes the caller asynchronously and shows a safety alert.

This version does NOT automatically block calls.

## Android Studio

1. Open this folder in Android Studio.
2. Let Gradle sync.
3. Connect an Android phone or start an emulator.
4. Run the `app` configuration.

## Backend URL

Default:

`http://10.0.2.2:8000`

That address works for an Android emulator when FastAPI is running on the development computer.

For a physical phone on the same Wi-Fi network, use the computer's LAN address, for example:

`http://192.168.1.25:8000`

The FastAPI server must listen on the LAN interface, for example:

`uvicorn app:app --reload --host 0.0.0.0 --port 8000`

For production, use HTTPS rather than cleartext HTTP.

## Enable sensors

Inside the app:

1. Save the backend URL.
2. Tap **ENABLE MESSAGE SENSOR**.
3. Enable CyberShield under Android Notification Access.
4. Tap **ENABLE CALL SENSOR**.
5. Approve CyberShield as the Call Screening app.
6. Tap **SEND TEST ALERT** to verify notifications.

## Privacy

Notification access is powerful: Android allows the app to receive notification content. The app should be presented to users with clear disclosure and should only process data needed for threat detection.

The call screening API is designed to screen calls before they are shown/rung. Android requires a response within a short timeout, so CyberShield responds immediately and performs network analysis afterward.

## Important limitation

A website running in a normal browser cannot directly read another app's SMS/WhatsApp notifications or phone calls. This Android companion app provides the OS-level sensor layer needed for that use case.
