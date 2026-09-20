package com.cybershield.sensor

import android.Manifest
import android.app.Activity
import android.app.role.RoleManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.telecom.TelecomManager
import android.view.Gravity
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.graphics.Color
import android.graphics.Typeface
import android.view.ViewGroup
import android.widget.Toast

class MainActivity : Activity() {

    private lateinit var statusText: TextView
    private lateinit var backendInput: EditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        buildUi()

        if (Build.VERSION.SDK_INT >= 33) {
            requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 10)
        }
    }

    override fun onResume() {
        super.onResume()
        updateStatus()
    }

    private fun buildUi() {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(20), dp(24), dp(20), dp(24))
            setBackgroundColor(Color.rgb(10, 10, 12))
        }

        val scroll = ScrollView(this)
        val content = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
        }

        val logo = TextView(this).apply {
            text = "CYBERSHIELD"
            textSize = 28f
            setTextColor(Color.WHITE)
            typeface = Typeface.DEFAULT_BOLD
        }
        content.addView(logo)

        val subtitle = TextView(this).apply {
            text = "MESSAGE + CALL SAFETY SENSOR"
            textSize = 12f
            setTextColor(Color.rgb(228, 91, 156))
            setPadding(0, dp(4), 0, dp(20))
        }
        content.addView(subtitle)

        statusText = TextView(this).apply {
            textSize = 15f
            setTextColor(Color.WHITE)
            setPadding(dp(16), dp(16), dp(16), dp(16))
            setBackgroundResource(com.cybershield.sensor.R.drawable.bg_card)
        }
        content.addView(statusText)

        addSpacer(content, 16)

        content.addView(label("BACKEND URL"))
        backendInput = EditText(this).apply {
            setText(AppPrefs.getBaseUrl(this@MainActivity))
            setTextColor(Color.WHITE)
            setHintTextColor(Color.GRAY)
            setHint("http://10.0.2.2:8000")
            textSize = 14f
            setSingleLine(true)
        }
        content.addView(backendInput, match())

        val save = button("SAVE BACKEND URL") {
            AppPrefs.setBaseUrl(this, backendInput.text.toString())
            Toast.makeText(this, "Backend URL saved", Toast.LENGTH_SHORT).show()
        }
        content.addView(save, match())

        addSpacer(content, 14)

        val messageAccess = button("📩 ENABLE MESSAGE SENSOR") {
            startActivity(Intent("android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS"))
        }
        content.addView(messageAccess, match())

        val callAccess = button("📞 ENABLE CALL SENSOR") {
            requestCallScreeningRole()
        }
        content.addView(callAccess, match())

        addSpacer(content, 16)

        val test = button("🚨 SEND TEST ALERT") {
            ThreatNotifier.show(
                this,
                "🚨 CyberShield Test Alert",
                "Sensor notifications are working. HIGH/CRITICAL detections will use this alert channel.",
                true
            )
        }
        content.addView(test, match())

        addSpacer(content, 20)

        val privacy = TextView(this).apply {
            text = "Privacy: CyberShield only receives notification content after you grant Android notification-access permission. Calls are passed to the call-screening service by Android. CyberShield does not automatically block calls in this version."
            textSize = 12f
            setTextColor(Color.rgb(170, 170, 178))
            setPadding(dp(4), 0, dp(4), 0)
        }
        content.addView(privacy)

        scroll.addView(content)
        root.addView(scroll, LinearLayout.LayoutParams(-1, 0, 1f))
        setContentView(root)
    }

    private fun requestCallScreeningRole() {
        if (Build.VERSION.SDK_INT >= 29) {
            val roleManager = getSystemService(RoleManager::class.java)
            if (roleManager.isRoleAvailable(RoleManager.ROLE_CALL_SCREENING)) {
                startActivityForResult(
                    roleManager.createRequestRoleIntent(RoleManager.ROLE_CALL_SCREENING),
                    20
                )
            } else {
                Toast.makeText(this, "Call screening is not available on this device.", Toast.LENGTH_LONG).show()
            }
        } else {
            Toast.makeText(this, "Call sensor requires Android 10 or newer.", Toast.LENGTH_LONG).show()
        }
    }

    private fun updateStatus() {
        val notificationEnabled = try {
            val cn = ComponentName(this, CyberShieldNotificationListener::class.java)
            val enabled = Settings.Secure.getString(
                contentResolver,
                "enabled_notification_listeners"
            ).orEmpty()
            enabled.contains(cn.flattenToString())
        } catch (_: Exception) { false }

        val callEnabled = if (Build.VERSION.SDK_INT >= 29) {
            getSystemService(RoleManager::class.java)
                .isRoleHeld(RoleManager.ROLE_CALL_SCREENING)
        } else false

        statusText.text = buildString {
            append("SENSOR STATUS\n\n")
            append(if (notificationEnabled) "🟢 Message sensor: ACTIVE\n" else "🔴 Message sensor: OFF\n")
            append(if (callEnabled) "🟢 Call sensor: ACTIVE" else "🔴 Call sensor: OFF")
        }
    }

    private fun label(text: String) = TextView(this).apply {
        this.text = text
        textSize = 11f
        setTextColor(Color.rgb(160, 160, 168))
        setTypeface(null, Typeface.BOLD)
        setPadding(0, 0, 0, dp(6))
    }

    private fun button(text: String, action: () -> Unit) = Button(this).apply {
        this.text = text
        setTextColor(Color.WHITE)
        setBackgroundResource(R.drawable.bg_button)
        setOnClickListener { action() }
        minHeight = dp(52)
    }

    private fun addSpacer(parent: ViewGroup, height: Int) {
        val spacer = TextView(this)
        parent.addView(spacer, LinearLayout.LayoutParams(1, height))
    }

    private fun match() = LinearLayout.LayoutParams(-1, dp(56)).apply {
        bottomMargin = dp(10)
    }

    private fun dp(value: Int): Int =
        (value * resources.displayMetrics.density).toInt()
}
