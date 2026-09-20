const analyzeBtn = document.getElementById("analyzeBtn");
const messageBox = document.getElementById("messageInput");
const results = document.getElementById("results");
const loading = document.getElementById("loading");
const notifyBtn = document.getElementById("notifyBtn");

analyzeBtn.addEventListener("click", analyzeThreat);

async function analyzeThreat() {

    const message = messageBox.value.trim();

    if (!message) {
        alert("Please paste something suspicious to analyze.");
        return;
    }

    results.classList.add("hidden");
    loading.classList.remove("hidden");

    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = "⏳ Scanning...";

    try {

        const response = await fetch("/api/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: message
            })
        });

        if (!response.ok) {
            throw new Error("Analysis failed");
        }

        const data = await response.json();

        displayResults(data);

    } catch (error) {

        console.error(error);
        alert("CyberShield could not analyze this message. Check that the server is running.");

    } finally {

        loading.classList.add("hidden");
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = "<span>⚡</span> Analyze Threat";
    }
}


function displayResults(data) {

    results.classList.remove("hidden");

    const score =
        Number(data.risk_score ??
        data.score ??
        0);

    const risk =
        data.risk_level ??
        data.risk ??
        "LOW";

    const category =
        data.category ??
        "Suspicious content";

    const indicators =
        data.indicators ??
        [];

    const actions =
        data.actions ??
        data.what_to_do ??
        [];

    const whatToDo =
        data.what_to_do ??
        [];

    const ifAlreadyInteracted =
        data.if_already_interacted ??
        [];

    document.getElementById("riskScore").textContent = score;

    document.getElementById("scoreBar").style.width =
        Math.min(score, 100) + "%";

    const riskLabel =
        document.getElementById("riskLabel");

    riskLabel.textContent =
        risk.toUpperCase();

    riskLabel.className =
        "risk-label " + risk.toLowerCase();

    document.getElementById("category").textContent =
        category;

    document.getElementById("indicatorCount").textContent =
        indicators.length;

    document.getElementById("recommendation").textContent =
        getRecommendation(risk);

    renderIndicators(indicators);

    // Existing action section
    renderActions(actions);

    // NEW: Immediate steps
    renderWhatToDo(whatToDo);

    // NEW: Steps if user already interacted
    renderAlreadyInteracted(ifAlreadyInteracted);

    if (
        (risk.toUpperCase() === "HIGH" ||
        risk.toUpperCase() === "CRITICAL") &&
        Notification.permission === "granted"
    ) {

        new Notification("🚨 CyberShield Threat Alert", {
            body: `${risk.toUpperCase()} risk detected: ${category}`
        });

    }

    results.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

function renderIndicators(indicators) {

    const container =
        document.getElementById("indicators");

    container.innerHTML = "";

    if (!indicators.length) {

        container.innerHTML =
            `<div class="indicator">
                No major warning indicators detected.
            </div>`;

        return;
    }

    indicators.forEach(item => {

        const div =
            document.createElement("div");

        div.className = "indicator";

        div.textContent =
            typeof item === "string"
                ? item
                : item.description || item.name || JSON.stringify(item);

        container.appendChild(div);
    });
}


function renderActions(actions) {

    const container =
        document.getElementById("actions");

    container.innerHTML = "";

    if (!actions.length) {

        container.innerHTML =
            `<div class="action">
                Verify the sender independently before taking action.
            </div>`;

        return;
    }

    actions.forEach(item => {

        const div =
            document.createElement("div");

        div.className = "action";

        div.textContent =
            typeof item === "string"
                ? item
                : item.description || item.name || JSON.stringify(item);

        container.appendChild(div);
    });
}
function renderWhatToDo(items) {

    const container =
        document.getElementById("whatToDo");

    // If the HTML section doesn't exist, don't cause an error
    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!items || !items.length) {

        container.innerHTML =
            `<div class="action">
                Do not respond, click links, or share sensitive information.
                Verify the message through an official source.
            </div>`;

        return;
    }

    items.forEach(item => {

        const div =
            document.createElement("div");

        div.className = "action";

        div.textContent =
            typeof item === "string"
                ? item
                : item.description || item.name || JSON.stringify(item);

        container.appendChild(div);
    });
}


function renderAlreadyInteracted(items) {

    const container =
        document.getElementById("alreadyInteracted");

    // If the HTML section doesn't exist, don't cause an error
    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!items || !items.length) {

        container.innerHTML =
            `<div class="action">
                Stop further interaction and verify your accounts or information.
            </div>`;

        return;
    }

    items.forEach(item => {

        const div =
            document.createElement("div");

        div.className = "action";

        div.textContent =
            typeof item === "string"
                ? item
                : item.description || item.name || JSON.stringify(item);

        container.appendChild(div);
    });
}


