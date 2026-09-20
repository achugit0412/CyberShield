# 🛡️ CyberShield

**CyberShield is a defensive cybersecurity platform that helps users identify phishing, financial scams, malicious links, fake job offers, and social-engineering attacks.**

It combines a **web-based threat analyzer**, a **FastAPI backend**, and an **Android companion sensor** that can analyze suspicious notifications and provide security alerts.
It then provides clear guidance on what to do next and what actions to take if the user has already interacted with the threat. CyberShield also teaches users about the detected type of attack, how it works, and how to recognize similar threats in the future


## 🚨 Problem

Scam messages are becoming increasingly convincing. Students and everyday smartphone users may receive:

* Phishing messages
* Fake banking or payment requests
* OTP and credential-stealing attempts
* Malicious or suspicious links
* Fake job and recruitment offers
* Social-engineering messages
* Suspicious notifications

Users often do not know whether a message is dangerous or what they should do next.

## 💡 Solution

CyberShield provides a unified defense system that analyzes suspicious content and delivers simple, understandable security guidance—no prior cybersecurity knowledge required. Additionally it teaches basics of this attacking techniques to know what to do in this situation 

### 🔄 How the Ecosystem Works Together
The **Android Companion App** and the **Web Threat Analyzer** are built to complement each other, but they also function as completely independent tools:

* **Automated Detection:** The Android background sensor automatically scans incoming notifications and alerts the user in real-time if a threat is flagged.
* **Standalone Web Triage & Fallback:** Users can simply copy-paste text directly into the **Web Analyzer** without using or installing the Android app at all. This allows anyone (including mobile or desktop users) to quickly analyze suspicious text, know more about the threat, use deep triage, and access preventative playbooks.
* **Unified Engine:** Both components query the exact same FastAPI backend, ensuring identical rule-based triage, risk-scoring, and protective action playbooks regardless of how the user accesses the platform.

### 📊 Threat Analysis Outputs
For every message analyzed in Web platform, CyberShield dynamically generates:
* **Risk Evaluation:** Clear classification levels (LOW / MEDIUM / HIGH / CRITICAL) paired with a precise numerical Risk Score.
* **Threat Categorization:** Identification of the attack type (e.g., Phishing, OTP Stealing, Social Engineering).
* **Suspicious Indicators:** Breakdowns of specific red flags detected within the text (e.g., high urgency, financial baiting).
* **Actionable Guidance:** Recommended immediate steps to take, alongside proactive playbooks detailing what to do if the user has already interacted with the threat.

## ✨ Key Features

### 🌐 Web Threat Analyzer

Users can enter suspicious messages or URLs into the CyberShield website.

The system analyzes the content and identifies potential threats.

### 📱 Android Security Sensor

The Android companion application can monitor notifications after the user explicitly grants Notification Access.

When a suspicious notification is detected, CyberShield sends the content to the backend for analysis and can display a security alert for high-risk results.

### ☎️ Call Security Component

CyberShield includes an Android `CallScreeningService` component designed to analyze incoming caller information and provide a safety alert.

The application does not automatically block calls.

### 🧠 Threat Detection

CyberShield uses a defensive rule-based analysis engine to identify indicators such as:

* Credential or OTP requests
* Urgency
* Financial language
* Account verification requests
* Suspicious actions
* Potential social engineering

An optional local Ollama model can also be used for AI-assisted analysis.

### ☁️ AWS Deployment

The deployed system uses:

* **AWS EC2** — application hosting
* **Nginx** — website serving and API reverse proxy
* **FastAPI** — backend API
* **CloudWatch** — server monitoring
* **SNS** — monitoring alerts
* **S3** — project artifact storage

## 🏗️ Project Structure

```text
CyberShield/
│
├── android/
│   ├── app/
│   │   ├── src/
│   │   └── build.gradle.kts
│   ├── gradle/
│   ├── gradlew
│   ├── gradlew.bat
│   └── README.md
│
├── static/
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   └── sw.js
│
├── app.py
├── requirements.txt
├── Dockerfile.txt
├── .gitignore
└── README.md
```

## 🛠️ Technology Stack

### Backend

* Python
* FastAPI
* Uvicorn

### Frontend

* HTML
* CSS
* JavaScript

### Android

* Kotlin
* Android SDK
* NotificationListenerService
* CallScreeningService

### Cloud

* AWS EC2
* Nginx
* AWS CloudWatch
* AWS SNS
* AWS S3

### Optional AI

* Ollama
* Local open-source LLM
  
⚠️ **NOTE FOR JUDGES (Play Protect & Restricted Settings Warning):**
Because this app's core features rely on Android Call, Notification, and SMS permissions, Google Play Protect will flag the sideloaded `.apk` as untrusted. To test the live app, please temporarily disable Play Protect (**Play Store > Profile > Play Protect > Settings > Turn off Scan**) before installing, or click **"Install Anyway"** if prompted.

Additionally, because this prototype is downloaded via a browser, Android's security architecture will grey out the toggle buttons (**"Restricted Setting" error**). After installing, please follow these 3 quick steps to enable testing:
1. Go to your phone's **Settings > Apps > CyberShield**.
2. Tap the **three vertical dots** in the top-right corner.
3. Select **"Allow restricted settings"** and confirm. You can now enable Notification and Call permissions normally!


CyberShield also includes a rule-based fallback so that threat analysis does not depend entirely on an external AI service.

## 🚀 Run the Backend Locally

### 1. Install Python

Use Python 3.10 or newer.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate it

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the server

```bash
uvicorn app:app --reload
```

### 6. Open the application

```text
http://127.0.0.1:8000
```

## 🤖 Optional Local AI

CyberShield can optionally use Ollama for local AI analysis.

Install Ollama:

https://ollama.com

Then pull a model, for example:

```bash
ollama pull llama3.2:3b
```

Configure the model using:

```text
OLLAMA_MODEL=llama3.2:3b
```

If Ollama is unavailable, CyberShield can use its local rule-based analyzer.

## 📱 Android Setup

1. Open the `android` folder in Android Studio.
2. Build the application.
3. Install it on an Android device.
4. Configure the backend URL.
5. Enable Notification Access for CyberShield.
6. Enable the required call-screening role if testing the call component.
7. Send a test suspicious notification.

The Android application communicates with the CyberShield FastAPI backend for threat analysis.

## 🌍 Live Demo

**CyberShield Web Application:**
https://43-204-97-141.nip.io/

## 🔐 Privacy & Security

CyberShield is designed as a defensive security tool.

Users should **never submit passwords, OTPs, private keys, authentication tokens, or other sensitive secrets** for testing.

Notification Access is a powerful Android permission. Users should explicitly understand what information the application can access.

For a production deployment, additional protections should include:

* HTTPS
* Authentication
* Rate limiting
* Secure logging
* Strong privacy controls
* Secure URL/file analysis
* Access control
* Human security-team escalation

## ⚠️ Important Disclaimer

CyberShield provides **defensive threat triage** and security guidance. A detection result should not be treated as absolute proof that a message or link is malicious.

Users should verify important requests through trusted official channels.

## 🎯 Hackathon Project

CyberShield was developed as a practical cybersecurity solution focused on helping students and everyday users recognize suspicious digital communications and respond safely.

The project combines:

**Web Analysis + Backend Threat Detection + Android Sensors + Cloud Deployment**

to provide a more accessible cybersecurity experience.

## 👩‍💻 Author

**Achyutha Rakshana**

GitHub:

https://github.com/achugit0412/CyberShield
