import os
import re
import json
from urllib.parse import urlparse
from typing import List

import requests
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


# =========================================================
# APP
# =========================================================

app = FastAPI(title="CyberShield")


# =========================================================
# CONFIGURATION
# =========================================================

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    ""
)


# =========================================================
# STATIC FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =========================================================
# REQUEST MODEL
# =========================================================

class AnalyzeRequest(BaseModel):
    text: str


# =========================================================
# URL EXTRACTION
# =========================================================

def extract_urls(text: str) -> List[str]:
    """
    Extract HTTP/HTTPS URLs from a message.
    """

    return re.findall(
        r"https?://[^\s<>\]\)\"']+",
        text,
        flags=re.IGNORECASE
    )


# =========================================================
# URL ANALYSIS
# =========================================================

def analyze_urls(urls: List[str]):
    """
    Detect suspicious characteristics in URLs.

    These indicators do NOT prove that a URL is malicious.
    """

    indicators = []

    for url in urls:

        try:
            parsed = urlparse(url)

            hostname = parsed.hostname or ""
            hostname_lower = hostname.lower()

            # -------------------------------------------------
            # IP address
            # -------------------------------------------------

            if re.fullmatch(
                r"\d{1,3}(\.\d{1,3}){3}",
                hostname_lower
            ):
                indicators.append(
                    "Link uses an IP address instead of a normal domain"
                )

            # -------------------------------------------------
            # @ symbol
            # -------------------------------------------------

            if "@" in parsed.netloc:

                indicators.append(
                    "Link contains an @ symbol that can obscure the destination"
                )

            # -------------------------------------------------
            # Punycode
            # -------------------------------------------------

            if "xn--" in hostname_lower:

                indicators.append(
                    "Link uses punycode, which can be used in look-alike domains"
                )

            # -------------------------------------------------
            # Very long URL
            # -------------------------------------------------

            if len(url) > 180:

                indicators.append(
                    "Link is unusually long"
                )

            # -------------------------------------------------
            # Suspicious URL keywords
            # -------------------------------------------------

            suspicious_words = [
                "verify",
                "verification",
                "secure",
                "security",
                "login",
                "signin",
                "account",
                "update",
                "confirm",
                "wallet",
                "refund",
                "reward",
                "claim",
                "otp",
                "kyc",
                "password",
            ]

            found_words = [
                word
                for word in suspicious_words
                if word in url.lower()
            ]

            if found_words:

                indicators.append(
                    "Link contains security/account-related keywords: "
                    + ", ".join(found_words[:5])
                )

            # -------------------------------------------------
            # Excessive subdomains
            # -------------------------------------------------

            if hostname.count(".") >= 4:

                indicators.append(
                    "Link contains an unusually large number of subdomains"
                )

        except Exception:

            indicators.append(
                "A URL could not be fully parsed"
            )

    return list(
        dict.fromkeys(indicators)
    )


# =========================================================
# ATTACK EXPLANATION
# =========================================================