function getRecommendation(risk) {

    const value =
        risk.toUpperCase();

    if (value === "CRITICAL") return "Do not interact";

    if (value === "HIGH") return "Verify first";

    if (value === "MEDIUM") return "Use caution";

    return "Low concern";
}


/* BROWSER NOTIFICATIONS */

notifyBtn.addEventListener("click", async () => {

    if (!("Notification" in window)) {

        alert("Browser notifications are not supported.");
        return;
    }

    const permission =
        await Notification.requestPermission();

    if (permission === "granted") {

        notifyBtn.textContent =
            "🔔 Alerts Enabled";

        new Notification("🛡️ CyberShield", {
            body: "Threat notifications are now enabled."
        });

    } else {

        notifyBtn.textContent =
            "🔕 Alerts Blocked";
    }
});


/* ENTER KEY */

messageBox.addEventListener("keydown", event => {

    if (
        event.ctrlKey &&
        event.key === "Enter"
    ) {
        analyzeThreat();
    }

});
/* =========================================================
   SOLUTION CARD INTERACTIONS
   ========================================================= */

const solutionCards = document.querySelectorAll(".solution-card");

const solutionInfo = {

    phishing: {
        label: "01 / PHISHING DETECTION",
        title: "HOW PHISHING ATTACKS HAPPEN",
        description:
            "Phishing is a social-engineering attack where someone pretends to be a trusted person, company, service, or organization to trick you into revealing information or taking an unsafe action.",

        how:
            "A common phishing attempt starts with an unexpected email, SMS, social-media message, or notification. The message may create urgency, claim there is a problem with an account, or offer a reward. It then tries to get the victim to click a link, open an attachment, or provide information.",

        signs: [
            "Unexpected messages asking you to act immediately.",
            "Links that do not match the real organization.",
            "Requests for passwords, OTPs, or sensitive information.",
            "Threats such as account suspension or loss of access.",
            "Messages containing unusual spelling, sender addresses, or formatting."
        ],

        prevention: [
            "Do not click unexpected links.",
            "Open the official website directly instead.",
            "Never share passwords or OTPs through messages.",
            "Verify the sender using an independent contact method.",
            "Use multi-factor authentication on important accounts."
        ],

        after:
            "If you already clicked a suspicious link, do not enter additional information. If you entered a password, change it through the legitimate website and enable multi-factor authentication. If sensitive information or money was involved, contact the relevant organization immediately."
    },


    scam: {
        label: "02 / SCAM ANALYSIS",
        title: "HOW ONLINE SCAMS HAPPEN",
        description:
            "Scams use deception to convince people to send money, reveal information, or perform an action that benefits the scammer.",

        how:
            "A scammer commonly creates a believable story such as a job offer, prize, refund, investment opportunity, emergency, or payment request. The message is designed to make the victim trust the story before checking whether it is legitimate.",

        signs: [
            "Promises of unusually large rewards.",
            "Requests for upfront fees or payments.",
            "Pressure to make a decision immediately.",
            "Requests for OTPs, banking information, or passwords.",
            "Communication that avoids normal verification channels."
        ],

        prevention: [
            "Verify offers independently.",
            "Do not send money because of an unexpected message.",
            "Never share OTPs or passwords.",
            "Research the organization using its official website.",
            "Be cautious with offers that create artificial urgency."
        ],

        after:
            "If you already sent money or sensitive information, contact your bank or payment provider as soon as possible, secure affected accounts, preserve screenshots and messages, and report the incident through the appropriate service."
    },


    url: {
        label: "03 / URL INTELLIGENCE",
        title: "HOW DECEPTIVE LINKS WORK",
        description:
            "A suspicious URL can redirect a user to a fake login page, fraudulent payment page, malicious download, or another unsafe destination.",

        how:
            "Attackers may make a link appear trustworthy by using a familiar-looking name, a misleading subdomain, unusual characters, or a domain that resembles a legitimate organization.",

        signs: [
            "The domain name does not belong to the claimed organization.",
            "The URL contains unusual characters or spelling.",
            "The message hides the destination behind unexpected links.",
            "The link is paired with an urgent request.",
            "The website asks for sensitive information unexpectedly."
        ],

        prevention: [
            "Check the actual domain before entering information.",
            "Navigate to important services manually.",
            "Avoid unexpected shortened or suspicious links.",
            "Use browser security warnings as an additional signal.",
            "Do not download files from untrusted websites."
        ],

        after:
            "If you opened a suspicious website but did not enter information, close it. If you entered credentials, change them through the legitimate service and review account activity."
    },


    account: {
        label: "04 / ACCOUNT SAFETY",
        title: "HOW ACCOUNT TAKEOVER ATTEMPTS HAPPEN",
        description:
            "Account takeover attempts try to obtain credentials or authentication information so someone else can access an account.",

        how:
            "Attackers may use fake login pages, impersonated support messages, password-reuse attacks, or requests for authentication codes.",

        signs: [
            "Unexpected login or verification messages.",
            "Requests to share an OTP or authentication code.",
            "Unexpected password-reset notifications.",
            "Login pages reached through suspicious links.",
            "Unrecognized account activity."
        ],

        prevention: [
            "Use unique passwords for important accounts.",
            "Enable multi-factor authentication.",
            "Never share authentication codes.",
            "Review account login activity.",
            "Use official websites instead of unexpected login links."
        ],

        after:
            "Change the affected password immediately through the legitimate service, sign out other sessions if available, enable multi-factor authentication, and review recent account activity."
    },


    incident: {
        label: "05 / INCIDENT RESPONSE",
        title: "WHAT TO DO AFTER A SECURITY INCIDENT",
        description:
            "Incident response means taking practical steps to limit damage after interacting with suspicious content.",

        how:
            "The correct response depends on what happened. The priority is to stop further interaction, secure affected accounts or devices, and preserve evidence.",

        signs: [
            "You clicked a suspicious link.",
            "You entered credentials into an unfamiliar website.",
            "You downloaded an unexpected file.",
            "You shared sensitive information.",
            "You sent money because of a suspicious message."
        ],

        prevention: [
            "Stop communicating with the suspicious sender.",
            "Change compromised passwords.",
            "Enable multi-factor authentication.",
            "Contact your bank if a financial transaction occurred.",
            "Keep screenshots, messages, URLs, and transaction information."
        ],

        after:
            "Do not delete useful evidence. Secure affected accounts and devices first. If financial information, identity information, or an important account was compromised, contact the relevant provider and use its official incident-reporting process."
    }

};


