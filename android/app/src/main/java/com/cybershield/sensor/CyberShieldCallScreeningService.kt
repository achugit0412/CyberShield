package com.cybershield.sensor

import android.telecom.Call
import android.telecom.CallScreeningService
import android.net.Uri

class CyberShieldCallScreeningService : CallScreeningService() {

    override fun onScreenCall(callDetails: Call.Details) {
        // Respond immediately. Android requires the screening service to answer
        // within a short system timeout. CyberShield does not auto-block calls.

        android.util.Log.d(
            "CyberShieldCall",
            "onScreenCall TRIGGERED: direction=${callDetails.callDirection}, handle=${callDetails.handle}"
        )
        respondToCall(
            callDetails,
            CallResponse.Builder()
                .setDisallowCall(false)
                .setRejectCall(false)
                .setSilenceCall(false)
                .build()
        )

        if (callDetails.callDirection != Call.Details.DIRECTION_INCOMING) return

        val number = callDetails.handle?.schemeSpecificPart ?: "Unknown number"
        val text = """
            Incoming phone call.
            Caller number: $number
            Treat the caller as unverified. Analyze for common scam/social-engineering warning signs.
        """.trimIndent()

        CyberShieldApi.analyze(this, text) { result ->
            if (result == null) {
                // Still provide a safety notification for an incoming screened call.
                ThreatNotifier.show(
                    this,
                    "📞 CyberShield Call Alert",
                    "Incoming call from $number. Verify the caller before sharing OTPs, banking or personal information.",
                    highPriority = true
                )
                return@analyze
            }

            val high = result.risk == "HIGH" || result.risk == "CRITICAL"
            val title = if (high) "🚨 CyberShield Call Alert" else "📞 CyberShield Call Alert"
            val body = if (high) {
                "${result.risk} risk: ${result.category}. Caller: $number"
            } else {
                "Incoming call from $number. Caller is not verified. Never share OTPs, passwords or banking details."
            }

            ThreatNotifier.show(this, title, body, highPriority = high)
        }
    }
}