def get_attack_explanation(
    text: str,
    category: str,
    indicators: list,
    risk: str
):
    """
    Explain the likely social-engineering or attack mechanism.

    This is an explanation of detected patterns, not proof
    that the sender is malicious.
    """

    t = text.lower()

    # -----------------------------------------------------
    # PHISHING
    # -----------------------------------------------------

    if category == "Possible phishing / credential theft":

        return (
            "This message shows characteristics of a phishing attack. "
            "The sender may be trying to make the recipient trust a fake "
            "account, security, login, or verification request. The typical "
            "attack path is to create urgency or fear, direct the victim to "
            "a website or form, and attempt to obtain credentials, OTPs, "
            "passwords, or other authentication information. If the victim "
            "provides the information, it could potentially be used to access "
            "an account or support further fraud."
        )

    # -----------------------------------------------------
    # FINANCIAL SCAM
    # -----------------------------------------------------

    if category == "Possible financial scam":

        return (
            "This message shows characteristics of a financial "
            "social-engineering attack. The sender may be attempting to "
            "persuade the recipient to send money, pay a fee, authorize a "
            "transaction, or reveal financial information. These scams often "
            "use urgency, fear of account problems, refunds, rewards, or "
            "promises of financial benefits to make the victim act before "
            "independently verifying the claim."
        )

    # -----------------------------------------------------
    # RECRUITMENT SCAM
    # -----------------------------------------------------

    if category == "Possible recruitment / social-engineering scam":

        if (
            "whatsapp" in t
            or "telegram" in t
        ):

            return (
                "This message appears to use recruitment-based social "
                "engineering. The sender establishes credibility by claiming "
                "that the recipient has been selected or shortlisted for a "
                "job or internship. It then creates a sense of urgency around "
                "the next step and moves the interaction to a messaging "
                "platform such as WhatsApp or Telegram. This can be a "
                "trust-building stage of a scam. Later stages may request "
                "registration fees, identity documents, banking information, "
                "credentials, or other sensitive information. The message "
                "alone does not prove malicious intent, so the organization "
                "should be verified independently."
            )

        return (
            "This message appears to use recruitment-based social "
            "engineering. It attempts to establish credibility through a "
            "job or internship selection claim and encourages the recipient "
            "to take a specific next step. Recruitment scams can later "
            "request money, identity documents, credentials, or other "
            "sensitive information. Verify the opportunity through the "
            "organization's independently found official channels."
        )

    # -----------------------------------------------------
    # MALWARE / REMOTE ACCESS
    # -----------------------------------------------------

    if category == "Possible malware / remote-access scam":

        return (
            "This message shows characteristics of a remote-access or "
            "malware-related social-engineering attack. The sender may try "
            "to convince the victim to install software or provide remote "
            "access to a device. If access is granted, the attacker could "
            "potentially view files, interact with applications, steal "
            "information, or access accounts available on the device."
        )

    # -----------------------------------------------------
    # GENERAL SOCIAL ENGINEERING
    # -----------------------------------------------------

    return (
        "This message contains social-engineering indicators. Social "
        "engineering attempts to influence a person into taking an action "
        "that benefits an attacker, such as clicking a link, sharing "
        "information, sending money, or installing software. CyberShield "
        "detected patterns that deserve additional verification before "
        "interacting with the sender."
    )


# =========================================================
# RESPONSE GUIDANCE
# =========================================================

def response_guidance(category: str):

    guidance = {

        "Possible phishing / credential theft": {

            "what_to_do": [
                "Do not click suspicious links.",
                "Do not share passwords, OTPs, PINs or verification codes.",
                "Open the organization's official website or app manually.",
                "Contact the organization through a verified support channel if necessary."
            ],

            "if_already_interacted": [
                "If you entered a password, change it immediately using the official website.",
                "Enable multi-factor authentication where available.",
                "If you shared an OTP or verification code, contact the affected service immediately.",
                "Review recent login activity and sign out unknown sessions.",
                "If financial information was shared, contact your bank or payment provider immediately."
            ]
        },


        "Possible financial scam": {

            "what_to_do": [
                "Do not transfer money because of the message.",
                "Do not pay registration, processing, unlocking or verification fees without independent verification.",
                "Never share UPI PINs, banking passwords or OTPs.",
                "Verify the organization through an independently found official contact."
            ],

            "if_already_interacted": [
                "Contact your bank or payment provider immediately.",
                "Report unauthorized transactions through the official banking or payment channel.",
                "Change compromised banking credentials.",
                "Preserve screenshots, transaction IDs and the original message.",
                "If money was transferred fraudulently, report it through the appropriate official cybercrime or banking channel."
            ]
        },


        "Possible recruitment / social-engineering scam": {

            "what_to_do": [
                "Verify the job or internship directly on the organization's official website.",
                "Do not pay recruitment, registration or training fees without independent verification.",
                "Do not share identity documents or banking information unnecessarily.",
                "Be cautious when a recruiter moves the conversation to WhatsApp or Telegram and creates urgency."
            ],

            "if_already_interacted": [
                "Stop sending additional personal or financial information.",
                "If you submitted documents, monitor for suspicious activity.",
                "If you shared a password, change it immediately.",
                "If you paid money, contact your bank or payment provider and preserve transaction evidence.",
                "Report the suspicious account or group to the platform."
            ]
        },


        "Possible malware / remote-access scam": {

            "what_to_do": [
                "Do not install software requested by an unexpected message or caller.",
                "Do not give remote desktop access to an unknown person.",
                "Download software only from the developer's official website or trusted app store.",
                "Do not disable security protections to install unknown software."
            ],

            "if_already_interacted": [
                "Disconnect the affected device from the internet if you suspect active unauthorized access.",
                "Remove unauthorized remote-access software if safe to do so.",
                "Change important passwords from a trusted device.",
                "Review banking and account activity.",
                "Run a trusted security scan and seek professional assistance if the device remains compromised."
            ]
        },


        "Suspicious message / social engineering": {

            "what_to_do": [
                "Pause before responding.",
                "Verify the sender and claim independently.",
                "Do not share secrets, credentials or financial information.",
                "Avoid clicking unexpected links or opening suspicious attachments."
            ],

            "if_already_interacted": [
                "Stop further communication with the sender.",
                "Change credentials if you disclosed them.",
                "Monitor relevant accounts for suspicious activity.",
                "Keep screenshots and other evidence."
            ]
        }
    }

    return guidance.get(
        category,
        guidance["Suspicious message / social engineering"]
    )


