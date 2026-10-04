package org.quantum33.autonomousagent

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.core.content.FileProvider
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import org.json.JSONObject

object AppUpdater {
    private const val RELEASE_API =
        "https://api.github.com/repos/quantumcomputing43/quantum33-autonomous-intelligence/releases/latest"

    fun checkAndOffer(activity: Activity, onStatus: (String) -> Unit) {
        Thread {
            try {
                val connection = URL(RELEASE_API).openConnection() as HttpURLConnection
                connection.connectTimeout = 8000
                connection.readTimeout = 8000
                connection.setRequestProperty("Accept", "application/vnd.github+json")
                val json = connection.inputStream.bufferedReader().use { it.readText() }
                connection.disconnect()

                val release = JSONObject(json)
                val tag = release.optString("tag_name", "")
                val current = activity.packageManager.getPackageInfo(
                    activity.packageName, 0
                ).versionName ?: "0.0.0"
                if (!isNewer(tag.removePrefix("v"), current.removePrefix("v"))) {
                    activity.runOnUiThread { onStatus("Update check: already up to date.") }
                    return@Thread
                }

                val assets = release.optJSONArray("assets") ?: return@Thread
                var apkUrl: String? = null
                for (i in 0 until assets.length()) {
                    val asset = assets.getJSONObject(i)
                    if (asset.optString("name").endsWith(".apk")) {
                        apkUrl = asset.optString("browser_download_url")
                        break
                    }
                }
                if (apkUrl.isNullOrBlank()) {
                    activity.runOnUiThread { onStatus("Update available, but APK asset is missing.") }
                    return@Thread
                }

                val finalUrl = apkUrl
                activity.runOnUiThread {
                    onStatus("Update available: $tag")
                    offerInstall(activity, finalUrl, tag)
                }
            } catch (error: Exception) {
                activity.runOnUiThread { onStatus("Update check unavailable: " + error.javaClass.simpleName) }
            }
        }.start()
    }

    private fun offerInstall(activity: Activity, apkUrl: String, tag: String) {
        Thread {
            try {
                val file = File(activity.cacheDir, "anonymous-simulation-matrix-$tag.apk")
                val connection = URL(apkUrl).openConnection() as HttpURLConnection
                connection.connectTimeout = 15000
                connection.readTimeout = 30000
                connection.inputStream.use { input ->
                    file.outputStream().use { output -> input.copyTo(output) }
                }
                connection.disconnect()

                val uri = FileProvider.getUriForFile(
                    activity,
                    "${activity.packageName}.fileprovider",
                    file
                )
                activity.runOnUiThread {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O &&
                        !activity.packageManager.canRequestPackageInstalls()) {
                        val settings = Intent(
                            Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                            Uri.parse("package:${activity.packageName}")
                        )
                        activity.startActivity(settings)
                        return@runOnUiThread
                    }
                    val intent = Intent(Intent.ACTION_VIEW).apply {
                        setDataAndType(uri, "application/vnd.android.package-archive")
                        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                    }
                    activity.startActivity(intent)
                }
            } catch (_: Exception) {
                activity.runOnUiThread { onStatusSafe(activity, "Update download/install could not start.") }
            }
        }.start()
    }

    private fun onStatusSafe(activity: Activity, message: String) {}

    private fun isNewer(remote: String, current: String): Boolean {
        fun parts(v: String) = v.split(".").map { it.toIntOrNull() ?: 0 }
        val a = parts(remote)
        val b = parts(current)
        for (i in 0 until maxOf(a.size, b.size)) {
            val x = a.getOrElse(i) { 0 }
            val y = b.getOrElse(i) { 0 }
            if (x != y) return x > y
        }
        return false
    }
}
