package com.cybershield.sensor

data class ThreatResult(
    val risk: String,
    val score: Int,
    val category: String,
    val indicators: List<String> = emptyList()
)