function getSolutionType(card) {

    const heading = card.querySelector("h3");

    if (!heading) {
        return null;
    }

    const text =
        heading.textContent
            .toLowerCase()
            .replace(/\s+/g, " ");

    if (text.includes("phishing")) {
        return "phishing";
    }

    if (text.includes("scam")) {
        return "scam";
    }

    if (text.includes("url")) {
        return "url";
    }

    if (text.includes("account")) {
        return "account";
    }

    if (text.includes("incident")) {
        return "incident";
    }

    return null;
}


function createSolutionPanel(card, data) {

    const oldPanel =
        document.getElementById("solutionExplanation");

    if (oldPanel) {
        oldPanel.remove();
    }

    const panel =
        document.createElement("section");

    panel.id = "solutionExplanation";

    panel.className = "solution-explanation";

    panel.innerHTML = `

        <button
            type="button"
            class="solution-explanation-close"
            id="closeSolutionExplanation"
            aria-label="Close explanation"
        >
            ×
        </button>

        <div class="solution-explanation-label">
            ${data.label}
        </div>

        <h2>
            ${data.title}
        </h2>

        <p class="solution-explanation-description">
            ${data.description}
        </p>

        <div class="solution-explanation-grid">

            <div class="solution-explanation-box">

                <span>HOW IT COMMONLY HAPPENS</span>

                <p>
                    ${data.how}
                </p>

            </div>


            <div class="solution-explanation-box">

                <span>WARNING SIGNS</span>

                <ul>
                    ${data.signs
                        .map(sign => `<li>${sign}</li>`)
                        .join("")}
                </ul>

            </div>


            <div class="solution-explanation-box">

                <span>HOW TO PREVENT IT</span>

                <ul>
                    ${data.prevention
                        .map(item => `<li>${item}</li>`)
                        .join("")}
                </ul>

            </div>


            <div class="solution-explanation-box">

                <span>IF IT ALREADY HAPPENED</span>

                <p>
                    ${data.after}
                </p>

            </div>

        </div>
    `;


    const solutionGrid =
        document.querySelector(".solution-grid");

    if (!solutionGrid) {
        return;
    }

    solutionGrid.after(panel);


    document
        .getElementById("closeSolutionExplanation")
        .addEventListener("click", function () {

            panel.remove();

            card.classList.remove("solution-active");

        });


    panel.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


solutionCards.forEach(function (card) {

    const type =
        getSolutionType(card);

    if (!type || !solutionInfo[type]) {
        return;
    }

    card.style.cursor = "pointer";

    card.addEventListener("click", function () {

        solutionCards.forEach(function (item) {
            item.classList.remove("solution-active");
        });

        card.classList.add("solution-active");

        createSolutionPanel(
            card,
            solutionInfo[type]
        );

    });

});