package com.cybershield.sensor

import android.content.Context

object AppPrefs {
    private const val PREFS = "cybershield"
    private const val BASE_URL = "base_url"

    fun getBaseUrl(context: Context): String {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getString(BASE_URL, "http://43.204.97.141:8000")!!
            .trimEnd('/')
    }

    fun setBaseUrl(context: Context, value: String) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
            .putString(BASE_URL, value.trim().trimEnd('/'))
            .apply()
    }
}