# =========================================================
# RULE-BASED DETECTOR
# =========================================================

def rule_analyze(text: str):

    original_text = text
    t = text.lower()

    indicators = []
    score = 0

    urls = extract_urls(
        original_text
    )

    # =====================================================
    # CONTEXT
    # =====================================================

    educational_context = any(
        phrase in t
        for phrase in [
            "cybersecurity example",
            "security awareness",
            "phishing example",
            "training example",
            "test message",
            "demo message",
            "example of phishing"
        ]
    )

    # =====================================================
    # CREDENTIAL REQUEST
    # =====================================================

    credential_request = re.search(
        r"\b("
        r"send|share|provide|enter|submit|confirm|verify|"
        r"give|tell|reply"
        r")\b.{0,60}\b("
        r"otp|password|passcode|pin|verification code|"
        r"login|credentials|security code"
        r")\b",
        t
    )

    if credential_request:

        score += 35

        indicators.append(
            "Message appears to request credentials or a verification code"
        )

    elif re.search(
        r"\b("
        r"otp|one[- ]time password|verification code|"
        r"password|passcode|pin|login credentials"
        r")\b",
        t
    ):

        score += 18

        indicators.append(
            "Credential or verification-code language is present"
        )

    # =====================================================
    # URGENCY
    # =====================================================

    if re.search(
        r"\b("
        r"urgent|immediately|act now|right now|"
        r"today|within \d+ hours|last chance|"
        r"expires|final warning|hurry|"
        r"do not delay"
        r")\b",
        t
    ):

        score += 18

        indicators.append(
            "Urgency or pressure is used to encourage quick action"
        )

    # =====================================================
    # FINANCIAL
    # =====================================================

    financial = re.search(
        r"\b("
        r"bank|upi|wallet|refund|kyc|credit card|"
        r"debit card|payment|pay|deposit|fee|"
        r"transfer|transaction|account"
        r")\b",
        t
    )

    if financial:

        score += 20

        indicators.append(
            "Financial or account-related language is present"
        )

    # =====================================================
    # RECRUITMENT
    # =====================================================

    recruitment = re.search(
        r"\b("
        r"job|internship|intern|salary|stipend|"
        r"recruitment|hiring|selection|shortlisted|"
        r"joining|induction|career|vacancy|offer letter"
        r")\b",
        t
    )

    if recruitment:

        score += 15

        indicators.append(
            "Recruitment or internship language is present"
        )

    # =====================================================
    # RECRUITMENT + MONEY
    # =====================================================

    if recruitment and financial:

        score += 20

        indicators.append(
            "Recruitment-related content is combined with payment or financial language"
        )

    # =====================================================
    # RECRUITMENT + MESSAGING PLATFORM
    # =====================================================

    if recruitment and re.search(
        r"\b(whatsapp|telegram)\b",
        t
    ):

        score += 12

        indicators.append(
            "Recruitment communication is redirected to a messaging platform"
        )

    # =====================================================
    # PRIZE / REWARD
    # =====================================================

    if re.search(
        r"\b("
        r"prize|winner|selected|congratulations|"
        r"reward|lottery|cash prize|free gift"
        r")\b",
        t
    ):

        score += 15

        indicators.append(
            "Unexpected prize, reward or selection language is present"
        )

    # =====================================================
    # ACTION REQUEST
    # =====================================================

    if re.search(
        r"\b("
        r"click|verify|confirm|activate|login|"
        r"sign in|join|register|download|install|"
        r"open|submit"
        r")\b",
        t
    ):

        score += 10

        indicators.append(
            "Message asks the recipient to perform an action"
        )

    # =====================================================
    # REMOTE ACCESS / MALWARE
    # =====================================================

    if re.search(
        r"\b("
        r"remote access|remote desktop|anydesk|"
        r"teamviewer|quick assist|install this app|"
        r"download this software"
        r")\b",
        t
    ):

        score += 35

        indicators.append(
            "Message requests remote access or software installation"
        )

    # =====================================================
    # URLS
    # =====================================================

    if urls:

        score += 12

        indicators.append(
            f"Message contains {len(urls)} web link"
            + ("s" if len(urls) != 1 else "")
        )

        url_indicators = analyze_urls(
            urls
        )

        if url_indicators:

            score += min(
                len(url_indicators) * 8,
                30
            )

            indicators.extend(
                url_indicators
            )

    # =====================================================
    # CREDENTIAL + URL
    # =====================================================

    if credential_request and urls:

        score += 15

        indicators.append(
            "A credential-related request is combined with a web link"
        )

    # =====================================================
    # FINANCIAL + URL
    # =====================================================

    if financial and urls:

        score += 10

        indicators.append(
            "Financial/account language is combined with a web link"
        )

    # =====================================================
    # RECRUITMENT + PAYMENT
    # =====================================================

    if recruitment and re.search(
        r"\b("
        r"pay|payment|fee|deposit|registration fee|"
        r"processing fee"
        r")\b",
        t
    ):

        score += 20

        indicators.append(
            "Recruitment content appears to involve a fee or payment"
        )

    # =====================================================
    # EDUCATIONAL CONTEXT
    # =====================================================

    if educational_context:

        score = max(
            score - 25,
            0
        )

        indicators.append(
            "Message appears to be presented as a security-awareness or test example"
        )

    # =====================================================
    # CAP SCORE
    # =====================================================

    score = min(
        score,
        100
    )

    # =====================================================
    # CATEGORY
    # =====================================================

    if re.search(
        r"\b("
        r"anydesk|teamviewer|remote access|"
        r"remote desktop|install this app"
        r")\b",
        t
    ):

        category = (
            "Possible malware / remote-access scam"
        )

    elif recruitment and financial:

        category = (
            "Possible recruitment / social-engineering scam"
        )

    elif recruitment:

        category = (
            "Possible recruitment / social-engineering scam"
        )

    elif financial and (
        credential_request
        or urls
        or re.search(
            r"\b(verify|kyc|refund|account|otp)\b",
            t
        )
    ):

        category = (
            "Possible financial scam"
        )

    elif credential_request or re.search(
        r"\b("
        r"otp|password|login|credentials|"
        r"verification code|kyc"
        r")\b",
        t
    ):

        category = (
            "Possible phishing / credential theft"
        )

    else:

        category = (
            "Suspicious message / social engineering"
        )

    # =====================================================
    # RISK
    # =====================================================

    if score >= 80:

        risk = "CRITICAL"

    elif score >= 55:

        risk = "HIGH"

    elif score >= 30:

        risk = "MEDIUM"

    else:

        risk = "LOW"

    # =====================================================
    # CONFIDENCE
    # =====================================================

    if len(indicators) >= 6:

        confidence = "HIGH"

    elif len(indicators) >= 3:

        confidence = "MEDIUM"

    else:

        confidence = "LOW"

    # =====================================================
    # ATTACK EXPLANATION
    # =====================================================

    attack_explanation = get_attack_explanation(
        original_text,
        category,
        indicators,
        risk
    )

    # =====================================================
    # RESPONSE GUIDANCE
    # =====================================================

    guidance = response_guidance(
        category
    )

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    indicators = list(
        dict.fromkeys(
            indicators
        )
    )[:10]

    # =====================================================
    # RESULT
    # =====================================================

    return {

        "risk": risk,

        "score": score,

        "category": category,

        "confidence": confidence,

        "attack_explanation":
            attack_explanation,

        "indicators":
            indicators,

        "actions":
            guidance["what_to_do"],

        "what_to_do":
            guidance["what_to_do"],

        "if_already_interacted":
            guidance["if_already_interacted"],

        "urls_found":
            urls,

        "engine":
            "CyberShield Rule Engine",

        "note": (
            "This assessment identifies risk indicators. "
            "It is not proof that the sender or message is malicious."
        )
    }


