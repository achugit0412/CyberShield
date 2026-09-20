package com.cybershield.sensor

import android.app.Notification
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.os.Bundle
import android.util.Log
import java.security.MessageDigest

class CyberShieldNotificationListener : NotificationListenerService() {

    private val recent = LinkedHashMap<String, Long>(50, 0.75f, true)

    override fun onNotificationPosted(sbn: StatusBarNotification) {
        if (sbn.packageName == packageName) return

        val notification = sbn.notification ?: return
        val extras = notification.extras ?: Bundle()

        val title = extras.getCharSequence(Notification.EXTRA_TITLE)?.toString().orEmpty()
        val text = extras.getCharSequence(Notification.EXTRA_TEXT)?.toString().orEmpty()
        val bigText = extras.getCharSequence(Notification.EXTRA_BIG_TEXT)?.toString().orEmpty()

        val content = listOf(title, text, bigText)
            .filter { it.isNotBlank() }
            .distinct()
            .joinToString("\n")

        if (content.length < 4) return

        val key = sha256("${sbn.packageName}|$content")
        val now = System.currentTimeMillis()
        if (recent[key]?.let { now - it < 15_000 } == true) return
        recent[key] = now
        if (recent.size > 50) recent.remove(recent.keys.first())

        val source = appLabel(sbn.packageName)
        val analysisText = "Incoming notification from $source:\n$content"
        Log.d(
            "CyberShield",
            "TEXT SENT TO BACKEND: $analysisText"
        )
        CyberShieldApi.analyze(this, analysisText) { result ->
            if (result == null) {
                Log.e("CyberShield", "No result received from backend")
                return@analyze
            }

            Log.d(
                "CyberShield",
                "Backend result: risk=${result.risk}, score=${result.score}, category=${result.category}"
            )

            val high = result.risk == "HIGH" || result.risk == "CRITICAL"

            Log.d("CyberShield", "High risk = $high")

            if (high) {
                val body = "${result.risk} risk: ${result.category}. " +
                        (result.indicators.firstOrNull()
                            ?: "Review before clicking links or sharing information.")

                Log.d("CyberShield", "Showing threat notification: $body")

                ThreatNotifier.show(
                    this,
                    "🚨 CyberShield Message Alert",
                    body,
                    highPriority = true
                )
            }
        }
    }

    private fun appLabel(pkg: String): String {
        return try {
            val info = packageManager.getApplicationInfo(pkg, 0)
            packageManager.getApplicationLabel(info).toString()
        } catch (_: Exception) {
            pkg
        }
    }

    private fun sha256(value: String): String {
        return MessageDigest.getInstance("SHA-256")
            .digest(value.toByteArray())
            .joinToString("") { "%02x".format(it) }
    }
}
