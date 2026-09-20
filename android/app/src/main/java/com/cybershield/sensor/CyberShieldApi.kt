package com.cybershield.sensor

import android.content.Context
import android.util.Log
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.Executors

object CyberShieldApi {
    private val executor = Executors.newSingleThreadExecutor()

    fun analyze(context: Context, text: String, callback: (ThreatResult?) -> Unit) {
        executor.execute {
            val result = try {
                val url = URL("${AppPrefs.getBaseUrl(context)}/api/analyze")
                val connection = (url.openConnection() as HttpURLConnection).apply {
                    requestMethod = "POST"
                    connectTimeout = 2500
                    readTimeout = 3000
                    doOutput = true
                    setRequestProperty("Content-Type", "application/json")
                    setRequestProperty("Accept", "application/json")
                }

                val body = JSONObject().put("text", text).toString()
                connection.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }

                if (connection.responseCode !in 200..299) {
                    connection.disconnect()
                    null
                } else {
                    val response = connection.inputStream.bufferedReader().use { it.readText() }
                    connection.disconnect()
                    val json = JSONObject(response)
                    val indicators = mutableListOf<String>()
                    val arr = json.optJSONArray("indicators")
                    if (arr != null) {
                        for (i in 0 until arr.length()) {
                            val item = arr.opt(i)
                            indicators.add(
                                if (item is JSONObject) {
                                    item.optString("description",
                                        item.optString("name", item.toString()))
                                } else item.toString()
                            )
                        }
                    }

                    ThreatResult(
                        risk = json.optString("risk_level",
                            json.optString("risk", "LOW")).uppercase(),
                        score = json.optInt("risk_score",
                            json.optInt("score", 0)),
                        category = json.optString("category", "Suspicious content"),
                        indicators = indicators
                    )
                }
            } catch (e: Exception) {
                Log.e("CyberShieldApi", "API request failed", e)
                null
            }

            callback(result)
        }
    }
}