# =========================================================
# OPTIONAL OLLAMA AI
# =========================================================

def ai_analyze(text: str):

    prompt = f"""
You are CyberShield, a defensive cybersecurity triage assistant.

Analyze this user-provided message.

Return ONLY valid JSON.

Required format:

{{
    "risk": "LOW|MEDIUM|HIGH|CRITICAL",
    "score": 0,
    "category": "string",
    "confidence": "LOW|MEDIUM|HIGH",
    "attack_explanation": "Explain how the suspected attack or social-engineering technique may work.",
    "indicators": [],
    "what_to_do": [],
    "if_already_interacted": []
}}

Rules:

- Do not claim certainty.
- Explain the likely attack mechanism.
- Identify concrete warning signs.
- Give defensive actions.
- Never ask for passwords, OTPs or other secrets.
- Do not provide offensive instructions.
- A suspicious message is not automatically proof of malicious intent.

MESSAGE:

{text[:8000]}
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=45
        )

        response.raise_for_status()

        raw = response.json().get(
            "response",
            ""
        )

        data = json.loads(
            raw
        )

        # -------------------------------------------------
        # Defaults
        # -------------------------------------------------

        data.setdefault(
            "risk",
            "MEDIUM"
        )

        data.setdefault(
            "score",
            50
        )

        data.setdefault(
            "category",
            "Suspicious message / social engineering"
        )

        data.setdefault(
            "confidence",
            "MEDIUM"
        )

        data.setdefault(
            "attack_explanation",
            "The AI detected social-engineering indicators that should be independently verified."
        )

        data.setdefault(
            "indicators",
            []
        )

        data.setdefault(
            "what_to_do",
            []
        )

        data.setdefault(
            "if_already_interacted",
            []
        )

        data["actions"] = data[
            "what_to_do"
        ]

        data["urls_found"] = extract_urls(
            text
        )

        data["engine"] = (
            "CyberShield + Local AI"
        )

        data["note"] = (
            "This assessment identifies risk indicators. "
            "It is not proof that the sender or message is malicious."
        )

        return data

    except Exception as error:

        print(
            "Ollama analysis failed:",
            error
        )

        return None


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return FileResponse(
        "static/index.html"
    )


# =========================================================
# ANALYZE API
# =========================================================

@app.post("/api/analyze")
def analyze(
    req: AnalyzeRequest
):

    text = req.text.strip()

    # -----------------------------------------------------
    # Empty message
    # -----------------------------------------------------

    if not text:

        return {
            "error":
                "Paste a message first."
        }

    # -----------------------------------------------------
    # Length limit
    # -----------------------------------------------------

    if len(text) > 10000:

        return {
            "error":
                "Message is too long for this prototype."
        }

    # -----------------------------------------------------
    # AI if configured
    # -----------------------------------------------------

    result = None

    if OLLAMA_MODEL:

        result = ai_analyze(
            text
        )

    # -----------------------------------------------------
    # Rule engine fallback
    # -----------------------------------------------------

    if result is None:

        result = rule_analyze(
            text
        )

    return result